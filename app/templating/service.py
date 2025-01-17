import os
import uuid
from locale import format_string
from urllib.parse import urlencode

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def render(name: str, req: Request, cx: dict | None = None, **kwargs):

    cx = cx or {}
    cx["uuid"] = uuid.uuid4().hex
    cx["format"] = lambda num: format_string("%d", num, grouping=True, monetary=True)
    cx["zip"] = zip
    cx["path"] = req.url.path
    cx["query"] = req.query_params
    cx |= os.environ
    cx["urlencode"] = urlencode

    return templates.TemplateResponse(req, name, cx, **kwargs)
