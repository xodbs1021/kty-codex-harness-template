---
name: kty-harness
description: Codex 개발 하네스. 기능 구현·수정·계획·검수, 관련 레퍼런스 조사, 실제 변경 설명과 구조의 설계 의도 설명에 사용한다. 단순 사실 조회는 직접 답한다.
---

# Codex 개발 하네스

메인은 제공 Codex의 `gpt-6.1-sol`이다. effort는 고정하지 않고 허용된 실제 설정을 따른다.
작업 전 `.harness/project-profile.md`, `.harness/principles.md`를 읽고 진행 중이면
`.harness/work/progress.md`와 기존 문답·검토 결과부터 복구한다.
설치본이 없으면 반입 저장소 `template/`의 대응 문서를 직접 읽고 실제 과제 경로를 따로 확인한다.
전체 읽기 전용이면 `.harness/read-only.md` 또는 반입본의 동일 문서를 함께 적용한다.
코드·문서 작성 및 검수 전에 `../google-styleguide/SKILL.md`와 해당 언어 원문을 읽는다.
사용자 대면 글·설명은 `../readable-writing/SKILL.md`도 적용한다.
둘 다 이 패키지에 포함된 Skill이며 자동 등록 실패 시 직접 읽는다.
새 작업의 초기 실행은 [decision-memory.md](references/decision-memory.md)에 따라
이미 반입된 기준본 대조와 과제 내부의 유사 작업 이력 회수를 한 번 수행한다.

## 오케스트레이션

**[workflow.md](references/workflow.md)가 호출 순서와 되돌림의 정본이다.**
역할 이름을 언급하는 것과 실제 별도 컨텍스트 호출·완료를 구분한다.

- 개발 요청: clarifier → 조사 필요 판단 → 필요 시 collector·evaluator → 설계/계획·별도 검토 →
  구현·실제 검사 → Sol A/B와 조건부 보안·테스트 검토 → 변경 설명 전달 → 완료 감사.
- 계획만 요청은 계획 A/B 검토까지, 검수만 요청은 해당 게이트의 A/B·조건부 검토까지 수행한다.
  부분 재실행은 기존 근거를 확인하고 필요한 단계만 재개한다. 요청 없이 구현으로 확대하지 않는다.
- 조사·비교 요청: [research.md](references/research.md)의 수집 → 독립 원문 평가 → 메인 종합.
- 변경 설명 요청: [explanation.md](references/explanation.md)의 `kty_change_explainer`.
- 구조·설계 이유 질문: 같은 문서의 `kty_architecture_guide`. 개발 파이프라인을 새로 돌리지 않는다.
- 설치·설정 요청: `.harness/setup.md`. 실제 과제 구현까지 완료했다고 보고하지 않는다.

사용 가능한 독립 역할을 호출한다. 이름이 미등록이면 해당 역할 TOML과 관련 reference를 제공 도구에
직접 전달한다. 독립 호출 자체가 없으면 메인이 순차 수행하고 **독립 실행 미수행**을 명시한다.
필요한 역할은 각각 새 컨텍스트로 호출하며, 지원되는 도구에서는 `fork_turns="none"`을 명시한다.
명료화·계획·개발을 한 자식에 합치거나 역할을 바꿔 재사용하지 않는다. 상세 호출·실패 계약은 workflow.md를 따른다.
명료화의 질문은 메인이 사용자에게 전달한다. 기존 결정·명시적 승인을 되묻지 않는다.
조사에서는 채택된 근거만 설계에 연결하고 조사 불요·실패도 이유를 남긴다.
계획 작성자와 검토자를 분리하며 설계·계획 각 검토도 Sol A/B로 수행한다. 구조적 변경은 두 pass를 구분한다.

## 역할과 입력

전체 역할·A/B·보안·테스트 계약은 [roles.md](references/roles.md)에 있다.
공통 입력은 실제 요구·관련 코드/데이터 경로·프로필·원칙·허용 작업·성공 조건·선행 근거다.
자식은 다른 에이전트를 생성하지 않는다. 메인이 호출·응답·지적 처리·진행을 관리한다.
네이티브 역할은 `.codex/agents/`에 있으며 모두 Sol이고 effort를 덮어쓰지 않는다.
자식은 부모의 실제 권한을 상속한다. 수정 금지 지침과 기술적 읽기 전용 격리를 혼동하지 않는다.
설치본과 제공 CLI를 허용된 범위에서 사용할 때 읽기 전용 역할을 별도 프로세스로 실행할 수 있다:

```bash
python3 .harness/harness.py role clarifier '실제 요청·과제 경로·선행 결정'
python3 .harness/harness.py role research-collector '공개 개념으로 정리한 조사 범위'
python3 .harness/harness.py role research-evaluator '수집 결과와 원문 위치'
python3 .harness/harness.py role plan-reviewer '검토할 계획·실제 코드·판정 기준'
python3 .harness/harness.py review '리뷰 A 또는 B의 실제 대상·판정 기준'
python3 .harness/harness.py role change-explainer '실제 변경 범위·검증 결과'
python3 .harness/harness.py audit '완료 주장과 단계별 실제 근거'
```

각 호출은 새 CLI이며 `--sandbox read-only`를 적용한다. 구현은 허용된 메인/developer에서 한다.
개인 인증·외부 AI를 연결하지 않는다. CLI 미지원이면 위 독립 도구/문서형 경로를 따른다.
명령을 안내한 것만으로 실행 완료로 처리하지 않는다.

## 구현·검수·완료

- 단계별 진행, 중요한 결정 기록, 반복 지적, 설치본 차이는
  [decision-memory.md](references/decision-memory.md)를 따른다. 과제 내부만 사용한다.
- [ECC 기준](references/ecc-quality.md)을 관련 단계에서 읽는다. 실제 사용한 TDD·디버깅 방법을 기록하고
  설치되지 않은 Claude·ECC·superpowers 플러그인을 호출했다고 주장하지 않는다.
- 실제 검증 명령은 `.harness/checks.json`의 argv 배열로 등록하고 `harness.py verify`를 실행한다.
  쓰기가 제한되면 read-only.md의 직접 검사 경로로 진행한다. 빈 검사·미실행은 통과가 아니다.
- A/B는 같은 상태를 서로의 첫 결론 없이 검토한다. 새로 수정했으면 필요한 검사·검토를 다시 수행한다.
- 조건부 security-reviewer·test-analyzer, 한쪽에만 있는 고위험 지적의 교차 검증을 workflow대로 수행한다.
  [계획 게이트](references/plan-gates.md)와 [교차 검증 계약](references/cross-verification.md)의 단계별 적용 범위·의존 해시·
  기각 재사용 조건·같은 결함 유형 확인을 적용한다.
- 변경 설명은 실제 diff와 검사 결과로 작성해 사용자에게 전달한 뒤 완료 감사한다.
  최종 감사는 명료화·조사·계획 검토·검수·설명 근거가 빠진 사실도 확인한다.
- 각 단계의 수행·불요·미실행과 이유를 남긴다. 제약을 감추거나 횟수를 채워 통과시키지 않는다.

## Probe 요구와 시간

실무 평가 과제는 [probe-workflow.md](references/probe-workflow.md)를 적용한다.
요구·결정 출처·구현 위치·실제 결과를 `.harness/task-evidence.md`에 연결한다.
업무 의미는 제공 업무 담당자, 화면·도구·제출 절차는 Helper에 확인한다.
사용자의 결정과 AI 제안, AI 검사와 응시자의 화면 확인·이해를 구분한다.
필수 동작을 먼저 완성하고 마지막 10분은 검증·문서·저장·제출 확인에 남긴다.
작업 시간에 결과·이유·대안·한계를 설명하며 후속 서술형에서는 AI 지원을 종료한다.

## 시험 환경과 훅

공개 도구는 제공 환경 안에서 가져온다. 문제·파일·작업 결과를 외부로 보내거나 push·PR·게시하지 않는다.
개인 API 키·외부 AI·Claude 실행 의존성은 없다. 감독·보안·연결 설정을 유지하고 차단은 정상 지원 절차로 확인한다.
본시험 브라우저·컴퓨터 자동 조작을 하지 않는다. 사전체험은 별도 허용 범위를 따른다.

SessionStart·Stop 훅은 설치·신뢰된 환경에서 변경 후 최신 검증 누락을 알리는 보조 장치다.
명료화·조사·설명·독립 검수까지 강제하지 않는다. 훅 미지원이어도 위 직접 실행 절차를 유지한다.
