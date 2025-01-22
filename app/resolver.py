from inspect import isclass
from typing import Annotated, get_origin

from pydantic import BaseModel, Field


class Resolver(BaseModel):
    """
    A class to perform dependency resolution outside the context of a fastapi request.
    """

    overrides: dict = Field(default_factory=dict)
    cached: dict = Field(default_factory=dict)

    def get[T](self, dependency: type[T]) -> T:
        if self.cached.get(dependency) is not None:
            return self.cached[dependency]

        if self.overrides.get(dependency) is not None:
            return self.get(self.overrides[dependency])

        if get_origin(dependency) == Annotated:
            return self.get_annotated(dependency)

        if callable(dependency):
            return self.get_callable(dependency)

    def get_annotated(self, dependency):
        depends = dependency.__metadata__[0]

        if depends.dependency:
            return self.get(depends.dependency)
        else:
            return self.get(dependency.__origin__)

    def get_callable(self, dependency):

        if hasattr(dependency, "__annotations__"):
            annotations = dependency.__annotations__

        if isclass(dependency) and not issubclass(dependency, BaseModel):
            annotations = dependency.__init__.__annotations__

        kwargs = {arg: self.get(_type) for arg, _type in annotations.items()}  # type: ignore

        self.cached[dependency] = dependency(**kwargs)
        return self.cached[dependency]
