# 설치 상태·수학 MCP 복구 검증 — 2026-11-05

## 사용자 전달 관측과 미확정 원인

Cofa Probe의 Codex 답변을 사용자가 전달했다. 아래는 유지보수자가 직접 관측한 로그가 아니다.

- 사용자 터미널 설치 성공, 역할 13개·Skill 4개 확인, 현재 세션의 Skill 4개 인식.
- 에이전트의 `.codex`·`.agents` 쓰기 제한을 환경 전체 설치 불가로 확대했던 설명 오류.
- SymPy MCP: SDK/FastMCP 호환·버전 교체 잔여 파일 문제를 수정한 뒤 로컬 SDK 방정식 호출·대입 통과.
- mcp-solver: 내부 Python MCP 서버 초기화 시간 초과. 최소 비동기 스레드 작업의 멈춤도 보고됨.
- 훅 모의 검사 6개 통과; 정상 신뢰·실제 Codex 이벤트 실행은 미검증.
- 두 MCP 모두 당시 Codex 도구로 연결된 상태는 아니었음.

체험이 끝나 실행 명령·정확한 버전·오류 로그·최소 재현 코드를 회수하지 못했다.
**Cofa Probe의 멈춤 원인은 확정하지 못했고, 수정본의 Cofa Probe 실행 성공도 확인하지 못했다.**
의존성 혼합을 피하는 설치 경로를 구현했고 macOS/Linux에서 동작을 검증했다.
로컬 성공을 당시 장애의 인과적 해결 증거로 바꾸지 않는다.

## 변경

- 설치기가 파일 자체 검사를 실행하고 `installation-status.json`을 갱신한다.
  doctor는 앱 테스트·쓰기 없이 파일·역할·Skill을 점검한다. 과제 슬롯과 기존 설정은 보존한다.
- 과거 설치 대기 기록보다 최신 파일 관측을 우선하고, 에이전트 제한과 정상 사용자 터미널을 구분한다.
- 선택형 SymPy/solver 설치기: 새 전용 venv, 주요 의존성 버전 지정, pip check, 합성 계산 검증,
  검증 이후 프로젝트 MCP 등록. 다른 설정·전역 Python·신뢰/승인 정책은 변경하지 않는다.
- 같은 이름의 기존 MCP 설정이 다르면 보존하고 중단한다. 불완전 설치는 연결 성공으로 등록하지 않는다.
  재검사 실패는 이전 성공 상태를 무효화한다. 계산 성공 후 등록만 실패하면 등록 단계만 재개할 수 있다.
- solver는 고정 소스의 v4 및 같은 커밋의 minion을 사용한다. 잘못된 동명 PyPI 패키지를 피하고,
  전용 uv·소스 경로·Python 경로를 명시한다. 실행 중 backend의 모든 간접 의존성이 고정된 것은 아니다.
- 스레드 / asyncio / AnyIO / 내부 엔진 / 외부 솔버·Z3를 각각 진단하고 제한 시간·스택을 남긴다.
- MCP만 제한되고 로컬 계산은 허용되면 설치한 SymPy/Z3를 직접 호출한다. mcp-optimizer는 계속 제외한다.

## 실제 실행

| 환경 | 검사 | 결과 |
| --- | --- | --- |
| macOS arm64, Python 3.13.14 | 새 SymPy venv·pip check·직접 SymPy/Z3·SDK 방정식 호출 | 통과: 해 2,3, 잔차 0,0; 모순 제약 unsat |
| macOS arm64, Python 3.13.14 | 새 solver 소스/venv·3종 스레드·내부 엔진·외부 solver·Z3·submit_code | 통과 |
| Linux x86-64, Python 3.13.18, 일반 사용자 runner | 동일 설치기 새 설치·두 MCP 계산·프로젝트 등록·재검사 | 통과 |
| Linux, `.codex`·`.agents` 파일시스템 쓰기 제거 후 | `harness.py doctor` | 파일 검사 통과; runtime 상태는 미확인 유지 |
| macOS, 등록된 실제 command/args를 SDK로 실행 | 두 launcher 초기화·도구 목록, SymPy 호출 | 통과; Codex 네이티브 호출은 아님 |
| 유지보수 테스트 | 기존 보존·훅·역할 검사 + doctor·MCP 상태/설정/타임아웃 회귀 | 53개 통과 |

Linux는 macOS OrbStack의 amd64 에뮬레이션 컨테이너이며 Cofa Probe 복제 환경이 아니다.
이미지는 `python:3.13-slim`, manifest digest
`sha256:ae14d4ce8771606477a81446e7ef429edd6762305fc50c84507c1041fa8285d1`,
실행 image ID `sha256:bdfc738a8a869292ec1b01f1b8e620db533e09d1fe68fe980a7118b22dae9cec`다.
Git·Python·venv와 패키지 취득이 가능한 컨테이너를 준비한 뒤 일반 사용자로 설치했다.
플랫폼 승인 정책·Codex UI·훅 신뢰·실제 이벤트는 이 검사로 검증하지 않았다.
원자료는 [구조화 결과](setup-repair-2026-11-05.json)에 있다. 개인 경로는 `<task>`로 치환했다.

이번 리허설 중 새 probe가 `select_backend`의 일반 텍스트 응답을 JSON으로만 파싱해 실패했다.
응답 형식 처리를 수정하고 재실행해 통과했다. 이 구현 중 오류는 Cofa의 초기화 장애와 별개다.

## 다음 Cofa Probe에서

[README](../README.md)와 [설치 절차](../template/.harness/math-setup.md)의 명령을 사용한다.
정상 설치본은 doctor/check부터 이어간다. fresh 환경에서도 스레드 단계가 멈추면
동일 패키지를 반복 재설치하거나 바깥 서버 시간 제한만 늘리지 않는다. 남은 로그로 런타임 문제를
판단해야 하며, 현재 허용된 직접 라이브러리 호출의 성공/실패를 별도로 기록한다.
Codex의 실제 도구 호출과 실제 훅 이벤트는 현장에서 추가로 확인해야 한다.

참조: [MCP 프로젝트 설정](https://developers.openai.com/codex/mcp),
[upstream solver 초기화 소스](https://github.com/szeider/mcp-solver/blob/24b7d6fb1d5e361eeb8558b6119ca8e8cb083a3a/src/mcp_solver/agent/mcp_server.py),
[upstream 설치 조건](https://github.com/szeider/mcp-solver/blob/24b7d6fb1d5e361eeb8558b6119ca8e8cb083a3a/INSTALL.md).
