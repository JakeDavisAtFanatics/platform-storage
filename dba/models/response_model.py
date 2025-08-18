from typing import Generic, Optional, TypeVar, Union

from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    successful: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[Union[Exception, str]] = None

    @property
    def has_error(self) -> bool:
        return not self.successful

    @classmethod
    def success(cls, data: Optional[T] = None) -> "Response[T]":
        return cls(
            successful=True,
            data=data,
        )

    @classmethod
    def failure(
        cls,
        message: Optional[str] = None,
        error: Optional[Exception] = None,
    ) -> "Response[T]":
        return cls(
            successful=False,
            message=message,
            error=error,
        )

    model_config = {"arbitrary_types_allowed": True}
