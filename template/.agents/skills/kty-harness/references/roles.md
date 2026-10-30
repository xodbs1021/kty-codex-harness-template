# 역할 계약

각 역할은 현재 프로필·원칙·관련 코드와 앞 단계의 산출물을 근거로 수행한다.
확인하지 못한 사실은 미확인으로 적는다. 동일 세션의 역할 전환은 독립 리뷰가 아니다.

| 역할 | 할 일 | 완료 조건 |
| --- | --- | --- |
| research-collector | 출처·원문 위치·적용 조건 수집 | 재검증 가능한 수집물과 공백 반환 |
| research-evaluator | 새 컨텍스트에서 원문 대조·평가 | 채택·보류·기각 및 근거 반환 |
| clarifier | 실제 요구·제약·기존 결정을 확인 | 사용자 판단이 필요한 미확인점이 정리됨 |
| architect | 구조적 변경의 계약·대안·흐름 검토 | 실제 코드와 불변식에 모순 없음 |
| planner | 파일·단계·검증·위험·시간 배분 | 필수 동작마다 구현과 확인 방법 존재 |
| plan-reviewer | 요구 누락·과설계·가정·경계 확인 | 구현을 다시 해야 할 결함이 해결됨 |
| developer | 승인된 범위의 코드와 의미 있는 검증 작성 | 실제 명령 성공 또는 실패 원인 보고 |
| reviewer | 변경 양쪽 경계·호출자·오류·회귀 확인 | 차단 지적 해결, 미해결 사항 기록 |
| security-reviewer | 해당하는 입력·인증·저장·외부 연결 확인 | 구체적 피해 경로를 검증·처리 |
| test-analyzer | assertion·반례·mock 경계·회귀 방어 확인 | 실제 검증력과 빠진 사례 반환 |
| architecture-guide | 구조의 이유·대안·장단점·코드 근거 설명 | 의도와 추론을 구분한 설명 |
| change-explainer | 결과·이유·대안·실행 흐름 설명 | 응시자가 자신의 선택과 한계를 이해 |
| completion-auditor | 최신 코드·검증·필수 파일 대조 | 코드 완료와 실제 동작·제출 완료 구분 |

검수 지적은 `심각도 / 카테고리 / 파일:줄 / 어떤 입력·상태에서 어떤 오류가 나는지 / 근거`로 쓴다.
스타일은 Google Skill·원문 조항과 대조하고, 직접 검사와 이전 로그 확인을 구분한다.
카테고리 집계·전문 역할 제안은 [decision-memory.md](decision-memory.md)를 따른다.
CRITICAL·HIGH는 해결 전 완료로 처리하지 않는다. 재현이나 경로 근거 없이 심각도를 높이지 않는다.
지적 0건도 유효한 판정이다. 검증 실패와 환경 제한을 성공으로 바꾸어 적지 않는다.

선행 결정·조사를 했으면 읽은 경로·URL과 이번 작업에 적용한 결론을 적는다.
조사가 불필요하거나 불가능하면 구체적인 이유를 적는다. 형식만 채운 기록은 근거가 아니다.

## 실제 역할 이름과 실행

| 계약 | 네이티브 이름 | 읽기 전용 CLI role 이름 |
| --- | --- | --- |
| clarifier | kty_clarifier | clarifier |
| research-collector | kty_research_collector | research-collector |
| research-evaluator | kty_research_evaluator | research-evaluator |
| architect | kty_architect | architect |
| planner | kty_planner | planner |
| plan-reviewer | kty_plan_reviewer | plan-reviewer |
| developer | kty_developer | 해당 없음: 쓰기 허용된 메인/역할 사용 |
| reviewer | kty_reviewer | reviewer (`review` 별칭 유지) |
| security-reviewer | kty_security_reviewer | security-reviewer |
| test-analyzer | kty_test_analyzer | test-analyzer |
| change-explainer | kty_change_explainer | change-explainer |
| architecture-guide | kty_architecture_guide | architecture-guide |
| completion-auditor | kty_auditor | auditor (`audit` 별칭 유지) |

