# Cofa Probe 수학 도구 설치·연결 절차

기본 하네스 설치와 수학 패키지 설치는 별개다. 아래 명령은 **하네스가 설치된 실제 과제 루트**에서,
환경이 허용하는 사용자 터미널 또는 에이전트 셸로 실행한다. 개인 서버·AI 키를 쓰지 않는다.
에이전트가 `.codex`를 못 써도 사용자 터미널이 설치에 성공했다면 현재 파일 검사부터 이어간다.

## 1. 하네스 파일 확인

```bash
python3 -B .harness/harness.py doctor
```

역할 13개·Skill 4개 등 파일 설치 검사다. 앱 테스트가 없어도 수행한다.
Skill 자동 인식, 독립 역할 실행, 훅 신뢰·자동 콜백은 별도 상태다.

## 2. SymPy MCP와 직접 호출용 SymPy·Z3

Python 3.11 이상인 **실제 설치된 인터프리터**를 사용한다. 아래 python3의 버전부터 확인한다.

```bash
python3 --version
python3 -B .harness/math_setup.py install --register
```

- 전용 venv 생성 → 고정 패키지 설치 → `pip check` → 직접 SymPy/Z3 계산 →
  SDK stdio 초기화·도구 목록·방정식 호출·원식 대입 → 프로젝트 MCP 설정 등록.
- `mcp-sympy 0.1.0 / mcp 1.30.0 / fastmcp 3.4.11 / anyio 4.16.0 / sympy 1.14.0`을 사용한다.
  기존 전역 환경에서 버전을 덮어 설치하지 않는다. 하위 의존성은 실제 설치 목록으로 기록한다.
- 정상 설치가 있으면 재사용·재검사한다. 패키지 잔재/혼합 설치가 의심될 때는 같은 명령에
  `--fresh`를 붙여 **새 환경**을 만든다. 기존 환경을 지우거나 제자리 다운그레이드하지 않는다.
- 설치 결과는 `.harness/work/math-tools/latest-check.json`, 선택한 Python은 `selected.json`에 있다.
  라이브러리 직접 호출 시 그 Python 경로를 사용한다. venv의 Python 심볼릭 링크를 resolve하지 않는다.

## 3. mcp-solver 설치와 초기화 원인 분리

이 서버 v4에는 **Python 3.13 또는 3.14**가 필요하다. `python3 --version`이 해당 범위면 그대로,
아니면 환경에 설치·허용된 `python3.13` 또는 `python3.14`로 아래 명령을 실행한다.
없는 인터프리터를 있다고 가정하지 않는다. OS 패키지 관리자·sudo로 권한을 변경하지 않는다.

```bash
python3.13 -B .harness/solver_setup.py install --register
```

- 검사한 upstream 커밋 `24b7d6fb1d5e361eeb8558b6119ca8e8cb083a3a`를 새 경로에 checkout하고
  해당 소스와 같은 커밋의 mcp-minion을 전용 venv에 설치한다. 동명 PyPI mcp-solver를 설치하지 않는다.
- SDK 1.30.0, AnyIO 4.16.0, agentic-python-coder 3.4.3, uv 0.11.21을 지정한다.
  uv도 전용 venv에 설치하므로 시스템 uv가 필요 없다. Git·패키지 취득 네트워크·쓰기 공간은 필요하다.
- 기본 스레드 → asyncio 스레드 → AnyIO 스레드 → 내부 IPython MCP 초기화 →
  외부 solver 초기화·Z3 실행·불가능 조건 재검산·submit_code 순서로 검사한다.
- 각 단계에 시간 제한이 있다. 멈추면 해당 단계·버전·스택을
  `.harness/work/solver-tools/latest-check.json`에 남기며 성공으로 등록하지 않는다.
