# 네이버 블로그 작성 대시보드 1차 버전

네이버 데이터랩의 검색어 트렌드를 매일 수집해, 신중년 대상 블로그 글감을 추천하고 Obsidian용 마크다운 리포트와 HTML 대시보드를 생성합니다.

## 현재 기능

- `keywords.json`에 분야와 관심 키워드 등록
- 네이버 데이터랩 통합검색어 트렌드 API 연동
- 최근 30일 데이터 수집
- 전일 대비 변화율·최근 7일 흐름 분석
- 추천도 점수 계산
- 블로그 제목 후보와 글 구성 제안 생성
- `reports/YYYY-MM-DD_naver_blog_report.md` 생성
- `dashboard.html` 생성
- `data/latest.json`, `data/history.json`에 원본·누적 데이터 저장
- API 키가 없으면 데모 모드로 자동 실행

## 데모 실행

Git Bash에서 프로젝트 폴더로 이동한 뒤 실행합니다.

```bash
cd 'D:/구글드라이브/Luke/GitHub/naverBlogDashboard'
python generate_dashboard.py --demo
```

실행 후 생성되는 파일:

```text
reports/YYYY-MM-DD_naver_blog_report.md
dashboard.html
data/latest.json
data/history.json
```

`dashboard.html`을 브라우저로 열면 오늘의 추천 키워드와 흐름을 확인할 수 있습니다.

## 실제 네이버 데이터 사용

네이버 개발자센터에서 데이터랩 API 애플리케이션을 등록한 뒤, API 키를 환경변수로 설정합니다. 키를 소스 파일이나 GitHub에 직접 기록하지 않습니다.

```bash
export NAVER_CLIENT_ID='발급받은_Client_ID'
export NAVER_CLIENT_SECRET='발급받은_Client_Secret'
python generate_dashboard.py
```

Windows Git Bash에서 현재 세션에만 설정하려면:

```bash
export NAVER_CLIENT_ID='발급받은_Client_ID'
export NAVER_CLIENT_SECRET='발급받은_Client_Secret'
```

API 오류가 발생하면 해당 키워드는 자동으로 데모 데이터로 대체되어 리포트 생성을 중단하지 않습니다. 운영 전에 오류 로그를 확인하는 것이 좋습니다.

## 키워드 수정

`keywords.json`의 `categories` 안에 분야와 키워드를 추가합니다.

```json
{
  "name": "신중년 건강",
  "keywords": ["중년 건강", "50대 건강관리", "무릎 통증"]
}
```

## 데이터 해석 주의

- 네이버 데이터랩 검색어 트렌드는 실제 검색 횟수가 아닌 상대 관심도 지수입니다.
- 검색 관심도가 높아도 블로그 경쟁도가 낮다는 뜻은 아닙니다.
- 건강·법률·정책 주제는 공식 기관 자료를 별도로 확인해야 합니다.
- API 키는 `.env`, GitHub, 마크다운 리포트에 기록하지 않습니다.

## 다음 단계

- 네이버 검색광고 키워드 도구의 실제 월간 검색량 연결
- 블로그 경쟁도 수동 입력 또는 별도 도구 연동
- Hermes 예약 실행으로 매일 리포트 생성
- Obsidian 데일리 노트 링크 자동 생성
- 텔레그램에 TOP 5 요약 알림
