async def _signup_login(client, email, nickname):
    await client.post(
        "/auth/signup",
        json={"email": email, "password": "password123", "nickname": nickname},
    )
    res = await client.post(
        "/auth/login", json={"email": email, "password": "password123"}
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def test_notifications_flow(auth_client, client):
    me = (await auth_client.get("/users/me")).json()
    other = await _signup_login(client, "n1@n.com", "알림꾼")
    other_id = (await client.get("/users/me", headers=other)).json()["id"]

    # 1. 팔로우 → 나에게 follow 알림 (언팔로우는 알림 없음)
    await client.post(f"/users/{me['id']}/follow", headers=other)
    res = await auth_client.get("/notifications")
    assert [n["type"] for n in res.json()] == ["follow"]
    assert res.json()[0]["actor"]["nickname"] == "알림꾼"
    assert res.json()[0]["is_read"] is False
    await client.post(f"/users/{me['id']}/follow", headers=other)  # unfollow
    assert len((await auth_client.get("/notifications")).json()) == 1

    # 2. 알림꾼이 나를 팔로우한 상태로 만들고, 내가 공개 글 게시 → 알림꾼에게 new_prompt
    await client.post(f"/users/{me['id']}/follow", headers=other)
    res = await auth_client.post(
        "/prompts", json={"title": "새 공개글", "prompt_text": "본문", "is_public": True}
    )
    pid = res.json()["id"]
    # 비공개 글은 알림 없음
    await auth_client.post(
        "/prompts", json={"title": "비밀글", "prompt_text": "본문", "is_public": False}
    )
    res = await client.get("/notifications", headers=other)
    notis = res.json()
    assert [n["type"] for n in notis] == ["new_prompt"]
    assert notis[0]["prompt_title"] == "새 공개글"

    # 3. 알림꾼이 내 글에 댓글 → 나에게 comment 알림 (본인 글 본인 댓글은 없음)
    await client.post(
        f"/prompts/{pid}/comments", json={"content": "좋아요!"}, headers=other
    )
    await auth_client.post(f"/prompts/{pid}/comments", json={"content": "셀프 댓글"})
    my_notis = (await auth_client.get("/notifications")).json()
    assert [n["type"] for n in my_notis][0] == "comment"  # 최신순
    assert sum(1 for n in my_notis if n["type"] == "comment") == 1

    # 4. 읽음 처리 (단건 + 전체)
    target = my_notis[0]
    res = await auth_client.patch(f"/notifications/{target['id']}/read")
    assert res.status_code == 204
    after = (await auth_client.get("/notifications")).json()
    assert next(n for n in after if n["id"] == target["id"])["is_read"] is True
    await auth_client.post("/notifications/read-all")
    assert all(n["is_read"] for n in (await auth_client.get("/notifications")).json())

    # 5. 남의 알림 읽음 처리 -> 404, 미인증 -> 401
    other_noti = (await client.get("/notifications", headers=other)).json()[0]
    res = await auth_client.patch(f"/notifications/{other_noti['id']}/read")
    assert res.status_code == 404
    res = await client.get("/notifications", headers={"Authorization": ""})
    assert res.status_code == 401
