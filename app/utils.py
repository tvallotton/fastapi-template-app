from contextlib import AsyncExitStack, asynccontextmanager
from inspect import isclass
from typing import Annotated, get_origin

from fastapi import Depends, FastAPI, Form, Path, Query, Response
from pydantic import BaseModel, Field


def redirect(path: str, status=200):
    return Response(status_code=status, headers={"Hx-Location": path})


def create_annotated_decorator(annotation):
    def decorator(*args, **kwargs):
        def annotate[T](item: T) -> T:
            return Annotated[item, annotation(*args, **kwargs)]  # type: ignore

        return annotate

    return decorator


dependency = create_annotated_decorator(Depends)
query = create_annotated_decorator(Query)
form = create_annotated_decorator(Form)
path = create_annotated_decorator(Path)


class Resolver(BaseModel):

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


def app_lifespan(lifespans: list):

    @asynccontextmanager
    async def _lifespan_manager(app: FastAPI):
        exit_stack = AsyncExitStack()
        async with exit_stack:
            for lifespan in lifespans:

                await exit_stack.enter_async_context(lifespan(app))
            yield

    return _lifespan_manager
