import logging

from functools import wraps

from mlsast.logic.project import Project
from mlsast.util.logmessages import Info


def step(func):
    """Decorator for the run function of a step. Appends the step run to the
    project objects list of conducted steps and logs the run of this step.

    Args:
        func (callable): The run() function that executes a steps logic.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Disable pylint warning protected-access as this decorator is a
        # justified exception.
        args[0].get_logger().info(Info.RUNNING_STEP % str(args[0]))

        # Append step after being run
        args[0].project.steps.append(str(args[0]).lower())

        return func(*args, **kwargs)

    return wrapper


def requires_steps(*steps):
    """Decorator that validates that all steps passed have been executed before.
    Used to annotate the constructors of the steps that they require to be
    executed beforehand.

    Args:
        steps (str): A vararg of strings with the class names of the steps that
        are required for this step to be executed.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for step in steps:
                args[1].has_passed(step, fail=True)

            return func(*args, **kwargs)

        return wrapper

    return decorator

class BaseStep():
    """The Base step class that all other steps must inherit from. A step is a
    single execution unit within a given pipeline. Each step must contain a
    run() method that must be annotated with the @step decorator for it to be
    tracked by the project object passed to the constructor. The Constructor
    itself may be decorated with the @requires_steps decorator that ensures all
    steps passed have been executed prior to this one. If not, then the process
    will halt immediately with an execption.
    """

    def __init__(self, project: Project) -> None:
        """The constructor of the BaseStep class. The project object passed is
        used to log the steps executed, when the run() method is called.

        Args:
            project (Project): The project currently being analyzed.
        """
        self._logger = logging.getLogger(__name__)
        self.project = project

        self.success = False

    @step
    def run(self):
        pass

    def __str__(self) -> str:
        return type(self).__name__

    def get_logger(self):
        return self._logger
