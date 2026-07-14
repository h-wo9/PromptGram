#!/usr/bin/env bash
# PromptGram dev 서버 실행: backend(uvicorn) + frontend(vite)
# DB는 별도: docker compose up -d
set -e
cd "$(dirname "$0")"

# backend — 반드시 backend/ 에서 실행 (.env 로드가 CWD 기준)
(cd backend && exec .venv/bin/uvicorn app.main:app --reload --port 8000) &
BE_PID=$!

# frontend
(cd frontend && exec npm run dev) &
FE_PID=$!

trap 'echo; echo "서버 종료 중..."; kill $BE_PID $FE_PID 2>/dev/null; wait' INT TERM

echo ""
echo "  PromptGram dev"
echo "  ─ backend  http://localhost:8000  (docs: /docs)"
echo "  ─ frontend http://localhost:5173"
echo "  종료: Ctrl+C"
echo ""

wait
