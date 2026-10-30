# KTY Codex Harness — SK하이닉스 AI 해커톤 2026

Codex와 **GPT 6.1 Sol (`gpt-6.1-sol`)** 중심의 개발 하네스다.
추론 강도(effort)는 기본으로 지정하지 않고 Codex가 실제 설정을 해석하도록 둔다.
기존 개인 하네스의 프로필·공학 원칙·계획 검증·코드 검수·설명·완료 감사를
Codex의 `AGENTS.md`, 저장소 Skill, 네이티브 훅으로 이식했다.

**반도체 지식 패키지는 1–5단계 수집을 완료했다.** 개념 65개·공개 1차 출처 84개와
문제 적용 절차·검색 메타데이터·재실행 가능한 합성 검사를 포함한다.
하네스의 시험 플랫폼 Codex 버전·허용 설정·Skill 발견·훅 지원 여부는 실제 사전체험에서 확인한다.

| 필요한 작업 | 시작 위치 |
| --- | --- |
| 과제에 하네스 설치·전용 프로필 적용 | 아래 ‘제공 Codex: README를 읽고 바로 적용’ |
| 반도체 용어·공식·조건 조회 | [지식 패키지 README](knowledge/semiconductor/README.md) |
| 실제 문제 분석·기준선·검증·제출 | [적용 가이드와 입력 프롬프트](knowledge/semiconductor/application-playbook.md) |
| 수집 범위·선수 개념 확인 | [5단계 읽기 지도](knowledge/semiconductor/curriculum.md) |
| 패키지 검사와 실제로 확인한 범위 | [검증 기록](knowledge/semiconductor/VALIDATION.md) |
| 사전체험에서 훅·Sol + Sol 실행 확인 | [15분 실행표](docs/practice-runbook.md) |

## 제공 Codex: README를 읽고 바로 적용

**이번 해커톤 전용 프로필은 이미 `template/.harness/project-profile.md`에 들어 있다.**
처음부터 범용 프로필을 만들지 말고 이 프로필을 실제 과제에 설치해 사용한다.
Sol + Sol 검수, effort 미고정, 검증·설명·시간·제출 원칙을 유지하고,
실제 과제에서만 알 수 있는 도메인·스택·불변식·제출 경로를 채운다.

사용자가 **“README 읽고 적용해”**라고 요청하면 아래 순서로 수행한다.

1. **반입 저장소와 설치할 과제 폴더를 구분한다.** 반입 전 작업 위치, 과제 README와
   기존 `AGENTS.md`로 실제 과제 Git 루트를 확인한다. 하네스 저장소 자체를 과제라고
   착각해 설치하지 않는다. 대상 경로를 알아낼 근거가 없을 때만 그 경로를 질문한다.
2. **현재 환경을 확인한다.** Python 3.9 이상·Bash·Git·제공 Codex, 쓰기 권한과 허용 경로를
   확인한다. 실제 환경의 권한·모델·effort·네트워크 정책을 우회하거나 자동 확대하지 않는다.
   전체 설치가 불가능하면 아래 문서형 모드를 적용하고 제한을 보고한다.
3. **반입한 패키지의 설치기를 실제 과제 루트에 실행한다.** `KTY_HARNESS_SOURCE`에
   확인한 반입 저장소 루트, `KTY_TASK_ROOT`에 실제 과제 루트를 설정한 뒤 실행한다.

   ```bash
   bash "$KTY_HARNESS_SOURCE/install.sh" "$KTY_TASK_ROOT"
   ```