- `MCP_SOLVER_DEV`는 해당 소스 checkout, PATH는 해당 venv를 사용한다.
  인터프리터 자동 다운로드는 끈다. 커널은 같은 Python을 사용하며 필요한 백엔드 패키지는
  upstream의 uv 경로로 취득한다. backend 의존성 전체가 고정됐다고 주장하지 않는다.

이미 설치됐다면 `install` 대신 `check --register`로 다시 검사한다. 패키지 환경 문제라면
`install --fresh --register`를 사용하되, 같은 실패를 반복하지 말고 아래 표의 단계부터 판단한다.

| 실패 지점 | 의미와 다음 조치 |
| --- | --- |
| Python 버전·venv·pip·소스 취득 | 메시지에 나온 선행 조건 해결. 구버전 Python에서 solver v4를 강제로 실행하지 않음 |
| thread / asyncio-thread / anyio-thread | MCP 프로토콜 전에 실패. 기록된 Python·AnyIO·스택 확인; 설치 혼합은 fresh 환경으로 재검사. fresh에서도 실패하면 런타임 문제로 남기고 플랫폼 지원 필요 |
| engine | 내부 `agentic_python_coder.mcp_server` 초기화 실패. 외부 solver의 timeout만 늘려 숨기지 않음 |
| solver | 내부 엔진은 성공. 외부 초기화·backend 취득·커널·계산 오류를 해당 로그로 분리 |
| 등록 | 계산 성공과 설정 파일 쓰기 실패 분리. 정상 사용자 터미널에서 `register`만 이어갈 수 있음 |
| Codex 도구 미노출·승인 제한 | 아래 현재 세션 확인. 승인·신뢰·sandbox를 강제로 변경하지 않음 |

## 4. 현재 Codex 세션에서 연결 확인

등록은 프로젝트 `.codex/config.toml`에 `kty_math_sympy` / `kty_math_solver` 항목을 추가한다.
기존 모델·effort·보안 설정과 다른 MCP는 보존한다. 같은 이름의 다른 설정은 덮어쓰지 않는다.
프로젝트 설정을 지원·신뢰하는 환경인지 확인한다. 필요하면 제공 UI의 정상 재연결/새 세션을 사용한다.

Codex에 **“등록 파일만 보지 말고 현재 도구 목록에서 해당 서버를 확인하고, 노출된 실제 MCP 도구로
합성 방정식 또는 모순 제약을 호출해 결과를 검산해. 실패하면 SDK 성공과 구분해 기록해”**라고 요청한다.
로컬 SDK 성공은 Codex가 MCP를 썼다는 증거가 아니다. /hooks 신뢰·실제 이벤트도 별도로 확인한다.
프로젝트 설정 형식 근거: [OpenAI 공식 MCP 문서](https://developers.openai.com/codex/mcp).

## 5. MCP 전용 제한일 때 직접 계산

로컬 계산이 별도로 허용되어 있다면 `math_setup.py`가 설치한 SymPy/Z3를 직접 import한다.
MCP를 시험하지 않고 라이브러리만 설치해야 할 때:

```bash
python3 -B .harness/math_setup.py install --direct-only
```

이를 MCP 차단 우회 프록시로 쓰지 않는다. 계산·프로세스 자체가 금지되면 실행하지 않는다.
실제 문제는 원래 제약을 재검산하고 기존 Sol A/B 검수로 이어간다. mcp-optimizer는 제외한다.

## 확인 범위

2026-11-05 사용자 전달 보고: 터미널 하네스 설치 및 Skill 4개 인식, SymPy 로컬 SDK 성공,
solver 내부 초기화 시간 초과·최소 비동기 스레드 멈춤, 모의 훅 6개 통과.
당시 버전·로그·최소 코드는 체험 종료로 회수 불가다. 원인 확정·Cofa Probe 해결 완료로 기록하지 않는다.
이 설치기는 새 전용 환경으로 의존성 혼합을 피하고 각 초기화 층을 검사한다.
현재 환경에서 통과한 단계만 완료 처리한다. 과제 데이터·로그를 외부로 보내지 않는다.
