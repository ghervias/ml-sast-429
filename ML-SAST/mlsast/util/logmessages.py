class Crit:
    """ This class collects all log messages to be printed when a critical condition is reached,
        that the program cannot recover from.

    Examples:
        If the application fails to establish a database connection, the program may be terminated
        immediately. The reason should then be logged, using a message defined in this class.
    """

    PARM_SRC_DIR = "Missing parameter '--source-dir', neither provided as command line argument " \
            "nor config value."

    CONF_NOT_FOUND = "Cannot find configuration file at the specified path:\n%s"
    CONF_MALFORMED = "The Configuration file appears to be malformed and cannot be parsed:\n %s"
    CONF_INCOMPLETE = "Key lookup failed, configuration may be incomplete. Key was:\n %s"
    CONF_NEO_ERROR = "Erroneous Neo4J configuration found, possibly due to malformed url:\n %s"
    CONF_PATH_NABS = "The path provided is not an absolute path! Please consult the manual for " \
            "further information. Path in question:\n%s"

    DEL_NOT_SET = "neo4j.delete option not set in config. Refusing to delete existing container: %s"
    DEL_SET_FALSE = "neo4j.delete option in project config set to false. Refusing to delete " \
        "container: %s"

    CODE_NOT_FOUND = "Could not find project source code at %s or %s!"
    BUILDSH_NOT_FOUND = "Build script (build.sh) not found in expected directory: %s"

    NEO_UNAVAILABLE = "Database unavailable, failed to establish a database connection:\n %s"
    NEO4J_NOT_FOUND = "Neo4J container is not running. Please start container with the provided " \
                      "docker-compose.\n %s"

    SVF_FAILUE = "The SVF container exitet with an error code: %s"
    METHOD_UNKNOWN = "Unkown clustering method for SVF: %s"

    DOCKER_ERROR = "Docker server returned an error:\n %s"
    IMAGE_NOT_FOUND = "Image not found, please pull specified image:\n %s"

    DIR_NOT_CREATED = "The directory could not be created:\n %s"
    DIR_NOT_FOUND = "The directory %s does not exist."

    STEP_NOT_RUN = "Pipeline step %s has not been executed. Aborting!"
    STEP_IMPORT_FAIL = "Failed to import step with name %s, error: %s"

class Err:
    """ This class contains all log messages to be printed when a non-fatal state is reached that
        the program may recover from, but cause the current operation to be aborted.

    Examples:
        If a single query yields no results, a corresponding message stating the issue may be
        defined here and logged as an error. The program may be able to continue the execution,
        however, as other queries could still return with meaningful data.
    """


class Warn:
    """ This class contains warning messages that may need to be logged during execution. These
        messages should be raised on minor errors.

    Examples:
        A default value is assumed, because it's definition is lacking from the configuration file.
    """

    LOG_UNKNOWN_LEVEL = "Encountered unknown log-level in config: %s"
    CONF_MISSING_KEY = "Access to missing configuration value: %s"

    MEMCFG_NOT_SET = "Memory configuration not set. The Neo4j database may be configured to use " \
        "more memory than is available to the machine. Please configure the memory settings " \
        "either manually in the projects config.yaml file or set the 'neo4j.memory' key to the " \
        "value 'auto' for the memory configuration to be determined automatically."


class Info:
    """ All information that relate to significant changes in the execution state of the program.

    Examples:
        When a query returns, the total number of subgraphs yielded may be logged.
    """
    SRC_DIR_CMD = "Using project source path from command line parameter:\n %s"
    SRC_DIR_CFG = "Using project source path from config file parameter:\n %s"

    LOG_LEVEL = "Log-level set to: %s"


    IMAGE_NOT_FOUND = "Could not find docker image in local repository: \n%s"
    BUILD_SVF = "Start building SVF..."
    BUILD_SVF_FINISHED = "Finished building SVF"
    CLONED_SVF_TO = "Cloned SVF repository to: %s"

    RUNNING_STEP = "Running step %s"

    EXISTING_CONTAINER = "Found existing docker container: %s"
    CREATE_CONTAINER = "No existing container found, creating container: %s"

class Debug:
    """ Information that pertains to the overall execution state of the program. Only to be used
        for debugging purposes.

    Examples:
        A docker container is run and the invocation parameters are logged for debugging purposes.
    """

    STA_CON_BUILD = "Executing build command within SVF container."
    STA_CON_NEO4J = "Importing graphs into database."
    STA_GRAPH_BLD = "Begin graph generation process."