4. **설치된 정본을 직접 읽어 적용한다.** 과제 루트의 `AGENTS.md`,
   `.agents/skills/kty-harness/SKILL.md`, `.harness/project-profile.md`, `.harness/principles.md`를
   읽는다. 프로필의 미확인 과제 사실은 실제 README·코드·업무 담당자 답변으로 갱신하고
   요구와 관찰 근거를 `.harness/task-evidence.md`에 연결한다.
   기존 프로필이 보존돼 있다면 반입본의 해커톤 정책과 비교해 필요한 내용을 병합한다.
   기존의 확인된 과제 사실을 템플릿의 미확인 값으로 덮어쓰지 않는다.
   반도체 용어·단위가 필요한 과제라면 **반입 저장소**의
   `knowledge/semiconductor/README.md`와 같은 폴더의 `application-playbook.md`를 읽고,
   그 폴더의 `index.jsonl`에서 관련 ID를 찾아 `path`의 본문·적용 조건·출처를 확인한다.
   실제 과제의 조건을 우선하고 예제 숫자를 제품 사양이나 과제 사실로 사용하지 않는다.
   지식 폴더는 설치 대상에 복사되지 않으므로 확인한 반입 경로와 사용한 ID를
   과제 진행 문서에 남긴다. 과제 해결도 요청받았다면 적용 가이드에 따라
   데이터 단위·분모·가용 시점·분할을 확인한 뒤 기준선·개선·제출 검사로 이어간다.
5. **실제 검증 명령을 등록한다.** 과제의 테스트·빌드·실행 방법을 확인해
   `.harness/checks.json`에 넣는다. 사전체험 marker 검사나 빈 명령을 본 과제의 검증으로
   쓰지 않는다. 적용 확인에 실행한 검사·결과·미실행 항목을 구분해 기록한다.
6. **현재 세션과 새 설정의 연결을 확인한다.** Sol 선택과 실제 effort, Skill 읽기·역할 발견을
   확인한다. 새 설정을 현재 세션이 발견하지 못하면 사용자에게 아래 새 세션 명령을 알려준다.
   대화 중인 Codex의 도구 안에서 인터랙티브 Codex를 중첩 실행해 기다리지 않는다.
   사용자가 `/hooks`에서 정상 신뢰 절차를 진행하도록 안내한다. 등록과 실제 콜백 실행은 구분한다.

   ```bash
   cd "$KTY_TASK_ROOT"
   bash .harness/codex.sh
   ```

7. **적용 상태를 보고한다.** 실제 과제 경로, 읽고 갱신한 프로필·Skill,
   등록·실행한 검증, Sol·실제 effort, 훅의 등록/신뢰/실행 상태,
   Sol 두 독립 리뷰의 실행 여부, 지식 폴더 경로·사용한 ID와 남은 제약을 보고한다.
   파일 복사만으로 훅·듀얼 검수·과제 검증이 성공했다고 말하지 않는다.
   적용만 요청받았다면 설치·설정·상태 확인까지만 수행한다.

사전체험용 진단을 요청받았을 때는 [15분 실행표](docs/practice-runbook.md)의
**별도 검증 폴더**를 사용한다. 실제 과제에 적용해 달라는 요청을 사전체험 fixture 생성으로
대체하거나, 실제 과제 폴더에 고의 결함·marker 검사를 넣지 않는다.

이미 반입한 패키지를 갱신할 때는 그 패키지의 Git 상태가 깨끗한지 확인하고
**반입 저장소만** `git pull --ff-only`로 갱신한다. 지식·문서만 갱신됐다면 새 파일을
읽으면 된다. 하네스 설치 파일도 갱신됐다면 설치기를 다시 실행한다.
`pull`만으로 과제 폴더의 하네스가 자동 갱신되는 것은 아니다. 기존 프로필·검증 명령은
보존되므로 필요한 병합을 확인한다. 과제 remote 변경·push·PR은 수행하지 않는다.

제공 Codex에 줄 짧은 요청 예시:

> 이 저장소 README를 읽고 원래 과제 작업 공간에 하네스를 적용해줘. 내장된 해커톤 전용 프로필을 사용하고 실제 과제 사실을 채워줘. 반도체 지식 README와 적용 가이드도 읽고 실제 반입 경로를 작업 기록에 남겨줘. 적용 결과와 아직 확인하지 못한 기능을 알려줘.

## 반도체 지식 패키지

