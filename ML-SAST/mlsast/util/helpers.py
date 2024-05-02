from hashlib import sha256
from os.path import dirname, exists, join
from pathlib import Path
from re import split
from sys import modules
from warnings import catch_warnings, filterwarnings
from zipfile import ZipFile

from docker import from_env
from docker.client import DockerClient
from requests import get


class HashError(Exception):
    """Exception to be raised when the verification of a file against a given
    hash fails.
    """


def get_docker_client() -> DockerClient:
    """ Wrapper function for retrieval of the docker client that would otherwise
    raise a deprecation warning (not our fault).  """

    with catch_warnings():
        filterwarnings("ignore", message="distutils Version classes are " \
                + "deprecated.*",
            category=DeprecationWarning)

        return from_env()


def get_config_path(prefer_home=True) -> str:
    """ Helper that retrieves the path to the config-file in yaml format. If the
        prefer_home is set, the configuration found in the user's
        `$HOME/mlsast-server` directory is preffered over the package's default
        config.

    Args:
        prefer_home (bool): Set to true by default. When set to false, the
        function returns the default configuration-file, found in the install
        directory of the `mlsast` package.

    Returns:
        str: The String that reflects the path to where the config-file should
        be retrieved from.
    """

    path = join(Path.home(), "mlsast-server", "config.yaml")

    if not prefer_home or not exists(path):
        path = join(dirname(modules[__name__].__file__), "../", "config.yaml")

    return path


def verify_file(file_path: str, sha256_hash: str, block_size=65536):
    file_hash = sha256()

    with open(file_path, "rb") as f:
        buf = f.read(block_size)

        while len(buf) > 0:
            file_hash.update(buf)
            buf = f.read(block_size)

    return file_hash.hexdigest() == sha256_hash


def http_download(url: str, dst: str, sha256_hash=None):
    data = get(url, verify=True)
    filename = url.split("/")[-1]

    with open(Path(dst) / filename, "wb") as f:
        f.write(data.content)

    if sha256_hash:
        if not verify_file(Path(dst) / filename, sha256_hash):
            raise HashError(sha256_hash)


def src_loc_from_dbg_str(dbg_str):
    """ Helper that finds a file location given as a debug string in
    LLVM format.

    Args:
        dbg_str: The LLVM debug location
    Returns:
        str: The location (line) and the file name.
    """

    loc = {'line': 0, 'file': False}
    match = split(r'\s*ln:\s*(\d+).*fl:.', dbg_str)
    if match and len(match) == 3:
        loc['line'] = int(match[1])
        loc['file'] = match[2]
    else:
        match = split(r'\s*in line:\s*(\d+).*file:.', dbg_str)
        if match and len(match) == 3:
            loc['line'] = int(match[1])
            loc['file'] = match[2]
    return loc


def retrieve_source_location(dbg_str, root_dir, delta=4) -> str:
    """ Helper that retrieves the source code for a given debug location in
    LLVM format.

    Args:
        dbg_str: The LLVM debug location
        root_dir: The root folder of the source code
        delta: A possible delta with lines before and
                after the given location
    Returns:
        str: The code found at the given location with the specified delta.
    """

    code = ''
    location = src_loc_from_dbg_str(dbg_str)
    if location['file']:
        with open(join(root_dir, location['file']), 'r') as file:
            lines = file.readlines()
        count = len(lines)
        if count >= location['line']:
            pos = max(location['line'] - delta - 1, 0)
            end = min(location['line'] + delta, count)
            while pos <= end - 1:
                code += lines[pos]
                pos += 1

    return code

def unzip(file_path: str) -> dict:
    """ Simple helper function that unzips a file provided by it's path. The
    files contained within the zipfile must be text files.

    Args:
        file_path (str): The file path.
    Returns (dict): A dictonary of files by name and content.
    """
    files = {}

    with ZipFile(file_path) as zfile:
        for member in zfile.namelist():
            with zfile.open(member) as unzipped:
                files.update({member: unzipped.read().decode()})

    return files
