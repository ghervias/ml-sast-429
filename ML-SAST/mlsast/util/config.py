import logging
from os import environ
from sys import exit
from yaml import safe_load


from mlsast.util.logmessages import Crit

class SafeList(list):
    """ A child class of list that does not raise an exception when it is accessed at an out of
    range index, but instead silently returns None. Furthermore, if an attempt is made to retrieve
    a class attribute that is not present, instead of an AttributeError being raised, this
    implementation returns None.
    """

    def __getattr__(self, attr):
        return self.__dict__.get(attr)

    def __getitem__(self, attr):
        return self.get(attr)

    def make_safe(self) -> None:
        """ Tries to recursively create SafeLists of all nested lists present in this instance. The
        recursion anchors at any non-list or -dict attribute including other Iterables like sets
        for instance. Something to be aware of.
        """

        for key, val in self.__dict__.items():
            if isinstance(val, dict):
                self.__dict__[key] = SafeDict(val)
                self.__dict__[key].make_safe()

            if isinstance(val, list):
                self.__dict__[key] = SafeList(val)
                self.__dict__[key].make_safe()

            val.make_safe()

class SafeDict(dict):
    """ A child of the dict class that does not raise an exception when a key is passed that is not
    present, but instead silently returns None. Furthermore, if an attempt is made to retrieve
    a class attribue that is not present, instead of an AttributeError being raised, this
    implementation, again, merely returns None.
    """

    def __getattr__(self, attr):
        return self.__dict__.get(attr)

    def __getitem__(self, attr):
        return self.get(attr)

    def make_safe(self):
        """ Tries to recursively create SafeDicts of all nested lists present in this instance. The
        recursion anchors at any non-list or -dict attribute including other Iterables like sets
        for instance. Something to be aware of.
        """
        for key, val in self.__dict__.items():
            if isinstance(val, dict):
                self.__dict__[key] = SafeDict(val)
                self.__dict__[key].make_safe()

            if isinstance(val, list):
                self.__dict__[key] = SafeList(val)
                self.__dict__[key].make_safe()


class Config(SafeDict):
    """ Configuration class that contains the applications global configuration parameters.

    """

    def __init__(self, path: str):

        """ Class constructor for the Config class that reads the application's configuration from
            a yaml file at the specified path. If any of the keys defined in this file are also
            passed to the process as environment variables, the latter override the values in the
            yaml file.

        Args:
            path (str): Path to the configuration file in YAML format.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            YAMLError: If the file cannot be parsed.
        """

        self._logger = logging.getLogger(__name__)
        self.path = path

        with open(path, "r") as yaml:
            config = safe_load(yaml)
            self.update(config)

            # Fill step pipeline with entries from config
            self.pipeline = [k for k in config.keys() if k != "general"]

            for key in config.keys():
                if key in environ:
                    self[key] = environ[key]

            self.__dict__.update(self)
            self.make_safe()

    def find(self, path: str, msg=Crit.CONF_INCOMPLETE, level="CRITICAL", abort=True) -> object:
        """ The preferred way of retrieving config values, as this method defines a safe and
        consistent way of handling missing parameters. The find method uses strings that specifiy
        the path under which to find the respective configuration values. Paths are separated by
        periods, e.g.: "root_directive.some.key".

        If the path cannot be found the message passed by the `msg`-parameter is logged according to
        the level passed by `level` and the program terminated if `abort` is set to True (default).

        Args:
            path (str): The path to the configuration value to be retrieved.
            msg (str): The messaged to be logged in case the key is not present.
            level (str): The log-level that is to be used.
            abort (bool): Terminate the program immediately if the path leads to an undefined value.

        Returns:
            obj: Returns the value present at the specified path. Likely a list, dict or string.
        """

        # May raise an AttributeError
        level = getattr(logging, level)
        keys = path.split(".")

        try:
            item = self
            for key in keys:
                item = item.get(key)

        # The path is invalid and it's end is unreachable
        except (AttributeError, IndexError, KeyError) as e:
            self._logger.log(level, msg, path, e)

            if abort:
                exit(1)

        if not item:
            self._logger.log(level, msg, path)

            if abort:
                exit(1)

        return item
