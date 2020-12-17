"""
SqlAlchemy and Pydantic models
"""

from typing import List, Optional
from pydantic import BaseModel  # pylint: disable=E0611

from fastapi import (
    File,
    Form,
)


class NeuralNetworkSchema(BaseModel):  # pylint: disable=R0903
    """
    Schema for neural networks
    """

    id: int
    name: str


class FormSchema(BaseModel):  # pylint: disable=R0903
    """
    Schema for form posting
    """

    first_image: Optional[bytes]
    second_image: Optional[bytes]
    server_image_1: Optional[str]
    server_image_2: Optional[str]
    models: List[str]

    @classmethod
    def as_form(
            cls,
            first_image: Optional[bytes] = File(...),
            second_image: Optional[bytes] = File(...),
            server_image_1: Optional[str] = Form(...),
            server_image_2: Optional[str] = Form(...),
            models: List[str] = Form(...)
    ):
        """
        Return form valid model
        """

        return cls(
            first_image=first_image,
            second_image=second_image,
            server_image_1=server_image_1,
            server_image_2=server_image_2,
            models=models
        )
