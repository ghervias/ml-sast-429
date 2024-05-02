from pathlib import Path
from sys import exit

from docker import from_env
from docker.errors import (
    APIError,
    BuildError,
    ContainerError,
    ImageNotFound,
    NotFound
)

from mlsast.logic import Project
from mlsast.util.logmessages import Crit, Info
from .basestep import step
from .graphstep import GraphStep

_DOCKER_TAG = "mlsast-svf:latest"
_DOCKER_CONTAINER = "mlsast-svf"
_SVF_COMMAND = "svf-mlsast"


class svf(GraphStep):
    def __init__(self, project: Project) -> None:
        """This class handles everything to get the SVF docker container  up and
        running.

        Args:
            project (Project): The current project
        """
        super().__init__(project)

        self.code_path = project.code_path
        self._client = from_env()

    def _build_image(self):
        """Builds the SVF image. If the image is not already present in the
        repository of the local machine, the corresponding git repository is
        cloned and the image built. Otherwise the already existing image will be
        used.

        Returns:
            Image: The SVF image.
        """
        try:
            docker_dir = self.project.module_root / "docker"

            self._logger.info(Info.BUILD_SVF)
            # Build the image
            res = self._client.images.build(
                path=str(docker_dir / "svf"),
                tag=_DOCKER_TAG,
                quiet=False
            )
            self._logger.info(Info.BUILD_SVF_FINISHED)
            self._logger.debug(res[1])


        except APIError as e:
            self._logger.critical(Crit.DOCKER_ERROR, e)
            exit(1)
        except BuildError as e:
            self._logger.critical(Crit.DOCKER_ERROR, e)
            exit(1)

        return res[0]

    def _get_command(self):
        """Builds the svf command from the parameters passed in the projects
        config.yaml file.

        Args:
            code_path (Path): The path to the source code from within the docker
            (i.e., relative to the volume mount) , e.g., /project/code.

        Returns:
            str: The command that may be evaluated from within a bash.
        """
        command = _SVF_COMMAND
        conf = self.project.config

        # Check if versioning threads are set.
        threads = conf.find("svf.options.versioning_threads", abort=False,
                            level="DEBUG")
        if threads:
            command += f" -versioning-threads={int(threads)}"

        # Check if PTS clustering is enabled.
        cluster = conf.find("svf.options.enable_clustering", abort=False,
                            level="DEBUG")
        if cluster:
            command += " -cluster-fs"

            # If PTS clustering is enabled a method must be set.
            method = conf.find("svf.options.cluster_method")
            if method in ["single", "complete", "average", "best"]:
                command += f" -cluster-method={method}"
            else:
                self._logger.critical(Crit.METHOD_UNKNOWN)

        # Check if the precise VFG based PTA should be used.
        precise = conf.find("svf.options.precise_analysis", abort=False,
                            level="DEBUG")
        if precise:
            command += " -precise-analysis"

        for graph in conf.find("svf.graphs"):
            if graph in ["icfg", "ptacg", "svfg", "tldep"]:
                command += f" -build-{graph}"

        return command

    def _get_image(self):
        """Prepares the docker container for svf. If the container cannot be
        found in the local repository it must be cloned from a git repository
        and build.

        Returns:
            Image: The docker image for SVF.
        """

        image = None

        try:
            image = self._client.images.get(_DOCKER_TAG)
        except ImageNotFound as e:
            self._logger.info(Info.IMAGE_NOT_FOUND, e)
            image = self._build_image()
        except APIError as e:
            self._logger.critical(Crit.DOCKER_ERROR, e)
            exit(1)

        return image

    def _generate_graphs(self):
        """Executes steps necessary to generate the graphs selected through the
        config.yaml of the respective project. This mostly comprises setting up
        and running the docker container for SVF by:

        1. Mounting the project folder at /project
        2. Setting the BINARY environment variable to the name of the binary
           after compilation.
        3. Setting the BUILD_ROOT envrionment variable to the root of the source
           code to be built.
        4. Setting the SVF_COMMAND environment variable by calling the
           _get_command() method to the SVF command that is issued to generate
           the graphs.
        5. Running the container.

        Everything else is handled by the entrypoint of the container.
        """
        container = None
        try:
            container = self._client.containers.get(_DOCKER_CONTAINER)
        except NotFound:
            self._logger.info(Info.CREATE_CONTAINER, _DOCKER_CONTAINER)

        if container:
            self._logger.info(Info.EXISTING_CONTAINER, _DOCKER_CONTAINER)

            if not self.project.config.find(
                    "svf.delete", msg=Crit.DEL_NOT_SET % _DOCKER_CONTAINER):
                self._logger.critical(Crit.DEL_SET_FALSE, _DOCKER_CONTAINER)

            else:
                container = self._client.containers.get(_DOCKER_CONTAINER)
                container.remove(force=True)

        image = self._get_image()

        # We only need to mount the project folder into the container. This is
        # done here using the volumes kwarg as the mounts kwarg always resultet
        # in exceptions being thrown somewhere deep within the docker package.
        # Appears to be a bug on their side.
        vol = {self.project.project_root: {"bind": "/project", "mode": "rw"}}

        # Get the environment variables, i.e., the build root within the project
        # and the command for the graph generation.
        code_path = Path("/project") / self.project.code_path
        env = {
            "BINARY": str(self.project.config.find("svf.binary")),
            "BUILD_ROOT": str(code_path),
            "SVF_COMMAND": str(self._get_command())
        }

        try:
            output = self._client.containers.run(
                image,
                [],
                name=_DOCKER_CONTAINER,
                remove=True,
                stdout=True,
                stderr=True,
                volumes=vol,
                environment=env
            )
        except ContainerError as e:
            self._logger.critical(Crit.SVF_FAILUE, e)
            exit(1)

        for line in str(output).split("\\n"):
            self._logger.info(line)

    @step
    def run(self):
        self._generate_graphs()

    def __str__(self) -> str:
        return type(self).__name__
