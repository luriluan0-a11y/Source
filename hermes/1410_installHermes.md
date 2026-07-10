
# Hermes Agent
24시간 돌아가는 맞춤형 자동화 에이전트(gateway가 열려 있다면)

## 게이트웨이(Gateway)란?
- OpenClaw나 Hermes 같은 AI 에이전트 프로그램이 텔레그램, 왓츠앱, 위챗 같은 메신저 앱과 실제로 "연결되어 메시지를 주고받는 프로그램/서버 부분"을 가리킴

- Nous Research에서 개발한 헤르메스 에이전트(Hermes Agent)는 자가 개선 기능과 강력한 도구 사용 능력을 갖춘 오픈소스 에이전트 런타임임 
- 무료 티어인 **Gemini API**와 연동하고 **텔레그램**을 인터페이스로 사용하면 아주 훌륭한 나만의 개인 비서를 구축할 수 있음(일단 Gemini가 결제가 되어 있다고 하시니...)
- 사람이 할 수 있는 모든 일을 함, 자가 발전을 함(돈을 많이 쓰면 잘 큼)
- 작업 수행 -> 학습 -> 성장 -> 반복
- 전체적인 설치 및 연동 프로세스를 단계별로 정리해 드리겠음

## Claude code vs Hermes
- claude code로 소프트웨어를 개발하고, Hermes로는 반복적인 일을 시키면 좋음
- 둘 다 사용하면 시너지가 남
- Hermes: 모닝 브리핑, 마케팅, 일정
- claude code: 코드 베이스, 커밋
- 사람은 관리만 하고, 반복적인 일은 Agent가 함


우선!!! 이것부터 할게요.
agent.md(예: claude.md) 지침을 넣어 놓은 파일
헤르메스도 hermes.md가 있음 예) 비서, 마케터 등의 페르소나가 있음
헤르메스에 필요한 지침이 있어야 함
나에게 최적화된 에이전트를 만드는 것이기 때문에 hermes.md 파일을 만들어야 함

//클릭하면 사이트 연결되도록 해줘.
스킬 모아둔 사이트
https://www.skills.sh

## 무엇을 시킬 것인가?
- 오늘 특강을 오신 동추원몰 대표님을 마케팅 전문가라고 했을 때, 에이전트를 부르는 이름은?
예) 동추원몰 대표님, 이것 좀 부탁드립니다.
- 내 일상에서 업무 혹은 도움을 받을 용도로 사용하는 것이기 때문에 무엇을 할지, 어떤 역할을 할지를 정해보도록 함
- 저는 매일 은평경우회에 인사말을 보내드리고 있어서 **계절 + 간단한 교훈이나 글귀를 넣어 작성하는 포멧**을 만들어 매일 안내하도록 만들어 봄

/model
openAI codex 추천(GPT5.5, 월 29,000원 (저 openAI 관련자 아닙니다.)
claude는 6월부터 정책이 바뀌어서 사용이 어렵습니다. 토큰이 매우 부족합니다.

hermes setup -> 링크 열어서 로그인



---

## 1단계: 사전 준비 (API 키 발급)

### 1. Google Gemini API 키 발급

1. [Google AI Studio](https://aistudio.google.com/)에 접속하여 구글 계정으로 로그인함
2. **'Get API key'** 버튼을 클릭하여 새 API 키를 생성함
3. 생성된 키(`AIzaSy...`)를 안전한 곳에 복사해 둠

### 2. 텔레그램 봇 토큰 발급

1. 텔레그램에서 **@BotFather**를 검색해 대화를 시작함
2. `/newbot` 명령어를 전송함
3. 봇의 이름(Display Name)과 사용자 이름(Username, 반드시 `bot`으로 끝나야 함)을 입력함
4. BotFather가 발급해 준 **HTTP API 토큰**(`123456789:ABC...`)을 복사함
5. (선택 사항) 그룹이나 보안을 위해 BotFather에게 `/setprivacy`를 보내 값을 `off`로 설정해 주면 그룹 메시지도 잘 인식함

---

## 2단계: Hermes Agent 설치 및 환경 설정

PowerShell을 관리자 화면으로 열고 아래 순서대로 진행함
window키 -> PowerShell 선택

### Hermes Agent 사이트
https://hermes-agent.nousresearch.com

### 1. Hermes Agent 설치

아직 설치하지 않으셨다면 npm 또는 공식 스크립트를 통해 설치할 수 있음

```powershell
# Windows (PowerShell) 환경에서의 공식 설치 명령어입니다.
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

### 2. 환경 변수 구성

Hermes가 생성하는 설정 디렉터리(보통 `~/.hermes/.env`) 또는 현재 환경 변수에 발급받은 키들을 등록해야함

```bash
# Gemini API 키 등록 (Hermes 네이티브 어댑터가 자동 인식)
export GEMINI_API_KEY="여러분의_구글_제미나이_API_키"

# 텔레그램 토큰 등록
export TELEGRAM_BOT_TOKEN="여러분의_텔레그램_봇_토큰"

```

*보안을 위해 본인의 텔레그램 계정 ID로만 접근을 제한하고 싶다면 `ALLOWED_TELEGRAM_USERS="본인_유저_ID"` 형태의 설정을 `.env` 파일에 추가하는 것을 권장함 
(유저 ID는 텔레그램에서 `@userinfobot`을 통해 쉽게 확인할 수 있습니다.)*

---

## 3단계: 제공업체(Provider) 및 모델 설정

- Hermes CLI를 실행하여 기본 언어 모델을 Gemini로 지정함 
- Hermes는 최신 **Gemini 3** 모델들을 기본적으로 잘 지원함

```bash
# 기본 제공업체를 gemini로 설정하고 모델을 지정합니다.
hermes model set gemini gemini-3-flash-preview

```

> **Tip:** 비용 효율성과 속도를 고려할 때 `gemini-3-flash-preview`나 `gemini-1.5-flash` 모델을 추천함

---

## 4단계: 게이트웨이 실행 및 테스트

모든 설정이 끝났다면 텔레그램 게이트웨이를 활성화하여 에이전트를 구동함

```bash
hermes gateway start --platform telegram

```

서버가 정상적으로 구동되면, 스마트폰이나 PC의 텔레그램 앱에서 앞서 만드신 봇 채널로 들어가 아무 메시지나 보내봄

헤르메스 에이전트가 Gemini API를 사용해 답변을 생성하고, 파일 시스템 접근이나 웹 스크랩 등의 도구(Skills)가 필요할 때 스스로 판단하여 작업을 수행한 뒤 텔레그램 메시지로 결과를 보내줄 것임