# KTY Codex Harness Template

Codex와 **GPT 6.1 Sol (`gpt-6.1-sol`, `xhigh`)** 중심의 개발 하네스다.
기존 개인 하네스의 프로필·공학 원칙·계획 검증·코드 검수·설명·완료 감사를
Codex의 `AGENTS.md`, 저장소 Skill, 네이티브 훅으로 이식했다.

현재는 **사전 체험 전의 기반 버전**이다. 시험 플랫폼의 Codex 버전·허용 설정·
Skill 발견·훅 지원 여부는 실제 체험에서 확인하고 보완한다.

## 설치와 실행

Linux·macOS의 Python 3.9 이상, Git, 제공 환경의 Codex가 필요하다.
외부 Python 패키지나 별도 AI API 키·구독은 필요 없다.
패키지는 작업 공간 바깥에 clone하고, 기존 과제 Git 저장소 루트에 설치한다.

```bash
git clone https://github.com/xodbs1021/kty-codex-harness-template.git /tmp/kty-codex-harness
bash /tmp/kty-codex-harness/install.sh /path/to/task-workspace
cd /path/to/task-workspace
bash .harness/codex.sh
```

실행기는 모델·추론 강도를 명시한다. Codex는 `.codex/agents/`에서 네이티브 역할을 발견한다.
메인은 제공된 인증·승인·샌드박스·연결 설정을 상속한다.
기존 `.codex/config.toml`이 있으면 보존한다. 직접 `codex`로 실행했을 때 기존 설정이
다른 모델을 고를 수 있으므로 이 하네스의 실행기를 사용하고 `/status`에서 확인한다.
필요하면 요청문 하나를 인자로 전달한다.

```bash
bash .harness/codex.sh 'README와 하네스를 읽고 필수 요구사항부터 구현해줘'
```

설치기는 기존 `AGENTS.md`에 관리 블록만 추가하고 기존 훅과 함께 두 이벤트를 등록한다.
프로필·검증 명령은 재설치 시 보존한다. 관리 파일의 로컬 수정은 덮어쓰지 않고 중단한다.
훅을 추가하지 않는 환경에서는 `install.sh /path/to/workspace --no-hooks`를 사용한다.
이 옵션은 기존 훅을 끄거나 삭제하지 않는다.

## 프로젝트 설정

`.harness/project-profile.md`에 목표·스택·불변식·경계·실행 방법·제출물을 채운다.
실제 검증 명령은 `.harness/checks.json` 한 곳에 배열로 등록한다.
아래는 형식 예시다. 과제의 실제 명령으로 바꾼다.

```json
{
  "checks": [
    {"name": "test", "argv": ["npm", "test"], "timeout_seconds": 120},
    {"name": "build", "argv": ["npm", "run", "build"], "timeout_seconds": 120}
  ]
}
```

```bash
python3 .harness/harness.py verify
```

빈 명령·실패·시간 초과·실행 파일 부재는 실패다. 검증 중 코드가 바뀌어도 실패다.
검증은 루트에서 명령을 직접 실행하며 셸 문법을 자동 해석하지 않는다.
출력은 현재 터미널에 남고 종료 코드·시간·코드 지문은 `.harness/state/`에 저장된다.
진행·계획·검수 기록은 `.harness/work/`에 남긴다. 두 폴더는 Git에서 제외한다.
시험 플랫폼이 작업 파일 전체를 수집할 수 있으므로 Git 제외를 제출 제외로 해석하지 않는다.

## ECC 적용

