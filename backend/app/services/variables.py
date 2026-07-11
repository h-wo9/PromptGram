import re

_VAR_PATTERN = re.compile(r"\[([^\[\]\n]{1,50})\]")


def parse_variables(prompt_text: str) -> list[str]:
    """prompt_text에서 [변수명] 패턴을 추출 (등장 순서 유지, 중복 제거)."""
    seen: dict[str, None] = {}
    for match in _VAR_PATTERN.finditer(prompt_text):
        name = match.group(1).strip()
        if name:
            seen.setdefault(name)
    return list(seen)
