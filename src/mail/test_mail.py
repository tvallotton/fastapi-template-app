import os

import httpx

from src import mail

client = httpx.AsyncClient()

MAILPIT_URL = os.environ["MAILPIT_URL"]


async def test_send_email():
    dest = "email.service@test"
    await mail.service.send("test", dest=dest, subject="greetings", context={})

    response = await client.get(f"{MAILPIT_URL}/search", params={"query": dest})

    id = response.json()["messages"][0]["ID"]

    response = await client.get(f"{MAILPIT_URL}/message/{id}")

    assert "hello world" in response.json()["HTML"]
