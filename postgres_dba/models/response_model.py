from typing import Generic, Optional, TypeVar, Union

from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    successful: bool
    request: Optional[str] = None
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[Union[Exception, str]] = None

    @property
    def has_error(self) -> bool:
        return not self.successful

    @classmethod
    def success(cls, data: Optional[T] = None, request: Optional[str] = None) -> "Response[T]":
        return cls(
            successful=True,
            data=data,
            request=request,
        )

    @classmethod
    def failure(
        cls,
        message: Optional[str] = None,
        request: Optional[str] = None,
        error: Optional[Exception] = None,
    ) -> "Response[T]":
        return cls(
            successful=False,
            message=message,
            request=request,
            error=error,
        )

    model_config = {"arbitrary_types_allowed": True}
