# -*- coding: utf-8 -*-
"""
블로그 키워드 분석기
주제: 절약, 절약 마인드, 실천 과제

외부 서비스 없이 로컬에서 실행됩니다.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


@dataclass
class KeywordIdea:
    keyword: str
    intent: str
    reader_problem: str
    content_angle: str
    difficulty: int
    value: int
    actionability: int

    @property
    def score(self) -> int:
        return self.value * 3 + self.actionability * 2 - self.difficulty


BASE_KEYWORDS = {
    "절약": [
        "절약 습관", "생활비 절약", "식비 절약", "고정비 줄이기", "소비 습관 고치기",
        "돈 모으는 방법", "가계부 쓰는 법", "충동구매 줄이기", "미니멀 소비", "월급 관리",
        "무지출 챌린지", "짠테크", "현명한 소비", "저축 루틴", "절약 브이로그 글감",
    ],
    "마인드": [
        "절약 마인드", "돈을 대하는 태도", "소비 기준 세우기", "비교 소비 끊기", "만족 지연",
        "작은 돈의 힘", "소비 욕망 다루기", "돈 걱정 줄이는 습관", "가난한 습관 바꾸기", "경제적 안정감",
    ],
    "실천": [
        "하루 천원 절약", "일주일 식비 계획", "냉장고 파먹기", "구독 서비스 정리", "외식비 줄이기",
        "커피값 줄이기", "대중교통 절약", "전기요금 절약", "통신비 절약", "보험료 점검",
        "소비 기록표", "절약 체크리스트", "30일 절약 챌린지", "월말 결산", "비상금 만들기",
    ],
}

INTENT_RULES = [
    ("방법", "정보 탐색", "무엇부터 해야 할지 모름"),
    ("습관", "문제 해결", "꾸준히 실천하지 못함"),
    ("줄이기", "즉시 실행", "지출을 바로 낮추고 싶음"),
    ("챌린지", "참여형", "혼자 하면 지속하기 어려움"),
    ("체크리스트", "실천 도구", "구체적인 점검표가 필요함"),
    ("마인드", "태도 전환", "절약이 궁상맞게 느껴짐"),
    ("가계부", "관리 도구", "돈 흐름을 파악하지 못함"),
    ("고정비", "구조 개선", "매달 빠져나가는 돈이 큼"),
]


def classify_intent(keyword: str) -> tuple[str, str]:
    for token, intent, problem in INTENT_RULES:
        if token in keyword:
            return intent, problem
    return "정보 탐색", "절약을 시작하고 싶지만 방향이 흐림"


def make_angle(keyword: str, theme: str) -> str:
    if "마인드" in keyword or "태도" in keyword or "욕망" in keyword:
        return "절약을 참는 일이 아니라 선택 기준을 세우는 일로 설명"
    if "식비" in keyword or "냉장고" in keyword or "외식" in keyword:
        return "이번 주 바로 따라 할 수 있는 식비 절약 루틴 제안"
    if "고정비" in keyword or "구독" in keyword or "통신비" in keyword or "보험료" in keyword:
        return "한 번 정리하면 매달 효과가 나는 구조적 절약법 제안"
    if "챌린지" in keyword or "체크리스트" in keyword:
        return "독자가 저장하고 따라 할 수 있는 실천표 중심 글"
    return f"{theme}을 일상 언어로 풀어 초보자도 바로 실행하게 구성"


def estimate(keyword: str) -> tuple[int, int, int]:
    difficulty = 5
    value = 6
    actionability = 6

    if any(x in keyword for x in ["체크리스트", "줄이기", "계획", "정리", "챌린지"]):
        actionability += 2
        value += 1
    if any(x in keyword for x in ["고정비", "보험료", "통신비", "구독"]):
        value += 2
        difficulty += 1
    if any(x in keyword for x in ["마인드", "태도", "욕망", "비교"]):
        difficulty += 1
        value += 1
    if any(x in keyword for x in ["하루", "일주일", "30일"]):
        actionability += 1
        difficulty -= 1

    return max(1, min(10, difficulty)), max(1, min(10, value)), max(1, min(10, actionability))


def generate_keywords(theme: str) -> list[KeywordIdea]:
    raw: list[str] = []
    for words in BASE_KEYWORDS.values():
        raw.extend(words)

    theme = theme.strip() or "절약"
    if theme not in raw:
        raw.insert(0, theme)
        raw.extend([
            f"{theme} 방법",
            f"{theme} 습관",
            f"{theme} 체크리스트",
            f"{theme} 실천 과제",
            f"{theme} 마인드",
        ])

    seen = set()
    ideas: list[KeywordIdea] = []
    for keyword in raw:
        if keyword in seen:
            continue
        seen.add(keyword)
        intent, problem = classify_intent(keyword)
        difficulty, value, actionability = estimate(keyword)
        ideas.append(
            KeywordIdea(
                keyword=keyword,
                intent=intent,
                reader_problem=problem,
                content_angle=make_angle(keyword, theme),
                difficulty=difficulty,
                value=value,
                actionability=actionability,
            )
        )
    return sorted(ideas, key=lambda x: x.score, reverse=True)


def make_titles(keyword: str) -> list[str]:
    obj = object_particle(keyword)
    return [
        f"{keyword}, 오늘부터 바로 시작하는 현실적인 방법",
        f"돈이 새는 사람을 위한 {keyword} 체크리스트",
        f"절약이 힘든 이유와 {keyword}{obj} 오래 지속하는 법",
        f"한 달 뒤 차이가 나는 {keyword} 실천 과제 7가지",
    ]


def make_outline(keyword: str) -> list[str]:
    obj = object_particle(keyword)
    return [
        "왜 절약이 필요한가: 불안 줄이기와 선택권 늘리기",
        "절약을 방해하는 마음: 비교, 보상 심리, 작은 돈 무시하기",
        f"핵심 주제: {keyword}{obj} 일상에서 적용하는 법",
        "오늘 할 수 있는 실천 과제 3가지",
        "일주일 동안 점검할 기록표",
        "포기하지 않기 위한 기준: 완벽보다 반복",
    ]


def has_final_consonant(text: str) -> bool:
    if not text:
        return False
    ch = text[-1]
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        return (code - 0xAC00) % 28 != 0
    return False


def object_particle(text: str) -> str:
    return "을" if has_final_consonant(text) else "를"


def render_markdown(theme: str, ideas: list[KeywordIdea], top_n: int) -> str:
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    top = ideas[:top_n]
    lines: list[str] = []
    lines.append(f"# 블로그 키워드 분석 결과: {theme}")
    lines.append("")
    lines.append(f"- 생성 시각: {now:%Y-%m-%d %H:%M:%S} KST")
    lines.append("- 관심사: 절약")
    lines.append("- 글 방향: 절약을 위한 마인드와 실천 과제")
    lines.append("")
    lines.append("## 추천 키워드 순위")
    lines.append("")
    lines.append("| 순위 | 키워드 | 의도 | 점수 | 난이도 | 가치 | 실행성 | 독자 문제 |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---|")
    for i, item in enumerate(top, 1):
        lines.append(
            f"| {i} | {item.keyword} | {item.intent} | {item.score} | {item.difficulty} | {item.value} | {item.actionability} | {item.reader_problem} |"
        )

    lines.append("")
    lines.append("## 상위 키워드별 글감")
    lines.append("")
    for item in top:
        lines.append(f"### {item.keyword}")
        lines.append("")
        lines.append(f"- 검색 의도: {item.intent}")
        lines.append(f"- 독자 문제: {item.reader_problem}")
        lines.append(f"- 글쓰기 각도: {item.content_angle}")
        lines.append("")
        lines.append("#### 제목 후보")
        for title in make_titles(item.keyword):
            lines.append(f"- {title}")
        lines.append("")
        lines.append("#### 글 구성")
        for part in make_outline(item.keyword):
            lines.append(f"- {part}")
        lines.append("")

    lines.append("## 바로 쓰기 좋은 첫 글 추천")
    lines.append("")
    first = top[0]
    lines.append(f"첫 글은 **{first.keyword}**로 시작하는 것이 좋습니다.")
    lines.append("실행성이 높고, 독자가 바로 따라 할 수 있어 저장과 공유를 유도하기 쉽습니다.")
    lines.append("")
    lines.append("## 첫 글 초안 구조")
    lines.append("")
    lines.append(f"# {make_titles(first.keyword)[0]}")
    lines.append("")
    lines.append("1. 절약은 궁핍함이 아니라 선택권을 늘리는 일입니다.")
    lines.append("2. 많은 사람이 절약에 실패하는 이유는 의지가 약해서가 아니라 기준이 없기 때문입니다.")
    lines.append(f"3. 오늘의 주제는 `{first.keyword}`입니다.")
    lines.append("4. 먼저 이번 달에 새고 있는 돈을 하나만 찾아봅니다.")
    lines.append("5. 다음으로 오늘 바로 줄일 수 있는 지출을 하나 정합니다.")
    lines.append("6. 마지막으로 일주일 뒤 결과를 기록합니다.")
    lines.append("7. 절약은 한 번에 크게 바꾸는 것이 아니라, 작은 선택을 반복하는 기술입니다.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="절약 블로그 키워드 분석기")
    parser.add_argument("--theme", default="절약", help="분석할 주제")
    parser.add_argument("--top", type=int, default=10, help="상위 몇 개 키워드를 출력할지")
    parser.add_argument("--out", default="", help="결과 마크다운 저장 경로")
    args = parser.parse_args()

    ideas = generate_keywords(args.theme)
    markdown = render_markdown(args.theme, ideas, args.top)

    if args.out:
        out = Path(args.out)
    else:
        stamp = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")
        out = Path.cwd() / f"keyword_report_{stamp}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    print(f"저장 완료: {out}")
    print(f"추천 1순위: {ideas[0].keyword}")


if __name__ == "__main__":
    main()
