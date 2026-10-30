# KTY Codex Harness — SK하이닉스 AI 해커톤 2026

제공 Codex에서 사용하는 해커톤 전용 하네스다. 메인·독립 검수는 `gpt-6.1-sol`,
effort는 실제 환경 설정을 따른다. 13개 역할, Google API 설계·코드 스타일·글쓰기 스킬,
검증 보조 훅, 반도체 지식 65개를 포함한다.

## 바로 시작

제공 Codex에 다음처럼 요청한다.

> GitHub xodbs1021의 kty-codex-harness-template을 찾아 README대로 하네스를 적용하고
> 이 과제를 해결해줘. 설치가 막히면 직접 읽기 방식으로 이어가고, 현재 권한에서
> 불가능한 작업과 실제로 검증하지 못한 항목은 구분해서 알려줘.

**“설치해줘”만 요청하면 설치·설정·검증까지다.** 기능 구현은 과제 해결도 요청했을 때 시작한다.
이 요청문은 권한을 바꾸지 않는다. 현재 과제 안내·플랫폼 규칙과 실제 권한을 따른다.

## 제공 Codex의 적용 순서

1.  **경로 확인:** 반입 패키지와 실제 과제 Git 루트를 구분한다.
    기존 README·AGENTS·진행 기록을 먼저 읽고, 과제에 임의 `git init`하지 않는다.
2.  **설치 가능:** 확인한 경로로 아래 설치기를 실행하고 곧바로
    [setup.md](template/.harness/setup.md)를 읽어 설정·검증·두 독립 리뷰까지 잇는다.
    파일 복사만으로 적용 완료라고 하지 않는다.
3.  **설치 불가:** [read-only.md](template/.harness/read-only.md)에 따라 반입본
    `template/`의 프로필·원칙·Skill을 직접 읽는다. 허용된 검사·독립 리뷰·설명·감사를
    이어가며, 전체 읽기 전용이면 설치·수정·저장·검증 영수증을 만들지 않는다.
4.  **실제 과제에 맞추기:** 요구·스택·실행·테스트·제출 조건은 현재 과제에서 확인한다.
    프로필·checks·근거를 허용된 곳에 기록한다. 기존 과제 사실은 보존한다.
5.  **활성화 확인:** 현재 모델·Skill·역할·훅의 실제 상태를 구분한다.
    새 세션·정상 신뢰가 필요하면 가능한 일을 먼저 끝내고 다음 조치만 안내한다.
    단계별 요청이 필요하면 [상세 설치 절차](docs/usage.md)를 따른다.

쓰기와 도구 사용이 허용된 환경에서 실행하는 설치 명령이다. 경로는 실제 값으로 바꾼다.

```bash
bash <반입한-패키지>/install.sh <실제-과제-Git-루트>
```

전체 설치는 Bash·Python 3.9 이상·Git·제공 Codex를 사용한다.
Python 외부 패키지·개인 AI 키는 필요 없다. 작업 공간 밖 clone은 필수가 아니다.
새 세션이 필요하고 제공 CLI가 지원하면 사용자가 과제 루트에서 실행한다.

```bash
bash .harness/codex.sh
```

재설치 시 기존 프로필·검증 명령·근거·설정 진행은 보존한다.
반입본만 `git pull --ff-only`한 뒤 설치 파일이 바뀌었다면 다시 설치하고 보존 슬롯의
필요한 차이를 병합한다. 패키지 pull만으로 과제 설치본이 갱신되지는 않는다.

## 설계한 작업 흐름

명료화 → 필요 시 조사·독립 평가 → 설계·계획과 각각 Sol A/B 검토 → 구현·검사 →
Sol A/B 코드 검수와 조건부 보안·테스트 검토 → 설명 → 완료 감사.

필요한 역할마다 새 컨텍스트를 쓰고 첫 리뷰끼리 결론을 공유하지 않는다.
독립 호출이 없으면 대체 검수라고 밝힌다. 작은 작업에 불필요한 역할을 전부 실행하지 않는다.
실행 계약은 [workflow.md](template/.agents/skills/kty-harness/references/workflow.md)가 정본이다.

- 코드·문서 작성/검수: [Google 스타일 Skill](template/.agents/skills/google-styleguide/SKILL.md). Python·Java·Go 원문 포함.
- API 설계·리뷰: [Google API Skill](template/.agents/skills/google-api-design/SKILL.md)의 관련 AIP 원문을 직접 읽고 계약·검증에 연결한다.
- 사용자 설명·문장 품질: [readable-writing](template/.agents/skills/readable-writing/SKILL.md).
- 결정·진행·반복 지적: [기록 계약](template/.agents/skills/kty-harness/references/decision-memory.md).
- 서비스 과제: 구현뿐 아니라 실행·연결·응답을 검증한다. 주소·포트·스택은 고정하지 않는다.
  [과제 적용 기준](template/.agents/skills/kty-harness/references/probe-workflow.md)을 따른다.

## 검증과 한계

실제 과제 검사는 `.harness/checks.json`에 등록한다. 쓰기 가능할 때 다음을 실행한다.

```bash
python3 .harness/harness.py verify
```

verify는 Go 포맷 검사와 실제 과제 검사를 실행한다. 다른 언어의 스타일 전체를 자동 검사하지 않는다.
도구 부재·실행 실패는 미검증/실패로 남긴다. 읽기 전용에서는 영수증 없이 허용된 검사를 직접 한다.
SessionStart·Stop은 최신 검증 기록을 확인하는 보조 장치다.
원본 Claude의 모든 가드나 13개 역할 실행·이해·실제 제출을 강제하는 장치는 아니다.

**실제 Probe는 현재 접근·구성 확인이 불가능해 로컬에서 검증할 수 없다.**
로컬 합성 과제의 통과를 시험환경 설치·훅·저장·제출 성공으로 확대하지 않는다.
시험 문제·파일·코드·로그·결과는 외부 AI·MCP·GitHub·개인 vault로 보내지 않는다.
후속 서술형 단계에서는 AI 지원을 종료한다.

## 필요한 자료만 읽기

| 목적 | 문서 |
| --- | --- |
| 설치·승인·읽기 전용·CLI 상세 | [설치·운영 가이드](docs/usage.md) |
| 반도체 개념 65개와 검색 | [지식 패키지](knowledge/semiconductor/README.md) |
| 지식을 실제 문제에 적용 | [적용 가이드](knowledge/semiconductor/application-playbook.md) |
| 사전체험 진단 | [15분 실행표](docs/practice-runbook.md) |
| 원본 구성 파일별 대응·차이 | [구성 대조와 최신 검증](docs/component-parity-2026-10-31.md) |
| 이전 역할 복원·검증 | [역할 대응표](docs/claude-parity.md), [검증 기록](VALIDATION.md) |
| 출처·라이선스 | [PROVENANCE.md](PROVENANCE.md) |

유지보수 검사는 `python3 -m unittest discover -s tests -v`로 실행한다.
관리자: [xodbs1021](https://github.com/xodbs1021).