`python3 .harness/harness.py role <이름> '<실제 입력>'`은 해당 TOML과 관련 reference를 읽는
별도 Sol CLI를 실행한다. 이름 등록 실패 시에도 [workflow.md](workflow.md)의 직접 전달 경로를 쓴다.
메인은 맥락·입력·출력·역할별 독립 여부를 기록한다. 파일 복사나 도움말 출력은 실제 실행 증거가 아니다.

## 조건부 보안·테스트 검토

보안 경계 변경은 security-reviewer에게 실제 입력·권한·데이터 흐름을 전달한다.
인증/인가 누락·입력 검증·쿼리 구성·경로 탈출·비밀 노출·외부 호출 실패 중 관련 항목만 검토한다.
노출된 시크릿은 삭제만으로 해결되지 않으므로 폐기·교체 필요를 보고한다.
실제 값은 출력하지 않으며 교체는 허용된 운영 절차로 수행한다.
지적은 구체적인 피해 경로와 코드 근거를 요구한다. 스타일 지적을 보안 결함으로 부풀리지 않는다.

test-analyzer는 검사가 현재 실패를 실제로 잡는지, assertion이 결과를 검증하는지,
mock이 핵심 경계를 가렸는지, 정상/경계/실패 입력과 회귀 방어가 있는지 확인한다.
코드 읽기만으로 확인한 것과 실행한 검사를 구분하고 실제 파일 수정은 메인에게 돌려준다.

## Sol + Sol 검수 호출

이 해커톤 프로필의 설계·계획·코드 검수는 각 게이트마다 Sol A/B 두 개의 독립 실행으로 수행한다.
설계/계획은 plan-reviewer를, 코드는 reviewer를 두 번 새로 호출한다. PR 게이트는 시험 흐름에서 제외한다.
별도 역할 파일 두 개가 필요한 것은 아니다. 코드 검수는 `kty_reviewer`를 새 컨텍스트로 두 번 호출하거나,
아래 코드 검수용 읽기 전용 명령을 서로 다른 요청으로 각각 실행한다.
설계/계획 각 pass는 `harness.py role plan-reviewer`를 A/B로 두 번 호출한다.
고위험 단독 지적의 교차 확인·기각·미확정 처리는 workflow 4단계를 각 게이트에 적용한다.

```bash
python3 .harness/harness.py review '리뷰 A: [대상·요구·판정 기준] 정확성과 보안을 검토하되 요구·계약·호출자·회귀에 중점을 두고, 이전 리뷰 결과를 읽지 말라.'
python3 .harness/harness.py review '리뷰 B: [같은 대상·요구·판정 기준] 정확성과 보안을 검토하되 공격 경로·잘못된 가정·권한·입력 경계·실패 조건에 중점을 두고, 이전 리뷰 결과를 읽지 말라.'
```

- 두 요청의 대괄호는 실제 대상·공통 요구로 채운다. 모델은 Sol, effort는 환경이 해석한다.
- 도구가 지원하면 `fork_turns="none"`으로 부모 대화 상속을 끄고 필요한 입력을 명시적으로 전달한다.
  기본값으로 전체 대화를 복사한 새 자식은 이 프로필의 독립 리뷰로 세지 않는다.
  같은 자식의 역할 전환·재응답도 새 A/B pass를 대신하지 않는다. 실제 호출 인자·ID를 기록한다.
- 시작 시 코드 지문을 확인하고 두 검토가 끝날 때까지 구현을 멈춰 같은 상태를 검토한다.
  진행·검수 기록은 `.harness/work/`에 두며, 서로의 결과를 첫 검토 입력으로 주지 않는다.
- 두 응답을 얻은 뒤 메인이 지적을 출처별로 합쳐 재현·수용·수정·기각 이유를 기록한다.
  코드가 중간에 바뀌면 같은 상태에 대한 듀얼 리뷰로 처리하지 않고 필요한 검토를 다시 한다.
- 수정 후 최신 검증과 영향 범위 재검수를 수행한다. 같은 세션의 재검토나 완료 감사가
  두 번째 독립 리뷰를 대신하지 않는다. 호출 실패·미지원은 듀얼 리뷰 미실행으로 보고한다.
- 이 절차는 역할 지침이며, 검증 훅이 두 번의 리뷰 실행이나 지적의 적절성까지 증명하지 않는다.
