import sys
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self
else:
    Self: Any = None