[ECC의 Codex 구성](https://github.com/affaan-m/everything-claude-code/tree/25278e7d7b6cf6e6a4e7a6c8e10f14ff22f0eb5b/.codex)을 확인했다.
필요한 공개 코딩·테스트·보안 규칙만 고정 버전으로 포함하고 Skill에서 선택해 읽는다.
원문의 전체 플러그인·전역 동기화·외부 MCP 설정은 설치하지 않는다.
테스트 종류·커버리지 목표는 프로젝트 위험과 과제 요구에 맞춰 적용한다.
출처·라이선스와 원본 대비 변경은 [PROVENANCE.md](PROVENANCE.md)에 있다.

## 검증 게이트와 한계

현재 Codex는 [저장소 Skill](https://learn.chatgpt.com/docs/build-skills)과
[네이티브 훅](https://learn.chatgpt.com/docs/hooks)을 지원한다.
프로젝트 신뢰와 별개로 `/hooks`에서 추가된 훅을 검토·신뢰해야 실행된다.
플랫폼이 훅을 허용하지 않으면 명시적 `verify` 절차를 따른다.
설정 파일 파싱 성공만으로 활성화를 판단하지 않는다. `--ignore-user-config`는
프로젝트 신뢰 정보도 제외할 수 있으므로 실제 훅 검증에 사용하지 않는다.

- SessionStart는 세션별 코드 기준 지문을 저장한다. 재개·컨텍스트 압축 때 보존한다.
- Stop은 세션 시작 이후 변경된 파일에 최신 검증 성공 기록이 있는지 확인한다.
- 검증 누락 시 한 번 이어서 검증을 요청한다. 계속 불가능하면 경고를 남기며
  세션 종료를 무한 차단하지 않는다. 이 경우 검증 미완료 상태다.
- 코드 지문은 Git이 추적하는 파일(삭제 포함)과 무시되지 않은 새 파일을 포함한다.
  `.harness/state/`, `.harness/work/`는 제외한다. 무시된 생성물과 외부 상태는 검증하지 않는다.
- 훅은 명령 종료 코드와 파일 동일성을 확인한다. 테스트 적정성·요구 충족·
  독립 리뷰·사용자 이해·제출 성공은 역할별 검수와 실제 확인이 필요하다.
- `.codex/agents/`에 planner·developer·reviewer·auditor 네이티브 역할을 제공한다.
  모두 `gpt-6.1-sol / xhigh`이고 planner·reviewer·auditor는 파일을 수정하지 않도록 지시한다.
  각 파일에 이름·설명·지침을 선언한다. 프로젝트 신뢰가 필요하며 기존 설정 파일을 보존한다.
  멀티에이전트 기능 자체를 강제로 켜지 않는다.
- 환경이 지원·허용하면 검증 역할을 별도 컨텍스트에 위임한다.
  지원하지 않으면 제한을 밝히고 같은 세션에서 수행한다. 실제 독립 컨텍스트가 없으면
  독립 리뷰라고 주장하지 않는다. 원본의 이종 모델 듀얼 리뷰와는 보장 범위가 다르다.
- 네이티브 자식의 실제 권한은 부모에게서 상속된다. 역할 파일에 `sandbox_mode`를 적어도
  별도 쓰기 차단을 보장하지 않는다. 강제 읽기 전용 검수는
  `python3 .harness/harness.py review '검수 요청'`, 완료 감사는
  `python3 .harness/harness.py audit '감사 요청'`으로 실행한다.
  이 명령은 별도 Codex 프로세스 전체를 `--sandbox read-only`로 실행한다.

## 시험 운영

과제 안내·현재 사용자 지시·플랫폼 규칙이 우선한다.
공개 도구 반입은 플랫폼 안에서 진행하고, 시험 문제·파일·결과를 외부로 보내거나
push·PR·게시하지 않는다. 외부 모델·개인 키·본시험 Computer Use는 사용하지 않는다.
허용된 사전 체험 환경 분석은 별도 안내에 맞춰 수행한다.
계획·협업 문서는 제공 Codex와 작성하되 후속 서술형은 응시자가 직접 답한다.

## 개발 검증

```bash
python3 -m unittest discover -s tests -v
```

설치·재설치·충돌 보존·심볼릭 링크 거부·검증 실패·시간 초과·코드 변경 후 무효화·
세션 격리·모델 인자 전달을 별도 임시 Git 저장소에서 검증한다.
이 저장소의 통과와 시험 플랫폼 호환성 확인은 별개다.