[반도체 지식 진입점](knowledge/semiconductor/README.md)에 **1단계 기초, 2단계 소자·공정, 3단계 DRAM·NAND 동작, 4단계 HBM·패키징·신뢰성, 5단계 데이터 적용**을 제공한다.
기초 11개·소자/공정 14개·메모리 동작 13개·HBM/패키징/신뢰성 15개·데이터 적용 12개, 총 65개 본문과 검색 메타데이터가 들어 있다.
해커톤에서 이 저장소를 반입한 후 제공 Codex가 필요한 본문을 읽으면 된다. 별도 설치는 필요 없다.
[과제 적용 순서와 통합 검증](knowledge/semiconductor/application-playbook.md)에 시작 프롬프트와 문제별 읽기 경로를 적었다.
본문·색인은 파일 읽기만으로 사용한다. 패키지 자체를 재검사하려면 Python 3.9 이상이 있는
환경에서 아래 명령을 실행한다. 외부 패키지·API 키·네트워크는 필요 없다.

```bash
# 반입한 하네스 저장소 루트에서 실행
python3 knowledge/semiconductor/verify.py
```

현재 검사 범위는 개념 65개·출처 84개 연결, 검색어 62건, 코드에 고정한 교육용 계산 fixture 91건,
합성 적용 검사 16개다. 본문 숫자 전체를 자동 대조하는 검사는 아니다. 로그인 없이 새로 clone한 사본에서도 통과했다.
이 검사는 지식 패키지 검사이므로 **실제 과제의 테스트·빌드·모델 평가를 대체하지 않는다.**
지식 내용은 Sol + Sol 독립 전수 검토와 수정 후 영향 범위 재검토를 수행했다.
[65개 본문 리뷰](knowledge/semiconductor/reviews/2026-10-30/README.md)와
[나머지58개 출처의 Sol+Sol 원문 대조](knowledge/semiconductor/reviews/2026-10-30-remaining-sources/README.md)에 근거를 기록한다.
기존83개 출처 모두 원문 관련 구간 대조 이력이 생겼고, 유전율 보강 원문 S84도 양쪽이 확인했다.
초록·공개 소개·사용한 관련 절 범위의 확인이며 전문 전체나 실제 제품의 검증을 뜻하지 않는다.
실제 Probe 환경 검증은 아직 수행하지 않았다.

> 반입한 저장소의 knowledge/semiconductor/README.md를 읽고, 이 과제의 용어·단위와 관련된 항목만 찾아 적용해줘. 일반 지식과 실제 과제 조건을 구분하고 사용한 개념 ID와 검증 결과를 남겨줘.

## 사전체험 준비

태윤이가 직접 조작하고 외부 관찰자는 화면만 읽는
[사전체험 15분 실행표](docs/practice-runbook.md)를 준비했다.
GitHub 아이디만으로 찾는 첫 입력문, 훅 신뢰·재시작·실제 Stop 차단,
Sol 두 독립 검수와 판정 기준을 순서대로 따른다.
`scripts/practice_probe.py`는 허용된 폴더 안에 새 검증용 Git 프로젝트만 준비하며
AI 호출·신뢰 설정 변경·원래 연습 과제 수정은 하지 않는다. 실제 Probe 검증은 아직 미실행이다.
[로컬 실측](docs/timed-rehearsal.md)은 실패 복구 포함 약 14분 21초였으며 여유가 작았다.
네이티브 서브에이전트 대신 별도 Sol CLI 두 세션으로 검수를 완료했다.
[Probe 접근 확인](docs/probe-access-check.md)에서 공개 모의 화면과 실제 실행 환경을 구분했다.

## 설치와 실행

전체 설치·영수증·훅 기능은 Linux·macOS의 Bash, Python 3.9 이상, Git, 제공 환경의 Codex를 사용한다.
이 조건은 응시자 PC가 아니라 Probe 안에서 명령을 실행하는 터미널 환경 기준이다.
Python 외부 패키지와 별도 AI API 키·구독은 필요 없다. 이것은 하네스의 구현 의존성이다.
실제 Probe 이미지에 해당 도구가 있는지, 추가 설치 권한이 있는지는 아직 확인하지 않았다.

운영 안내에는 공개 GitHub 도구의 clone·다운로드와 터미널 설치가 명시돼 있다.
GitHub 반입 허용이 OS 패키지 설치 권한·모든 다운로드 주소의 접근·작업 공간 밖 쓰기를
보장하지는 않는다. 사전 체험에서 제공 환경의 터미널로 먼저 확인한다.

