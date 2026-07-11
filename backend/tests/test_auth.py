async def test_signup_login_refresh_me(client):
    res = await client.post(
        "/auth/signup",
        json={"email": "a@b.com", "password": "password123", "nickname": "abc"},
    )
    assert res.status_code == 201

    # duplicate email
    res = await client.post(
        "/auth/signup",
        json={"email": "a@b.com", "password": "password123", "nickname": "abc"},
    )
    assert res.status_code == 409

    # short password rejected
    res = await client.post(
        "/auth/signup",
        json={"email": "c@d.com", "password": "short", "nickname": "abc"},
    )
    assert res.status_code == 422

    # wrong password
    res = await client.post(
        "/auth/login", json={"email": "a@b.com", "password": "wrongpass1"}
    )
    assert res.status_code == 401

    res = await client.post(
        "/auth/login", json={"email": "a@b.com", "password": "password123"}
    )
    assert res.status_code == 200
    access = res.json()["access_token"]
    assert "refresh_token" in res.cookies

    # refresh via cookie
    res = await client.post("/auth/refresh")
    assert res.status_code == 200
    assert res.json()["access_token"]

    # /users/me with access token
    res = await client.get("/users/me", headers={"Authorization": f"Bearer {access}"})
    assert res.status_code == 200
    assert res.json()["email"] == "a@b.com"

    # no token -> 401
    res = await client.get("/users/me")
    assert res.status_code == 401
