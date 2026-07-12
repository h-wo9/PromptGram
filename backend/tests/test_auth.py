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
    body = res.json()
    access, refresh = body["access_token"], body["refresh_token"]
    assert access and refresh
    assert not res.cookies  # cookie 미사용

    # /users/me with access token
    res = await client.get("/users/me", headers={"Authorization": f"Bearer {access}"})
    assert res.status_code == 200
    assert res.json()["email"] == "a@b.com"

    # no token -> 401
    res = await client.get("/users/me")
    assert res.status_code == 401


async def test_refresh_rotation_and_reuse_rejected(client):
    await client.post(
        "/auth/signup",
        json={"email": "r@r.com", "password": "password123", "nickname": "rot"},
    )
    login = await client.post(
        "/auth/login", json={"email": "r@r.com", "password": "password123"}
    )
    old_refresh = login.json()["refresh_token"]

    # rotation: 새 pair 발급, refresh가 교체됨
    res = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert res.status_code == 200
    new_refresh = res.json()["refresh_token"]
    assert res.json()["access_token"]
    assert new_refresh != old_refresh

    # 이전(회수된) refresh 재사용 -> 401
    res = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert res.status_code == 401

    # 새 refresh는 유효
    res = await client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert res.status_code == 200

    # 무작위 토큰 -> 401
    res = await client.post("/auth/refresh", json={"refresh_token": "garbage-token"})
    assert res.status_code == 401


async def test_logout_revokes_refresh(client):
    await client.post(
        "/auth/signup",
        json={"email": "o@o.com", "password": "password123", "nickname": "out"},
    )
    login = await client.post(
        "/auth/login", json={"email": "o@o.com", "password": "password123"}
    )
    refresh = login.json()["refresh_token"]

    res = await client.post("/auth/logout", json={"refresh_token": refresh})
    assert res.status_code == 204

    # revoke된 refresh로 갱신 시도 -> 401 (재로그인 유도)
    res = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert res.status_code == 401