```bash
pwd
git --version
git rev-parse --show-toplevel
python3 --version
codex --version
```

Python이 이미 있으면 그대로 사용한다. 없거나 3.9 미만이면 허용된 설치 방법·권한·시간을
확인한 뒤 추가한다. 이 패키지는 sudo·시스템 패키지 설치·Python 다운로드를 자동 수행하지 않는다.

패키지 반입 경로는 허용된 쓰기 가능한 곳이면 된다. **작업 공간 밖 clone은 필수가 아니다.**
아래 `/tmp`는 접근 가능한 경우의 예시다. 설치 대상은 기존 과제 Git 저장소 루트다.

```bash
git clone https://github.com/xodbs1021/kty-codex-harness-template.git /tmp/kty-codex-harness
bash /tmp/kty-codex-harness/install.sh /path/to/task-workspace
cd /path/to/task-workspace
bash .harness/codex.sh
```

작업 공간 안에 가져와야 한다면 과제 Git 루트에서 다음 형태를 사용할 수 있다.
원본 반입 폴더는 Git에서 제외하며, 설치 대상 파일과 겹치지 않는다.
경로가 이미 있으면 덮어쓰지 않고 기존 반입 상태를 먼저 확인한다.

```bash
git clone https://github.com/xodbs1021/kty-codex-harness-template.git .harness/vendor/kty-codex-harness
bash .harness/vendor/kty-codex-harness/install.sh .
bash .harness/codex.sh
```

과제 폴더가 Git 루트가 아니면 임의로 `git init`하지 않고 실제 작업 경로를 확인한다.
파일이 반입됐다는 사실과 설치·Skill 발견·훅 활성화 성공은 각각 확인한다.

실행기는 모델을 명시한다. Codex는 `.codex/agents/`에서 네이티브 역할을 발견한다.
메인은 제공된 인증·승인·샌드박스·연결 설정을 상속한다.
기존 `.codex/config.toml`이 있으면 보존한다. 직접 `codex`로 실행했을 때 기존 설정이
다른 모델을 고를 수 있으므로 이 하네스의 실행기를 사용하고 `/status`에서 확인한다.
필요하면 요청문 하나를 인자로 전달한다.

```bash
bash .harness/codex.sh 'README와 하네스를 읽고 필수 요구사항부터 구현해줘'
```

설치기는 기존 `AGENTS.md`에 관리 블록만 추가하고 기존 훅과 함께 두 이벤트를 등록한다.
프로필·검증 명령은 재설치 시 보존한다. 관리 파일의 로컬 수정은 덮어쓰지 않고 중단한다.
구버전의 변경되지 않은 기본 config는 설치 manifest로 소유를 확인할 수 있을 때만
effort 없는 기본값으로 갱신한다. 사용자 설정이나 소유가 불명확한 config는 보존하므로,
이미 설치한 곳에서는 남아 있는 effort 설정도 확인한다.
훅을 추가하지 않는 환경에서는 `install.sh /path/to/workspace --no-hooks`를 사용한다.
이 옵션은 기존 훅을 끄거나 삭제하지 않는다.

### Python 설치가 어려울 때의 문서형 모드

핵심 프로필·원칙·검수 절차는 Markdown이다. 전체 설치가 불가능해도 제공 Codex로
반입한 패키지의 `template/.harness/project-profile.md`, `template/.harness/principles.md`,
`template/.agents/skills/kty-harness/SKILL.md`와 필요한 references를 읽고 적용할 수 있다.
자동 발견을 가정하지 말고 제공 Codex에 실제 반입 경로를 전달한다.
문서 안의 설치 후 상대 경로는 반입된 `template/` 안의 읽기 경로로 대응시키고,
진행·판단·검증 기록은 실제 과제 작업 공간에 작성한다.

이 모드에서는 설치기·`.harness/harness.py`·Python 훅을 실행하지 않는다.
문서의 Python 검증 명령 대신 과제 자체의 테스트·빌드·실행 명령을 직접 수행하고,
허용된 작업 공간의 진행 문서에 명령·결과·미검증 사항을 기록한다.
네이티브 독립 역할이 있으면 검수에 사용하고, 없으면 같은 세션 검수임을 밝힌다.
검증 영수증·강제 읽기 전용 별도 CLI·훅 게이트가 활성화됐다고 보고하지 않는다.
제공 환경이 Git도 지원하지 않으면 도구 반입·작업 저장 방법부터 Helper에 확인한다.

