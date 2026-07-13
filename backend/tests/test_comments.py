async def _make_prompt(auth_client, **over):
    res = await auth_client.post(
        "/prompts",
        json={"title": "댓글 테스트", "prompt_text": "본문입니다", "is_public": True, **over},
    )
    return res.json()["id"]


async def test_comment_crud_and_edited_flag(auth_client):
    pid = await _make_prompt(auth_client)

    # 작성
    res = await auth_client.post(f"/prompts/{pid}/comments", json={"content": "첫 댓글!"})
    assert res.status_code == 201
    c = res.json()
    assert c["content"] == "첫 댓글!"
    assert c["author"]["nickname"] == "tester"
    assert c["updated_at"] is None  # 수정 전에는 (수정됨) 없음

    # 목록 (최신순)
    await auth_client.post(f"/prompts/{pid}/comments", json={"content": "둘째 댓글"})
    res = await auth_client.get(f"/prompts/{pid}/comments")
    assert res.status_code == 200
    contents = [x["content"] for x in res.json()]
    assert contents == ["둘째 댓글", "첫 댓글!"]

    # 수정 → updated_at 설정
    res = await auth_client.patch(f"/comments/{c['id']}", json={"content": "고친 댓글"})
    assert res.status_code == 200
    assert res.json()["content"] == "고친 댓글"
    assert res.json()["updated_at"] is not None

    # 삭제
    res = await auth_client.delete(f"/comments/{c['id']}")
    assert res.status_code == 204
    res = await auth_client.get(f"/prompts/{pid}/comments")
    assert len(res.json()) == 1


async def test_comment_permissions(auth_client, client):
    pid = await _make_prompt(auth_client)
    cid = (
        await auth_client.post(f"/prompts/{pid}/comments", json={"content": "내 댓글"})
    ).json()["id"]

    # 미인증 작성 -> 401
    res = await client.post(
        f"/prompts/{pid}/comments", json={"content": "익명"}, headers={"Authorization": ""}
    )
    assert res.status_code == 401

    # 다른 사용자의 수정/삭제 -> 403
    await client.post(
        "/auth/signup",
        json={"email": "c@c.com", "password": "password123", "nickname": "other"},
    )
    login = await client.post(
        "/auth/login", json={"email": "c@c.com", "password": "password123"}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    res = await client.patch(f"/comments/{cid}", json={"content": "탈취"}, headers=headers)
    assert res.status_code == 403
    res = await client.delete(f"/comments/{cid}", headers=headers)
    assert res.status_code == 403

    # 빈 내용 -> 422
    res = await auth_client.post(f"/prompts/{pid}/comments", json={"content": ""})
    assert res.status_code == 422
