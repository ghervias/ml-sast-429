from os.path import exists, dirname
from pathlib import Path
from sys import exit
import logging

from mlsast.util.config import Config
from mlsast.util.logmessages import Crit

class Project():
    """The project class wraps the project folder passed to the tool through the
    command line argument -p/--project. Each project folder must contain a valid
    conig.yaml, a build.sh and and finally a subdirectory containing the source
    code.
    """

    def __init__(self, path: str, module_root: str) -> None:
        """Project class that wraps the project folder.

        Args:
            path (str): Path to the project directory
            module_root (Path): The path to the module root directory.

        Raises:
            FileNotFoundError: If the the project folder is malformed (lacking files or folders).
            KeyError: If the the source code folder is neither present at its default location or
            the source code folder is not specified in the config.yaml of the project folder.
        """
        self._logger = logging.getLogger(__name__)

        self.module_root = Path(dirname(module_root))
        self.steps = []

        # Set project root
        path = Path(path)
        if not exists(path):
            raise FileNotFoundError(Crit.DIR_NOT_FOUND, path.resolve())

        self.project_root = path

        # Load config file
        config_file = self.project_root / "config.yaml"
        if not exists(config_file):
            raise FileNotFoundError(Crit.DIR_NOT_FOUND, config_file.resolve())

        self.config = Config(config_file.resolve())

        # Get log level
        self.log_level = self.config.find("general.loglevel")

        # Check if source code folder exists at its standard location or if not
        # is specified in the config file.
        conf_code_path = self.config.find("general.source", abort=False)
        default_code_path = self.project_root / "code"
        self.code_path = None

        if conf_code_path:
            if exists(self.project_root / conf_code_path):
                self.code_path = conf_code_path
        else:
            if exists(default_code_path):
                self.code_path = default_code_path

        if not self.code_path:
            if not conf_code_path:
                self._logger.critical(Crit.CONF_INCOMPLETE, "general.source")
                exit(1)

            if not exists(self.project_root / conf_code_path) \
                    or not exists(default_code_path):
                self._logger.critical(
                    Crit.CODE_NOT_FOUND,
                    conf_code_path,
                    default_code_path
                )
                exit(1)

        # Check build.sh script
        build_path = self.project_root / "build.sh"
        if not exists(build_path):
            self._logger.critical(Crit.BUILDSH_NOT_FOUND, build_path)
            exit(1)

        self.build_path = build_path

    def has_passed(self, step: str, fail=False) -> None:
        """Checks whether the anaylsis has passed the provided step and raises
        an exception if fail is set to True.

        Args:
            step (str): String identifiying the step.
            fail (bool): Abort with an exception if the specified step has not
                been executed.

        Raises:
            Exception: Raises an exception if the step has not been executed and
            fail is set to True.
        """

        if step.lower() in self.steps:
            return True
        elif fail:
            self._logger.critical(Crit.STEP_NOT_RUN, step)
            exit(1)

        return False
