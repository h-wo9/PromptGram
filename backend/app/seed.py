"""데모 데이터 시딩: python -m app.seed"""

import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.core.db import async_session_factory
from app.core.security import hash_password
from app.crud.prompt import set_prompt_tags
from app.models import Bookmark, Like, Prompt, PromptTag, Tag, User
from app.services.variables import parse_variables

USERS = [
    ("demo@promptgram.dev", "demo1234", "데모유저"),
    ("mina@promptgram.dev", "demo1234", "미나"),
    ("dev@promptgram.dev", "demo1234", "개발자킴"),
]

SOURCES = ["ChatGPT", "Claude", "Gemini"]

PROMPTS = [
    ("코드 리뷰 요청 템플릿", "다음 [언어] 코드를 리뷰해줘. 특히 [관점] 관점에서 개선점을 알려줘:\n\n[코드]", ["개발", "코드리뷰"]),
    ("이메일 정중하게 다듬기", "아래 이메일을 [톤] 톤으로 다듬어줘. 받는 사람은 [수신자]야:\n\n[초안]", ["글쓰기", "업무"]),
    ("논문 요약", "다음 논문 초록을 3문장으로 요약하고 핵심 기여를 bullet으로 정리해줘:\n\n[초록]", ["연구", "요약"]),
    ("SQL 쿼리 최적화", "이 [DB종류] 쿼리를 최적화해줘. 실행 계획 관점에서 설명도 부탁해:\n\n[쿼리]", ["개발", "SQL"]),
    ("여행 일정 짜기", "[도시]에서 [일수]일 동안의 여행 일정을 짜줘. 예산은 [예산]이고 [스타일] 스타일을 선호해.", ["여행", "라이프"]),
    ("면접 예상 질문", "[직무] 포지션 면접에서 나올 만한 질문 10개와 모범 답변 포인트를 알려줘. 경력은 [연차]야.", ["커리어", "면접"]),
    ("블로그 글 개요", "[주제]에 대한 블로그 글 개요를 잡아줘. 타겟 독자는 [독자]이고 SEO 키워드를 포함해줘.", ["글쓰기", "블로그"]),
    ("영어 회화 교정", "다음 영어 문장을 자연스럽게 교정하고, 왜 그렇게 고쳤는지 설명해줘:\n\n[문장]", ["영어", "학습"]),
    ("회의록 정리", "다음 회의 녹취록을 안건별로 정리하고 action item을 뽑아줘:\n\n[녹취록]", ["업무", "요약"]),
    ("정규식 생성기", "[요구사항]을 만족하는 정규식을 만들어줘. 테스트 케이스 5개도 함께.", ["개발", "정규식"]),
    ("아이 그림책 스토리", "[나이]살 아이를 위한 [주제] 그림책 스토리를 8장 분량으로 써줘.", ["창작", "육아"]),
    ("마케팅 카피 5종", "[제품]의 인스타그램 광고 카피를 5가지 톤으로 써줘. 타겟은 [타겟]이야.", ["마케팅", "카피"]),
    ("운동 루틴 설계", "주 [횟수]회, 회당 [시간]분으로 [목표]를 위한 운동 루틴을 짜줘. 장비는 [장비]만 있어.", ["건강", "운동"]),
    ("파이썬 에러 디버깅", "이 Python traceback을 분석하고 원인과 수정 방법을 알려줘:\n\n[에러로그]", ["개발", "Python"]),
    ("자소서 문항 답변", "[회사] [직무] 자소서 문항 '[문항]'에 대한 답변 초안을 작성해줘. 내 경험: [경험]", ["커리어", "자소서"]),
    ("요리 레시피 변형", "[요리] 레시피를 [인원]인분, [제약] 조건에 맞게 바꿔줘.", ["요리", "라이프"]),
    ("발표 스크립트", "[주제]에 대한 [시간]분짜리 발표 스크립트를 써줘. 청중은 [청중]이야.", ["업무", "발표"]),
    ("계약서 조항 쉬운 설명", "다음 계약서 조항을 일반인이 이해할 수 있게 풀어서 설명해줘:\n\n[조항]", ["법률", "생활"]),
    ("브랜드 네이밍", "[업종] 스타트업의 브랜드 이름 10개를 제안해줘. 컨셉 키워드: [키워드]", ["창업", "네이밍"]),
    ("독서 토론 질문", "[책제목]으로 독서 토론을 할 때 쓸 깊이 있는 질문 8개를 만들어줘.", ["독서", "모임"]),
    ("유튜브 스크립트 훅", "[주제] 유튜브 영상의 첫 30초 훅 스크립트를 3가지 버전으로 써줘.", ["콘텐츠", "유튜브"]),
    ("데이터 분석 계획", "[데이터셋] 데이터로 [질문]에 답하려면 어떤 분석을 해야 할지 단계별로 알려줘.", ["데이터", "분석"]),
    ("React 컴포넌트 설계", "[기능]을 하는 React 컴포넌트를 설계해줘. 상태 관리와 props 인터페이스 포함.", ["개발", "React"]),
    ("협상 시뮬레이션", "[상황]에서 연봉 협상을 한다고 가정하고, 상대방 역할을 맡아 시뮬레이션해줘.", ["커리어", "협상"]),
    ("하루 식단 짜기", "[칼로리]kcal 이내로 [식성] 기준 하루 식단을 짜줘. 알레르기: [알레르기]", ["건강", "식단"]),
    ("고객 응대 답변", "화가 난 고객의 다음 문의에 공감하면서도 정책을 지키는 답변을 써줘:\n\n[문의내용]", ["업무", "CS"]),
    ("시 쓰기", "[계절]과 [감정]을 소재로 한 현대시를 써줘. 은유를 풍부하게.", ["창작", "시"]),
    ("Git 커밋 메시지", "다음 변경사항에 대한 conventional commit 메시지를 만들어줘:\n\n[변경사항]", ["개발", "Git"]),
    ("스터디 커리큘럼", "[주제]를 [기간]주 만에 마스터하는 스터디 커리큘럼을 주차별로 짜줘. 수준: [수준]", ["학습", "스터디"]),
    ("제품 비교 분석", "[제품A]와 [제품B]를 가격, 성능, 사용성 관점에서 표로 비교해줘.", ["쇼핑", "비교"]),
]


