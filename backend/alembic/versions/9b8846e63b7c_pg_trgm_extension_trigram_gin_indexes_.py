"""pg_trgm extension + trigram GIN indexes for prompt search

Revision ID: 9b8846e63b7c
Revises: f6f67cab6f03
Create Date: 2026-07-14 01:21:40.833536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b8846e63b7c'
down_revision: Union[str, Sequence[str], None] = 'f6f67cab6f03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 한국어 검색: tsvector는 형태소(조사) 문제로 부적합 → pg_trgm 트라이그램 인덱스로
    # ILIKE '%q%' 부분 문자열 검색을 가속한다.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX ix_prompts_title_trgm ON prompts USING gin (title gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_prompts_prompt_text_trgm ON prompts USING gin (prompt_text gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_prompts_prompt_text_trgm")
    op.execute("DROP INDEX IF EXISTS ix_prompts_title_trgm")