### 추론 강도 선택

기본 실행은 `model_reasoning_effort`를 주입하지 않는다. 프로젝트 기본 config와 역할
파일에도 effort를 지정하지 않는다. 최종 값은 Codex의 설정 우선순위와 모델·관리 정책에
따르므로 실제 실행 정보에서 확인한다. 시험 환경의 조절 지원 여부는 아직 미확인이다.

제공 환경에서 조절을 허용하고 해당 수준이 지원될 때만 명시적으로 선택한다.

```bash
bash .harness/codex.sh --effort high '필수 요구사항을 구현해줘'
python3 .harness/harness.py review --effort high '변경의 정확성과 보안을 검수해줘'
```

수준의 지원 여부는 Codex가 검증하며, 거부되면 오류를 그대로 반환한다.
다른 강도로 몰래 바꾸거나 설정 제한을 우회하지 않는다. 인터랙티브 CLI에서는
허용된 `/model` 선택기를 사용할 수 있다. 별도 review·audit CLI는 새 프로세스이므로
메인 화면에서 일시적으로 바꾼 effort가 그대로 이어진다고 가정하지 않는다.

## 프로젝트 설정

`.harness/project-profile.md`에는 이번 해커톤의 목표·도구 경계·Sol + Sol 검수·시간 배분·
제출 원칙을 미리 채웠다. 과제 도메인·스택·불변식·실행 경로·필수 제출물은 실제 접속 후 채운다.
기존 설치의 프로젝트 프로필은 보존하므로 새 배포본의 내용을 임의로 덮어쓰지 않는다.
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

## Probe에서 요구·판단·근거 연결

[공식 자료와 공개 데모 분석](docs/probe-analysis.md)을 바탕으로 실무 평가 절차를 보완했다.
`.harness/task-evidence.md`에는 필수 요구의 출처·성공 조건, 중요한 판단의 출처,
구현 위치와 실제 입력·결과를 연결한다. 이 문서는 재설치 시 보존한다.
과제에서 지정한 제출 문서가 있으면 그 문서를 정본으로 연결하고 필요한 근거를 반영한다.

데이터 제외·변환은 핵심 결과에 미치는 영향을 확인하고, 업무상 실패·반례도 검증한다.
AI 제안·테스트 실행과 응시자의 직접 결정·수동 확인을 구분한다.
작업 단계에서 코드의 이유·대안·한계를 설명하며, AI 설명만으로 본인 이해가 확인됐다고 쓰지 않는다.
후속 서술형 단계에는 AI 지원을 종료한다. 공개 데모 점수는 실제 과제 배점으로 사용하지 않는다.

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
  모두 `gpt-6.1-sol`이며 effort를 덮어쓰지 않는다. planner·reviewer·auditor는 파일을 수정하지 않도록 지시한다.
  각 파일에 이름·설명·지침을 선언한다. 프로젝트 신뢰가 필요하며 기존 설정 파일을 보존한다.
  멀티에이전트 기능 자체를 강제로 켜지 않는다.
- 환경이 지원·허용하면 검증 역할을 별도 컨텍스트에 위임한다.
  지원하지 않으면 제한을 밝히고 같은 세션에서 수행한다. 실제 독립 컨텍스트가 없으면
  독립 리뷰라고 주장하지 않는다. 원본의 이종 모델 듀얼 리뷰와는 보장 범위가 다르다.
- 프로필의 Sol + Sol 검수는 `kty_reviewer`를 두 독립 컨텍스트로 호출하거나 `review` 명령을
  두 번 새로 실행한다. 두 리뷰 모두 정확성과 보안을 보되 A/B 중점을 달리하며,
  같은 코드 상태를 서로의 결론 없이 검토한 뒤 메인이 지적을 합쳐 재현·판단한다.
  호출 계약은 `references/roles.md`에 있으며 이 절차의 실행을 훅이 강제하는 것은 아니다.
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
