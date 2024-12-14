from src.test_common import HTMLClient


def test_signup(client: HTMLClient, email="signup@test.email"):
    client.goto("/user/signup")
    client.write("input", email)
    client.click("button[type='submit']")
    client.read_email(email)
    client.click("#verify-link")


def test_login(client: HTMLClient, email="login@email.test"):
    test_signup(client, email)
    client.goto("/user/login")
    client.write("input", email)
    client.click("button[type='submit']")
    client.read_email(email)
    client.click("#verify-link")
