# 헤르메스 env 파일 수정

- #로 표시된 주석 제거하고 작성
- TELEGRAM_BOT_TOKEN= BotFather가 준 토큰
- TELEGRAM_ALLOWED_USERS= 넘버로 된 고유 숫자가 필요
- TELEGRAM_HOME_CHANNEL= @텔레그램 bot 이름

# config.yaml 파일 수정
model:
  default: tencent/hy3:free
  provider: nous
  base_url: https://inference-api.nousresearch.com/v1

# 구글 API 에러
- 오류가 발견되고 있어서 일단 모델을 바꾸면서 진행

/hermes model
명령어를 치면 모델 선택이 가능

Error: Attempted to access streaming response content, without having called read().

  이 에러, 정확히 같은 사례가 Hermes 공식 GitHub 이슈에 등록되어 있어요.

**무슨 상황이냐면**
Hermes 데스크톱 앱에서 세션을 시작하고 워크스페이스 도구(git status, 파일 작업 등)를 실행시키면, 실행이 끝난 직후 이 에러가 빨간 팝업으로 뜨는 버그예요. Google Gemini 프로바이더를 쓸 때 특히 자주 나타나는 걸로 보고돼 있어요.

**중요한 점 — 실제로는 문제없이 작동함**
이건 UI 레벨에서만 뜨는 표시상 에러이고, 실제 백엔드(httpx) 로직은 정상 작동한다고 되어 있어요. 즉:
- 도구 실행 결과는 실제로는 제대로 처리되고 모델에게 잘 전달됨
- 다만 화면에 있는 **모니터링/진단 UI 레이어**가 이미 다 써버린(consumed) 스트리밍 응답에 다시 접근하려다가 에러를 띄우는 것

**왜 이런 에러가 뜨는지 (기술적으로)**
UI 모니터링 레이어나 진단 도구가, 백엔드가 이미 aiter_lines()로 다 읽어서 닫아버린 httpx 스트림에서 response.content나 response.text를 다시 읽으려고 시도하는 게 원인이라고 되어 있어요.

**어떻게 하면 되나**
- 현재(2026년 7월) 기준 **알려진 버그**이고, 아직 오픈 상태 (P2 - 중간 우선순위)로 등록되어 있어요
- 대응은 딱히 필요 없고, **그냥 에러 팝업만 닫고 무시**하시면 됩니다 — 실제 작업(git status, 파일 작업 등)은 정상적으로 완료됩니다
- 혹시 계속 거슬리시면 Gemini 프로바이더 대신 다른 프로바이더(OpenAI, Anthropic 등)로 바꿔보시는 게 임시 우회책이 될 수 있어요

혹시 지금 config.yaml에서 어떤 프로바이더 쓰고 계신지 알려주시면 좀 더 구체적으로 봐드릴게요.