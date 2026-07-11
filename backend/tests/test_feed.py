async def _create_prompts(auth_client, n=15):
    ids = []
    for i in range(n):
        res = await auth_client.post(
            "/prompts",
            json={
                "title": f"prompt {i}",
                "prompt_text": f"본문 {i} [변수]",
                "tags": ["공통"] if i % 2 == 0 else ["홀수"],
                "is_public": True,
            },
        )
        ids.append(res.json()["id"])
    return ids


async def test_feed_cursor_no_dup_no_missing(auth_client):
    ids = await _create_prompts(auth_client, 15)

    res = await auth_client.get("/prompts", params={"sort": "latest"})
    assert res.status_code == 200
    page1 = res.json()
    assert len(page1["items"]) == 12
    assert page1["next_cursor"]

    res = await auth_client.get(
        "/prompts", params={"sort": "latest", "cursor": page1["next_cursor"]}
    )
    page2 = res.json()
    got = [p["id"] for p in page1["items"]] + [p["id"] for p in page2["items"]]
    assert len(got) == len(set(got)) == 15  # 중복·누락 없음
    assert set(got) == set(ids)
    assert page2["next_cursor"] is None


async def test_feed_tag_filter_and_private_excluded(auth_client):
    await _create_prompts(auth_client, 4)
    await auth_client.post(
        "/prompts",
        json={"title": "secret", "prompt_text": "비공개", "is_public": False},
    )
    res = await auth_client.get("/prompts", params={"tag": "공통"})
    items = res.json()["items"]
    assert len(items) == 2
    assert all("공통" in p["tags"] for p in items)

    res = await auth_client.get("/prompts")
    assert all(p["title"] != "secret" for p in res.json()["items"])


async def test_feed_popular_sort(auth_client):
    await _create_prompts(auth_client, 3)
    res = await auth_client.get("/prompts", params={"sort": "popular"})
    counts = [p["like_count"] for p in res.json()["items"]]
    assert counts == sorted(counts, reverse=True)
