from app.test_common import HTMLClient
from app.user.factory import UserFactory


def test_signup(client: HTMLClient):
    email = "signup@test.email"
    client.goto("/user/signup")
    client.write("input", email)
    client.click("button[type='submit']")
    client.read_email(email)
    client.click("#verify-link")


async def test_login(client: HTMLClient, injector):
    email = "login@test.email"
    await injector.get(UserFactory).create(email=email)
    client.goto("/user/login")
    client.write("input", email)
    client.click("button[type='submit']")
    client.read_email(email)
    client.click("#verify-link")
