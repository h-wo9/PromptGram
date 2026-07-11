PROMPT = {
    "title": "번역 프롬프트",
    "prompt_text": "다음 [원문]을 [언어]로 번역해줘. 톤은 [원문] 유지.",
    "ai_source": "ChatGPT",
    "tags": ["#번역", "translation", "번역"],
    "is_public": True,
}


async def test_create_parses_variables_and_upserts_tags(auth_client):
    res = await auth_client.post("/prompts", json=PROMPT)
    assert res.status_code == 201
    data = res.json()
    assert data["variables"] == ["원문", "언어"]
    assert data["tags"] == ["번역", "translation"]
    assert data["author"]["nickname"] == "tester"

    # 같은 태그 재사용 시 upsert (중복 생성 없이 성공)
    res = await auth_client.post("/prompts", json={**PROMPT, "title": "second"})
    assert res.status_code == 201
    assert res.json()["tags"] == ["번역", "translation"]


async def test_update_and_delete_author_only(auth_client, client):
    prompt_id = (await auth_client.post("/prompts", json=PROMPT)).json()["id"]

    res = await auth_client.patch(
        f"/prompts/{prompt_id}",
        json={"prompt_text": "요약해줘: [본문]", "tags": ["요약"]},
    )
    assert res.status_code == 200
    assert res.json()["variables"] == ["본문"]
    assert res.json()["tags"] == ["요약"]

    # 다른 사용자로 수정/삭제 시도 -> 403
    await client.post(
        "/auth/signup",
        json={"email": "x@y.com", "password": "password123", "nickname": "other"},
    )
    login = await client.post(
        "/auth/login", json={"email": "x@y.com", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    res = await client.patch(
        f"/prompts/{prompt_id}", json={"title": "hack"}, headers=other_headers
    )
    assert res.status_code == 403
    res = await client.delete(f"/prompts/{prompt_id}", headers=other_headers)
    assert res.status_code == 403

    res = await auth_client.delete(f"/prompts/{prompt_id}")
    assert res.status_code == 204
    res = await auth_client.get(f"/prompts/{prompt_id}")
    assert res.status_code == 404


async def test_private_prompt_hidden_from_others(auth_client, client):
    prompt_id = (
        await auth_client.post("/prompts", json={**PROMPT, "is_public": False})
    ).json()["id"]
    # 비로그인 조회 -> 404
    res = await client.get(f"/prompts/{prompt_id}", headers={"Authorization": ""})
    assert res.status_code == 404
    # 작성자 조회 -> 200
    res = await auth_client.get(f"/prompts/{prompt_id}")
    assert res.status_code == 200
