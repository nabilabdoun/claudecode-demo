import os


def login(username, password):
    expected_username = os.getenv("APP_USERNAME", "admin")
    expected_password = os.getenv("APP_PASSWORD", "")
    if username == expected_username and password == expected_password:
        return "Login successful"
    return "Login failed"