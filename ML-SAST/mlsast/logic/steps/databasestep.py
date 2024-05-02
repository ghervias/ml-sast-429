from mlsast.logic.steps.basestep import BaseStep

class DatabaseStep(BaseStep):
    """The DatabaseStep should be used as the base class for all steps in the
    pipeline that wrap some database service.

    Args:
        BaseStep (BaseStep): The base class.
    """

    def __str__(self) -> str:
        return type(self).__name__
