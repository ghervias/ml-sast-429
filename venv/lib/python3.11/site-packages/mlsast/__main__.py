import logging
from importlib import import_module
from os.path import abspath
from sys import exit, stdout

import mlsast


def main():
    """Main function of the prototype: Initializes the project from the
    directory passed via the -p/--project command line argument and configures
    the logger. Finally the pipeline is read from the config and executed by
    first loading the step modules contained in mlsast.logic.steps and then
    executing the run methods of the steps.

    Returns:
            int: 0 on success, 1 on failure
    """

    # Parse arguments
    args = mlsast.frontend.argparser.parse_args()

    # Set up logger
    logging_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(stream=stdout, level=logging.INFO,
                        format=logging_format)
    logging.captureWarnings(True)
    logger = logging.getLogger()

    # Attempt to load project
    module_root = abspath(__file__)
    project_path = abspath(args.project)
    project = mlsast.logic.Project(project_path, module_root)

    # Configure logger from config file
    level = project.config.find("general.loglevel", abort=False)

    if level and level in logging.__dict__:
        logger.setLevel(level)
        logger.info(mlsast.util.logmessages.Info.LOG_LEVEL, level)

    else:
        logger.warning(mlsast.util.logmessages.Warn.LOG_UNKNOWN_LEVEL, level)

    # Execute pipeline from config by loading the steps accordingly and
    # executing them in order. The program termintes immediately with an
    # exception if the module cannot be found.
    for step_name in project.config.pipeline:
        try:
            step_path = f"mlsast.logic.steps.{step_name}"
            print(step_path)
            module = import_module(step_path)
            step = getattr(module, step_name)(project)

            # Execute step
            step.run()
        except ModuleNotFoundError as error:
            logger.critical(mlsast.util.logmessages.Crit.STEP_IMPORT_FAIL, (step_name, error.msg))

    exit(0)


if __name__ == "__main__":
    main()