async def seed() -> None:
    async with async_session_factory() as db:
        # 기존 데이터 정리 (idempotent)
        for model in (Like, Bookmark, PromptTag, Prompt, Tag, User):
            await db.execute(delete(model))
        await db.commit()

        users = [
            User(email=email, password_hash=hash_password(pw), nickname=nick)
            for email, pw, nick in USERS
        ]
        db.add_all(users)
        await db.flush()

        now = datetime.now(timezone.utc)
        rng = random.Random(42)
        prompts: list[Prompt] = []
        for i, (title, text, tags) in enumerate(PROMPTS):
            prompt = Prompt(
                user_id=rng.choice(users).id,
                title=title,
                prompt_text=text,
                ai_response=None,
                ai_source=rng.choice(SOURCES),
                variables=parse_variables(text),
                is_public=True,
                like_count=0,
                copy_count=rng.randint(0, 120),
                created_at=now - timedelta(hours=len(PROMPTS) - i, minutes=rng.randint(0, 50)),
            )
            db.add(prompt)
            await db.flush()
            await set_prompt_tags(db, prompt.id, tags)
            prompts.append(prompt)

        # 좋아요/스크랩 시딩 (+counter 동기화)
        for prompt in prompts:
            likers = rng.sample(users, rng.randint(0, len(users)))
            for u in likers:
                db.add(Like(user_id=u.id, prompt_id=prompt.id))
            prompt.like_count = len(likers)
            savers = rng.sample(users, rng.randint(0, 2))
            for u in savers:
                db.add(Bookmark(user_id=u.id, prompt_id=prompt.id))
            prompt.bookmark_count = len(savers)

        await db.commit()
        count = len((await db.scalars(select(Prompt.id))).all())
        print(f"seeded: {len(users)} users, {count} prompts")


if __name__ == "__main__":
    asyncio.run(seed())
