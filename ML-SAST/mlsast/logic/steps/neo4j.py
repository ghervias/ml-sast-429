from os import mkdir
from os.path import exists
from pathlib import Path
import re
from shutil import copy, copytree, rmtree
from sys import exit

from docker import from_env
from docker.errors import (
    APIError,
    ContainerError,
    ImageNotFound,
    NotFound
)

from mlsast.logic.project import Project
from mlsast.logic.steps.basestep import requires_steps, step
from mlsast.logic.steps.databasestep import DatabaseStep
from mlsast.util.logmessages import Info, Crit
from mlsast.util.helpers import http_download

_DOCKER_CONTAINER = "mlsast-neo4j"
_NEO4J_TAG = "neo4j:4.4.8"

_GDS_URL = "https://graphdatascience.ninja/neo4j-graph-data-science-2.1.13.zip"
_GDS_HASH = "789fd25fc8daaf10a9b00b0087d5c048eca251e1bbd7436f463f8f50ec811772"

_APOC_URL = "https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/" \
    + "download/4.4.0.1/apoc-4.4.0.1-all.jar"
_APOC_HASH = "dfedccd32f924d7be29d219554ad075b4377558a0a1af22d5a67f9e511d57953"

class neo4j(DatabaseStep):
    """A database step wrapping the neo4j graph database service.

    Args:
        DatabaseStep (DatabaseStep): The base class.
    """

    @requires_steps("svf")
    def __init__(self, project: Project) -> None:
        """This class handles everything to get neo4j up and running.

        Args:
            project (Project): The current project
        """
        super().__init__(project)

        self.query = project.config.find("neo4j.query")
        self._client = from_env()

    def _get_image(self):
        """Prepares the docker containe for neo4j. If the container cannot be
        found in the local repository it must be pulled from the official repo.

        Returns:
            Image: The docker image for Neo4j.
        """

        image = None

        try:
            image = self._client.images.get(_NEO4J_TAG)
        except ImageNotFound as e:
            self._logger.info(Info.IMAGE_NOT_FOUND, e)
            image = self._client.images.pull(_NEO4J_TAG)
        except APIError as e:
            self._logger.critical(Crit.DOCKER_ERROR, e)
            exit(1)

        return image

    def _setup_neo_dir(self):
        neo_path = self.project.project_root / "neo4j"
        docker_root = self.project.module_root / "docker"
        dirs = {}

        if exists(neo_path) and self.project.config.find("neo4j.delete",
                msg=Crit.DEL_NOT_SET, abort=False, level="INFO"):
            rmtree(neo_path)

        if not exists(neo_path):
            mkdir(neo_path)

        if not exists(docker_root / "neo4j"):
            mkdir(docker_root / "neo4j")

        dirs.update({neo_path / "import": {
            "bind": "/var/lib/neo4j/import",
            "mode": "rw"}})
        if not exists(neo_path / "import"):

            # Create symlink from extracted csv files to import folder.
            src = self.project.project_root / "svf"
            dst = neo_path / "import"
            copytree(src, dst)

        dirs.update({neo_path / "export": {
            "bind": "/var/lib/neo4j/export",
            "mode": "rw"}})
        if not exists(neo_path / "export"):

            # Nothing to be done, but create the directory.
            mkdir(neo_path / "export")

        dirs.update({neo_path / "conf": {
            "bind": "/var/lib/neo4j/conf",
            "mode": "rw"}})
        if not exists(neo_path / "conf"):

            # Make directory.
            mkdir(neo_path / "conf")

            # Copy conf file.
            src = self.project.module_root / Path("docker/neo4j/neo4j.conf")
            dst = neo_path / "conf"
            copy(src, dst)

        dirs.update({self.project.project_root / "logs": {
            "bind": "/var/lib/neo4j/logs",
            "mode": "rw"}})
        if not exists(self.project.project_root / "logs"):

            # Nothing to be done, but create the directory.
            mkdir(neo_path / "logs")

        dirs.update({neo_path / "plugins": {
            "bind": "/var/lib/neo4j/plugins",
            "mode": "rw"}})
        if not exists(neo_path / "plugins"):

            # Make directroy.
            mkdir(neo_path / "plugins")

            # Download plugins
            http_download(_GDS_URL, neo_path / "plugins", sha256_hash=_GDS_HASH)
            http_download(_APOC_URL, neo_path / "plugins",
                          sha256_hash=_APOC_HASH)

            # Copy MLSAST plugin.
            src = self.project.module_root / Path("docker/neo4j/" \
                + "mlsast-procedures-0.1.jar")
            dst = neo_path / "plugins"
            copy(src, dst)

        dirs.update({neo_path / "scripts": {
            "bind": "/var/lib/neo4j/scripts",
            "mode": "rw"}})
        if not exists(neo_path / "scripts"):

            # Make directory.
            mkdir(neo_path / "scripts")

            # Copy MLSAST plugin.
            src = self.project.module_root / Path("docker/neo4j/" \
                + "export.sh")
            dst = neo_path / Path("scripts/export.sh")
            copy(src, dst)

        return dirs

    def _prepare_query(self):
        query = self.project.config.find("neo4j.query")
        query = re.sub(r"([\"\'\\])", r"\\\1", query)

        prepare = self.project.config.find("neo4j.prepare", abort=Warning,
            level="WARN")

        query = f"{prepare}\nCALL apoc.export.json.query(\"{query}\"," \
            + "\"/var/lib/neo4j/export/query_results.json\");"

        query_path = self.project.project_root / Path("neo4j/scripts")
        with open(query_path / "query.cypher", "w") as f:
            f.writelines(query)

    def _get_env(self):
        env = {"QUERY_FILE": "/var/lib/neo4j/scripts/query.cypher"}

        mem_cfg = self.project.config.find("neo4j.memory", level="INFO",
                abort=False)

        if mem_cfg is None:
            self._logger.info(Info.MEMCFG_NOT_SET)
        elif isinstance(mem_cfg, str) and mem_cfg == "auto":
            env.update({"MEM_CFG": "auto"})
        elif isinstance(mem_cfg, dict):
            env.update({"MEM_CFG": "manual"})
            for k, v in mem_cfg.items():
                if k == "dbms.memory.heap.initial_size":
                    env.update({"HEAP_INITIAL": v})
                if k == "dbms.memory.heap.max_size":
                    env.update({"HEAP_MAX": v})
                if k == "dbms.memory.pagecache.size":
                    env.update({"PAGECACHE": v})
                if k == "dbms.memory.off_heap.max_size":
                    env.update({"OFF_HEAP_MAX": v})
        else:
            self._logger.critical(Crit.CONF_MALFORMED, mem_cfg)

        return env

    @step
    def run(self):
        container = None
        try:
            container = self._client.containers.get(_DOCKER_CONTAINER)
        except NotFound:
            self._logger.info(Info.CREATE_CONTAINER, _DOCKER_CONTAINER)

        if container:
            self._logger.info(Info.EXISTING_CONTAINER, _DOCKER_CONTAINER)

            if not self.project.config.find(
                    "neo4j.delete", msg=Crit.DEL_NOT_SET % _DOCKER_CONTAINER):
                self._logger.critical(Crit.DEL_SET_FALSE, _DOCKER_CONTAINER)

            else:
                container = self._client.containers.get(_DOCKER_CONTAINER)
                container.remove(force=True)

        image = self._get_image()
        vol = self._setup_neo_dir()
        self._prepare_query()
        env = self._get_env()

        try:
            output = self._client.containers.run(
                image,
                ["/var/lib/neo4j/scripts/export.sh"],
                name=_DOCKER_CONTAINER,
                remove=True,
                stdout=True,
                stderr=True,
                volumes=vol,
                environment=env,
                entrypoint="/bin/bash"
            )

            for line in str(output).split("\\n"):
                self._logger.info(line)

        except ContainerError as e:
            self._logger.critical(Crit.DOCKER_ERROR, e)
            exit(1)

    def __str__(self) -> str:
        return type(self).__name__
