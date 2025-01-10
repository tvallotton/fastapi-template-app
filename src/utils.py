from copyreg import constructor
from inspect import isclass
from typing import Annotated, Type, get_origin

from fastapi import Depends, Form, Path, Query, Response
from pydantic import BaseModel, Field


def redirect(path: str, status=200):
    return Response(status_code=status, headers={"Hx-Location": path})


def create_annotated_decorator(annotation):
    def decorator(*args, **kwargs):
        return lambda item: Annotated[item, annotation(*args, **kwargs)]

    return decorator


dependency = create_annotated_decorator(Depends)
query = create_annotated_decorator(Query)
form = create_annotated_decorator(Form)
path = create_annotated_decorator(Path)


class Injector(BaseModel):

    overrides: dict = Field(default_factory=dict)
    cache: dict = Field(default_factory=dict)

    def get(self, dependency):
        if self.cache.get(dependency) is not None:
            return self.cache[dependency]

        if self.overrides.get(dependency) is not None:
            return self.overrides[dependency]

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

        kwargs = {arg: self.get(_type) for arg, _type in annotations.items()}

        self.cache[dependency] = dependency(**kwargs)
        return self.cache[dependency]
