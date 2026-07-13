async def _signup_login(client, email, nickname):
    await client.post(
        "/auth/signup",
        json={"email": email, "password": "password123", "nickname": nickname},
    )
    res = await client.post(
        "/auth/login", json={"email": email, "password": "password123"}
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def test_public_profile_and_public_prompts_only(auth_client):
    me = (await auth_client.get("/users/me")).json()
    await auth_client.post(
        "/prompts", json={"title": "공개글", "prompt_text": "본문", "is_public": True}
    )
    await auth_client.post(
        "/prompts", json={"title": "비밀글", "prompt_text": "본문", "is_public": False}
    )

    res = await auth_client.get(f"/users/{me['id']}", headers={"Authorization": ""})
    assert res.status_code == 200
    body = res.json()
    assert body["nickname"] == "tester"
    assert "email" not in body  # 공개 프로필에 email 비노출
    assert body["follower_count"] == 0 and body["is_following"] is False

    res = await auth_client.get(f"/users/{me['id']}/prompts", headers={"Authorization": ""})
    titles = [p["title"] for p in res.json()]
    assert titles == ["공개글"]  # 비공개 제외

    res = await auth_client.get("/users/999999")
    assert res.status_code == 404


async def test_follow_toggle_counts_and_lists(auth_client, client):
    me = (await auth_client.get("/users/me")).json()
    other = await _signup_login(client, "f1@f.com", "팔로워일")

    # other가 me를 팔로우
    res = await client.post(f"/users/{me['id']}/follow", headers=other)
    assert res.status_code == 200
    assert res.json() == {"is_following": True, "follower_count": 1}

    # 프로필에서 팔로우 상태/카운트 확인 (other 시점)
    res = await client.get(f"/users/{me['id']}", headers=other)
    assert res.json()["follower_count"] == 1
    assert res.json()["is_following"] is True

    # 팔로워/팔로잉 목록
    res = await client.get(f"/users/{me['id']}/followers")
    assert [u["nickname"] for u in res.json()] == ["팔로워일"]
    other_id = (await client.get(f"/users/{me['id']}/followers")).json()[0]["id"]
    res = await client.get(f"/users/{other_id}/following")
    assert [u["nickname"] for u in res.json()] == ["tester"]

    # 재토글 = 언팔로우
    res = await client.post(f"/users/{me['id']}/follow", headers=other)
    assert res.json() == {"is_following": False, "follower_count": 0}

    # 자기 자신 팔로우 -> 400, 미인증 -> 401
    res = await auth_client.post(f"/users/{me['id']}/follow")
    assert res.status_code == 400
    res = await client.post(
        f"/users/{me['id']}/follow", headers={"Authorization": ""}
    )
    assert res.status_code == 401
