"""네이버 데이터랩 기반 네이버 블로그 작성 대시보드 1차 버전.

API 키가 없으면 자동으로 데모 모드로 실행합니다.
실제 API 사용: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 환경변수 설정 후 실행.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import random
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "keywords.json"
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
API_URL = "https://openapi.naver.com/v1/datalab/search"


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def api_series(keyword: str, start: dt.date, end: dt.date) -> list[dict]:
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "timeUnit": "date",
        "keyword": [{"groupName": keyword, "keywords": [keyword]}],
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "X-Naver-Client-Id": os.environ["NAVER_CLIENT_ID"],
            "X-Naver-Client-Secret": os.environ["NAVER_CLIENT_SECRET"],
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    results = payload.get("results", [])
    return results[0].get("data", []) if results else []


def demo_series(keyword: str, days: int = 30) -> list[dict]:
    seed = sum(ord(c) for c in keyword)
    rng = random.Random(seed)
    base = 32 + seed % 48
    trend = ((seed % 11) - 4) / 100
    today = dt.date.today()
    values = []
    for index in range(days):
        wave = math.sin(index / 3.2 + seed) * 7
        noise = rng.uniform(-3.5, 3.5)
        value = max(4, min(100, base + index * trend + wave + noise))
        values.append({"period": (today - dt.timedelta(days=days - 1 - index)).isoformat(), "ratio": round(value, 2)})
    # Make a few topics visibly rise in the demo so the dashboard is useful on first run.
    if keyword in {"50대 건강관리", "중년 재취업", "정부지원금", "인공지능 활용"}:
        for index, item in enumerate(values[-7:]):
            item["ratio"] = round(min(100, item["ratio"] + index * 4), 2)
    return values


def collect(config: dict, demo: bool) -> list[dict]:
    end = dt.date.today()
    start = end - dt.timedelta(days=29)
    has_keys = bool(os.getenv("NAVER_CLIENT_ID") and os.getenv("NAVER_CLIENT_SECRET"))
    use_demo = demo or not has_keys
    records = []
    for category in config["categories"]:
        for keyword in category["keywords"]:
            try:
                series = demo_series(keyword) if use_demo else api_series(keyword, start, end)
                source = "demo" if use_demo else "naver-datalab"
            except Exception as exc:
                print(f"[WARN] {keyword}: API 실패 → 데모 데이터 사용 ({exc})")
                series = demo_series(keyword)
                source = "demo-fallback"
            records.append(analyze(category["name"], keyword, series, source))
    return records


def analyze(category: str, keyword: str, series: list[dict], source: str) -> dict:
    values = [float(item.get("ratio", 0)) for item in series if "ratio" in item]
    if not values:
        values = [0]
    current = values[-1]
    previous = values[-2] if len(values) > 1 else current
    avg7 = sum(values[-7:]) / min(7, len(values))
    prior7 = sum(values[-14:-7]) / min(7, max(1, len(values) - 7)) if len(values) > 7 else avg7
    change = ((current - previous) / previous * 100) if previous else 0
    weekly_change = ((avg7 - prior7) / prior7 * 100) if prior7 else 0
    score = max(0, min(100, 50 + weekly_change * 0.7 + change * 0.3))
    return {
        "category": category,
        "keyword": keyword,
        "series": series,
        "current": round(current, 2),
        "change": round(change, 1),
        "weekly_change": round(weekly_change, 1),
        "avg7": round(avg7, 2),
        "recommendation_score": round(score, 1),
        "source": source,
    }


def recommendation_text(record: dict) -> str:
    if record["weekly_change"] >= 15:
        return "급상승 — 오늘 우선 검토"
    if record["weekly_change"] >= 5:
        return "상승 — 글감 후보"
    if record["weekly_change"] <= -10:
        return "하락 — 추이 관찰"
    return "안정 — 장기 소재"


def title_candidates(keyword: str) -> list[str]:
    return [
        f"{keyword}, 지금 알아두면 좋은 핵심 정보",
        f"{keyword} 처음 시작하는 분들을 위한 쉬운 정리",
        f"{keyword}에 대해 많이 묻는 질문 5가지",
    ]


def summary_text(keyword: str) -> str:
    return f"이 글은 {keyword}를 실천할 때 먼저 확인할 항목과 생활 속 적용 방법을 정리하고, 무리하지 않고 꾸준히 이어갈 수 있는 절약 기준을 안내합니다."


def make_report(config: dict, records: list[dict], today: dt.date) -> str:
    top = sorted(records, key=lambda x: x["recommendation_score"], reverse=True)[:5]
    lines = [
        "---",
        f"title: 네이버 블로그 키워드 리포트 {today.isoformat()}",
        "tags: [네이버데이터랩, 블로그글감, 키워드분석, 데일리리포트]",
        f"date: {today.isoformat()}",
        f"source_mode: {top[0]['source'] if top else 'unknown'}",
        "---",
        "",
        f"# 네이버 블로그 키워드 리포트 — {today.isoformat()}",
        "",
        f"> 대상 독자: {config.get('target_audience', '미설정')}",
        "> 검색 관심도는 네이버 데이터랩의 상대 지수입니다. 실제 검색 횟수와는 다를 수 있습니다.",
        "",
        "## 오늘의 핵심 요약",
        "",
        f"- 분석 키워드: **{len(records)}개**",
        f"- 오늘 우선 검토할 키워드: **{top[0]['keyword'] if top else '없음'}**",
        f"- 데이터 모드: **{top[0]['source'] if top else '없음'}**",
        "",
        "## 오늘의 추천 키워드 TOP 5",
        "",
        "| 순위 | 분야 | 키워드 | 전일 대비 | 7일 흐름 | 추천도 | 판정 |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for index, item in enumerate(top, 1):
        lines.append(f"| {index} | {item['category']} | **{item['keyword']}** | {item['change']:+.1f}% | {item['weekly_change']:+.1f}% | {item['recommendation_score']:.1f} | {recommendation_text(item)} |")
    detail_keyword = config.get("detail_keyword", "절약")
    detailed = [item for item in top if detail_keyword in item["keyword"]][:3]
    for item in detailed:
        lines += ["", f"## {item['keyword']}", "", f"- 분야: {item['category']}", f"- 현재 관심도 지수: {item['current']}", f"- 전일 대비: {item['change']:+.1f}%", f"- 최근 7일 흐름: {item['weekly_change']:+.1f}%", "", "### 제목 후보", ""]
        lines += [f"- {title}" for title in title_candidates(item["keyword"])]
        lines += ["", "### 요약", "", summary_text(item["keyword"]), "", "### 글 구성 제안", "", f"1. 왜 {item['keyword']}이(가) 주목받는지", "2. 절약 효과를 확인하기 전에 점검할 항목", "3. 실제 생활에 적용하는 방법", "4. 무리하지 않고 꾸준히 이어가는 기준"]
    lines += ["", f"## {detail_keyword} 관련 상세 작성 대상: {len(detailed)}개"]
    lines += ["", "## 전체 키워드 현황", "", "| 분야 | 키워드 | 7일 흐름 | 추천도 |", "|---|---|---:|---:|"]
    for item in sorted(records, key=lambda x: (x["category"], -x["recommendation_score"])):
        lines.append(f"| {item['category']} | {item['keyword']} | {item['weekly_change']:+.1f}% | {item['recommendation_score']:.1f} |")
    lines += ["", "## 해석 주의사항", "", "- 데이터랩 검색어 트렌드는 0~100 상대 지수이며 실제 검색 건수가 아닙니다.", "- 급상승 키워드라도 블로그 경쟁도와 정보의 정확성을 별도로 확인해야 합니다.", "- 건강·법률·정책 글은 최신 공식 기관 자료를 확인한 뒤 작성합니다.", "", "## 원본 데이터", "", "- `data/latest.json`", "- 수집 모드: `" + (top[0]["source"] if top else "unknown") + "`"]
    return "\n".join(lines) + "\n"


def make_dashboard(config: dict, records: list[dict], today: dt.date) -> str:
    detail_keyword = config.get("detail_keyword", "절약")
    ranked = sorted(records, key=lambda x: x["recommendation_score"], reverse=True)
    detailed = [item for item in ranked if detail_keyword in item["keyword"]][:3]
    cards = []
    for index, item in enumerate(ranked[:5], 1):
        trend_class = "up" if item["weekly_change"] >= 0 else "down"
        cards.append(f'<article class="card"><div class="rank">TOP {index} · {html.escape(item["category"])}</div><div class="keyword">{html.escape(item["keyword"])}</div><div class="category">{recommendation_text(item)}</div><div class="numbers"><div class="num"><b class="{trend_class}">{item["weekly_change"]:+.1f}%</b><span>7일 흐름</span></div><div class="num"><b>{item["recommendation_score"]:.1f}</b><span>추천도</span></div></div></article>')
    rows = []
    for item in sorted(records, key=lambda x: (x["category"], -x["recommendation_score"])):
        trend_class = "up" if item["weekly_change"] >= 0 else "down"
        rows.append(f'<tr><td>{html.escape(item["category"])}</td><td><b>{html.escape(item["keyword"])}</b></td><td class="{trend_class}">{item["weekly_change"]:+.1f}%</td><td>{item["recommendation_score"]:.1f}</td><td>{recommendation_text(item)}</td></tr>')
    details = []
    for item in detailed:
        title_list = "".join(f'<li>{html.escape(title)}</li>' for title in title_candidates(item["keyword"]))
        details.append(f'<article class="detail-card"><div class="detail-label">{html.escape(item["category"])}</div><h2>{html.escape(item["keyword"])}</h2><p class="summary">{html.escape(summary_text(item["keyword"]))}</p><h3>제목 후보</h3><ul>{title_list}</ul><h3>글 구성</h3><ol><li>왜 {html.escape(item["keyword"])}이(가) 주목받는지</li><li>절약 전에 점검할 항목</li><li>생활 속 적용 방법</li><li>꾸준히 이어가는 기준</li></ol></article>')
    payload = json.dumps({"date": today.isoformat(), "target": config.get("target_audience", ""), "records": records}, ensure_ascii=False)
    css = ":root{--line:#2d4267;--text:#edf4ff;--muted:#9eb0d0;--accent:#78adff;--mint:#68e1ae;--rose:#ff8da8;--amber:#ffd477}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 0,#29477e,#0d1526 43%);color:var(--text);font:15px/1.5 system-ui,sans-serif}main{max-width:1220px;margin:auto;padding:36px 20px 60px}.eyebrow{color:var(--accent);font-weight:800;letter-spacing:.1em;font-size:11px;text-transform:uppercase}h1{font-size:clamp(28px,5vw,48px);margin:8px 0}.sub{color:var(--muted)}.meta{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}.pill{background:#ffffff0d;border:1px solid var(--line);border-radius:99px;padding:8px 12px;color:var(--muted)}.pill b{color:var(--text)}.grid,.detail-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.card,.detail-card{background:#16223add;border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 15px 40px #0003}.rank,.detail-label{font-size:12px;color:var(--accent);font-weight:800}.keyword{font-size:21px;font-weight:850;margin:7px 0}.category{color:var(--muted);font-size:12px}.numbers{display:flex;gap:18px;margin-top:14px}.num b{display:block;font-size:20px}.num span{font-size:11px;color:var(--muted)}.up{color:var(--mint)}.down{color:var(--rose)}.table-wrap{overflow:auto;margin-top:20px}table{width:100%;border-collapse:collapse;background:#16223a99;border:1px solid var(--line)}th,td{padding:12px;text-align:left;border-bottom:1px solid #ffffff10;white-space:nowrap}th{color:var(--muted);font-size:12px}.details{margin-top:26px}.details h2{font-size:21px}.detail-card{background:linear-gradient(145deg,#1b2c4b,#142039)}.detail-card h2{font-size:21px;margin:4px 0 12px}.detail-card h3{font-size:13px;color:#c8d7f5;margin:17px 0 7px}.detail-card .summary{color:#c7d5ed;font-size:13px;background:#ffffff08;border-radius:10px;padding:11px}.detail-card ul,.detail-card ol{margin:0;padding-left:21px;color:var(--muted);font-size:13px}.detail-card li{margin:5px 0}.notice{margin-top:20px;color:var(--muted);font-size:12px;border-left:3px solid var(--amber);padding-left:12px}@media(max-width:550px){main{padding:25px 14px}}"
    template = """<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>네이버 블로그 작성 대시보드</title><style>__CSS__</style></head><body><main><div class='eyebrow'>Naver DataLab · Blog Writer Dashboard</div><h1>오늘의 블로그 글감</h1><p class='sub'>__DATE__ · 대상 독자: __TARGET__</p><div class='meta'><div class='pill'>분석 키워드 <b>__TOTAL__</b>개</div><div class='pill'>데이터 모드 <b>__MODE__</b></div><div class='pill'>추천 글감 <b>__TOP__</b></div></div><section class='grid'>__CARDS__</section><div class='table-wrap'><table><thead><tr><th>분야</th><th>키워드</th><th>7일 흐름</th><th>추천도</th><th>판정</th></tr></thead><tbody>__ROWS__</tbody></table></div><section class='details'><h2>절약 관련 제목과 요약</h2><div class='detail-grid'>__DETAILS__</div></section><p class='notice'>데이터랩 관심도는 상대 지수입니다. 건강·법률·정책 주제는 공식 자료를 확인한 뒤 글을 작성하세요.</p></main><script>const data=__PAYLOAD__;</script></body></html>"""
    top_keyword = ranked[0]["keyword"] if ranked else "없음"
    mode = records[0]["source"] if records else "없음"
    return (template.replace("__CSS__", css).replace("__DATE__", today.isoformat()).replace("__TARGET__", html.escape(config.get("target_audience", ""))).replace("__TOTAL__", str(len(records))).replace("__MODE__", html.escape(mode)).replace("__TOP__", html.escape(top_keyword)).replace("__CARDS__", "".join(cards)).replace("__ROWS__", "".join(rows)).replace("__DETAILS__", "".join(details)).replace("__PAYLOAD__", payload))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="API 대신 데모 데이터 사용")
    args = parser.parse_args()
    config = read_json(CONFIG, {"target_audience": "신중년", "categories": []})
    today = dt.date.today()
    records = collect(config, args.demo)
    DATA.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)
    latest = {"date": today.isoformat(), "records": records}
    (DATA / "latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
    history_path = DATA / "history.json"
    history = read_json(history_path, [])
    history = [x for x in history if x.get("date") != today.isoformat()]
    history.append(latest)
    history_path.write_text(json.dumps(history[-90:], ensure_ascii=False, indent=2), encoding="utf-8")
    (REPORTS / f"{today.isoformat()}_naver_blog_report.md").write_text(make_report(config, records, today), encoding="utf-8")
    dashboard_html = make_dashboard(config, records, today)
    (ROOT / "dashboard.html").write_text(dashboard_html, encoding="utf-8")
    (ROOT / "index.html").write_text(dashboard_html, encoding="utf-8")
    print(f"[OK] {len(records)} keywords analyzed")
    print(f"[OK] report: {REPORTS / f'{today.isoformat()}_naver_blog_report.md'}")
    print(f"[OK] dashboard: {ROOT / 'dashboard.html'}")
    print(f"[OK] mode: {records[0]['source'] if records else 'none'}")


if __name__ == "__main__":
    main()
