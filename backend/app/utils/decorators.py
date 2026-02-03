from collections.abc import Callable
import functools
from typing import Any


def transactional(func: Callable):
    """
    Decorator to wrap an asynchronous method in a database transaction.

    This decorator ensures that the decorated method is executed within a
    transactional context using SQLAlchemy's `session.begin()`.

    Behavior:
    - Automatically issues a COMMIT if the method completes successfully.
    - Automatically issues a ROLLBACK if any exception occurs during execution.
    - Requires the host class to have an initialized `self._session` attribute
      (AsyncSession).

    Args:
        func (Callable): The asynchronous service method to be decorated.

    Raises:
        AttributeError: If the instance of the class does not have a `_session` attribute.

    Returns:
        Callable: The wrapped asynchronous function.
    """

    @functools.wraps(func)
    async def wrapper(self, *args: Any, **kwargs: Any):
        if not hasattr(self, '_session'):
            raise AttributeError(f'Class {self.__class__.__name__} must have self._session')

        # Use begin_nested() for savepoint if already in transaction, otherwise begin()
        if self._session.in_transaction():
            async with self._session.begin_nested():
                return await func(self, *args, **kwargs)
        else:
            async with self._session.begin():
                return await func(self, *args, **kwargs)

    return wrapper
