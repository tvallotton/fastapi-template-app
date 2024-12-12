import os

import httpx
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

MAILPIT_URL = os.environ["MAILPIT_URL"]


class HTMLClient(BaseModel):
    client: TestClient
    doc: BeautifulSoup = BeautifulSoup()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get(self, path, *args, **kwargs):
        print("GET", path, *args, **kwargs)
        resp = self.client.get(path, *args, **kwargs)
        print(resp.status_code)
        return BeautifulSoup(resp.text, features="html.parser")

    def _post(self, path, *args, **kwargs):
        print("POST", path, *args, kwargs)
        resp = self.client.post(path, *args, **kwargs)

        return BeautifulSoup(resp.text, features="html.parser")

    def goto(self, path, *args, **kwargs):
        self.doc = self._get(path, *args, **kwargs)

    def write(self, query: str, text: str):
        "use the query to find an input element and write to it"
        element = self.doc.select_one(query)
        assert element is not None, f"query {query} yielded no results"
        assert element.name in ["input", "textarea"]
        element["value"] = text

    def click(self, query: str):
        """
        use the query to find an element and click it
        """
        element = self.doc.select_one(query)

        assert element is not None

        match element.name:
            case "a":
                self.click_a(element)
            case "button":
                self.click_button(element)
            case _:
                self.click_htmx(element)

    def click_a(self, element):
        self.goto(element["href"])

    def click_button(self, button):

        type = button.get("type", "submit")
        if button.find_parent("form") and type == "submit":
            self.submit_form(button)
        else:
            self.click_htmx(button)

    def submit_form(self, button):
        form = button.find_parent("form")
        assert form is not None

        action = find_action(button) or find_action(form)
        method = find_method(button) or find_method(form)
        data = {
            input.get("name"): input.get("value")
            for input in form.select("input")
            if input.get("name")
        }

        if method == "GET":
            self.doc = self._get(action, params=data)
        elif form.get("hx-ext"):
            self.doc = self._post(action, json=data)
        else:
            self.doc = self._post(action, data=data)

    def click_htmx(self, element):
        if get_attr(element, "hx-trigger") != "click":
            return

        hx_get = get_attr(element, "hx-get")
        hx_post = get_attr(element, "hx-post")

        if hx_get is not None:
            replace = self._get(hx_get)

        elif hx_post is not None:
            replace = self._post(hx_post)
        else:
            raise NotImplemented()

        query = get_attr(element, "hx-target")

        target = element
        if query is not None:
            target = self.doc.select_one(query)
            assert target is not None, f"target error for query {query}"

        target.replace_with(replace)

    def read_email(self, query: str):
        print(search_by_email(query))
        messages = search_by_email(query)["messages"]
        assert messages != [], f"No emails were found for query {query}"

        id = messages[0]["ID"]
        html = httpx.get(f"{MAILPIT_URL}/message/{id}").json()["HTML"]
        self.doc = BeautifulSoup(html, features="html.parser")

    def text(self):
        return self.doc.text()


def search_by_email(query):
    return httpx.get(f"{MAILPIT_URL}/search", params={"query": query}).json()


def delete_by_email(query):
    return httpx.delete(f"{MAILPIT_URL}/search", params={"query": query})


def find_method(element):
    """
    finds the method attribute of a form element
    with support of htmx
    """
    if element.get("hx-post"):
        return "POST"
    elif element.get("hx-get"):
        return "GET"
    elif element.get("hx-put"):
        return "PUT"
    elif element.get("hx-delete"):
        return "DELETE"
    elif element.name == "form":
        return element.get("method") or "GET"


def get_attr(element, attr: str):
    "finds an attribute respecting inheritance"
    while element is not None:
        if element.get(attr):
            return element[attr]
        else:
            element = element.parent


def find_action(form):
    """
    finds the action attribute of a form element
    with support of htmx
    """
    return (
        form.get("action")
        or form.get("hx-post")
        or form.get("hx-get")
        or form.get("hx-put")
        or form.get("hx-delete")
    )
