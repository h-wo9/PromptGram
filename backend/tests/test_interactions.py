async def _create(auth_client, **over):
    payload = {
        "title": "t",
        "prompt_text": "본문 [x]",
        "tags": ["태그"],
        "is_public": True,
        **over,
    }
    res = await auth_client.post("/prompts", json=payload)
    return res.json()["id"]


async def test_like_bookmark_toggle_and_counters(auth_client):
    pid = await _create(auth_client)

    res = await auth_client.post(f"/prompts/{pid}/like")
    assert (res.json()["is_liked"], res.json()["like_count"]) == (True, 1)
    # 재요청 = 토글 해제 (중복 방지)
    res = await auth_client.post(f"/prompts/{pid}/like")
    assert (res.json()["is_liked"], res.json()["like_count"]) == (False, 0)

    res = await auth_client.post(f"/prompts/{pid}/bookmark")
    assert (res.json()["is_bookmarked"], res.json()["bookmark_count"]) == (True, 1)
    res = await auth_client.post(f"/prompts/{pid}/bookmark")
    assert (res.json()["is_bookmarked"], res.json()["bookmark_count"]) == (False, 0)

    res = await auth_client.post(f"/prompts/{pid}/copy")
    assert res.json()["copy_count"] == 1
    # 같은 계정 재복사 -> 카운트 유지 (복사 자체는 성공)
    res = await auth_client.post(f"/prompts/{pid}/copy")
    assert res.status_code == 200
    assert res.json()["copy_count"] == 1

    # 다른 계정 복사 -> +1
    await auth_client.post(
        "/auth/signup",
        json={"email": "cp@cp.com", "password": "password123", "nickname": "copier"},
    )
    login = await auth_client.post(
        "/auth/login", json={"email": "cp@cp.com", "password": "password123"}
    )
    other = {"Authorization": f"Bearer {login.json()['access_token']}"}
    res = await auth_client.post(f"/prompts/{pid}/copy", headers=other)
    assert res.json()["copy_count"] == 2

    # 비로그인 복사 -> 카운트 안 오름
    res = await auth_client.post(f"/prompts/{pid}/copy", headers={"Authorization": ""})
    assert res.status_code == 200
    assert res.json()["copy_count"] == 2


async def test_mypage_tabs(auth_client):
    mine = await _create(auth_client, title="mine")
    private = await _create(auth_client, title="private", is_public=False)

    res = await auth_client.get("/users/me/prompts")
    titles = [p["title"] for p in res.json()]
    assert set(titles) == {"mine", "private"}  # 내 글에는 비공개 포함

    await auth_client.post(f"/prompts/{mine}/bookmark")
    res = await auth_client.get("/users/me/bookmarks")
    assert [p["id"] for p in res.json()] == [mine]


async def test_profile_update(auth_client):
    res = await auth_client.patch(
        "/users/me",
        json={"nickname": "새닉네임", "bio": "한 줄 소개", "profile_image_url": "https://img.example/a.png"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["nickname"] == "새닉네임"
    assert body["bio"] == "한 줄 소개"
