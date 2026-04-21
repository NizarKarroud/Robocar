from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T" , bound=BaseModel)


class SignedPayload(BaseModel , Generic[T]):
    data : T
    signature : str