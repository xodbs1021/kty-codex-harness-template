# 수학 도구·MCP·Sol A/B 로컬 검증

2026-11-05, macOS arm64 / Python 3.13.14 / Codex CLI 0.165.0.
버스 도메인은 **합성 테스트 사례**다. 재시험 출제 예측이나 실제 시험 문제 복원이 아니다.

## 판정

| 경로 | 실제 관측 | 판정 |
| --- | --- | --- |
| 설치된 하네스 architect | 독립 Sol CLI가 가이드를 읽고 CP-SAT와 완전 탐색 기준선 선택 | 통과 |
| 직접 라이브러리 7개 | 각 도구에 맞는 작은 계산과 결과 검증 | 통과, 프로세스 분리 조건 |
| mcp-sympy · SDK stdio | 실제 sympy_solve 호출, 해 2·3 대입 검사 | 해당 호출 통과 |
| mcp-solver · SDK stdio | Z3 백엔드 생성 → 계산 → 독립 경로 검사 → submit_code | 해당 흐름 통과 |
| mcp-optimizer · SDK stdio | LP·기본 폐회로 성공, 시간 제한과 끝점 입력 무시 재현 | 해당 경로 기능 부적합 |
| Sol A/B 독립 리뷰 | 두 CLI 세션 모두 계산 재실행·원시 MCP 응답 검토 | 추가 지적 각 0건 |
| Codex 네이티브 MCP 호출 | 도구 선택·호출 시도 후 승인 정책으로 차단 | 실패: 실제 계산 미실행 |

**전체 경로가 무조건 작동한다는 결론은 아니다.** SDK 연결 성공은 Codex 승인 정책이나
실제 Probe의 사용 가능 여부를 증명하지 않는다. MCP 후보 3개를 모두 채택해도 된다는 뜻도 아니다.

## 검증 이후 하네스 반영

사용자 요청으로 mcp-optimizer는 **사용 후보에서 제거**했다. 현재 목록은 라이브러리7개·MCP2개다.
이 문서·results.json·검증 스크립트에 남은 mcp-optimizer는 실패 재현 이력이며 반입 하네스가
설치·등록하거나 대체 도구로 선택하는 경로가 아니다.
MCP 전용 제한일 때 별도로 허용된 라이브러리 직접 계산으로 전환하도록 Skill·workflow·관련 역할7개와
읽기 전용 절차를 갱신했다. 계산 자체 금지라면 미실행으로 남긴다.
갱신된 지침의 추가 검증은 [전환 검증](fallback.md)에 구분해 기록한다.

## 계산과 반례

- 정류장 4개, 각 2명, 버스 2대, 정원 4명, 도착 마감 12분의 작은 편도 모델.
- OR-Tools CP-SAT: `OPTIMAL`, 목적값·bound 모두 **22**.
  예: `0→1→3→5`, `0→2→4→5`, 각 11분.
- 표준 라이브러리 완전 탐색: 120후보, 유효 후보 6개, 최소값22.
  솔버와 별도 검사기로 방문·인원·끝점·시간·목적값을 재계산했다.
- 정원3·마감5는 각각 `INFEASIBLE`; 독립 탐색에서도 유효 후보0.
- 0초 계산 예산은 `UNKNOWN`으로 남겼으며 불가능으로 바꾸지 않았다.
- 누락·중복·정원 초과·마감 초과·목적값 오류·끝점 오류 주입6종을 거부했다.
- mcp-solver의 Z3에서도 정상22와 두 불가능 사례가 일치했다. submit_code 성공은
  문법 확인이며, 의미 검증은 그 전에 수행한 별도 검사와 완전 탐색이 담당했다.

라이브러리별 실제 버전·수치·시간은 [results.json](results.json)에 있다.
SymPy 방정식, SciPy/CVXPY LP, NetworkX 경로·도달 불가, Z3 모순, HiGHS 정수 최적화를 검사했다.
CVXPY는 HiGHS를 사용하므로 두 결과를 독립 최적화 엔진의 합의로 세지 않는다.

## 실행에서 드러난 문제

1. **macOS 네이티브 충돌:** highspy 1.15.1을 먼저 import하고 OR-Tools 9.15.6755를
   같은 프로세스에 import하면 libhighs 심볼 오류가 재현됐다. OR-Tools를 별도 프로세스로
   실행해 통과했다. 시스템 라이브러리나 관리자 권한 우회는 적용하지 않았다.
2. **mcp-optimizer 의존성:** 최초 환경의 PuLP 4 계열에서 `PULP_CBC_CMD` 부재로 LP가 실패했다.
   분리 환경에 `pulp<4`를 설치해 실제 3.3.2로 실행하자 LP·기본 경로 계산은 성공했다.
   이것은 아래 의미 오류를 해결하지 않는다.
3. **mcp-optimizer 의미 오류:** 고정 커밋 `65db2231711535033936975e7450032a3a494954`에서
   `max_time=1`인데 합계5인 경로를 `optimal`로 반환했다. 별도 입력의 `end_location=2`도
   무시해 끝점0을 반환했다. 입력·응답을 results.json에 보관했다. 시간·끝점 제약 문제에는
   해당 경로 도구를 채택하지 않는다. 상위 소스는 수정하지 않았다.
4. **리허설 코드 수정:** Z3 목적식 후보가 비면 Python 정수0이 되어 minimize가 실패했다.
   `z3.IntVal(0)`으로 형식을 유지하도록 수정하고 세 사례를 실제 재실행했다.
5. **Codex 네이티브 호출 차단:** 임시 실행 인자만으로 MCP 두 개를 연결했다. Sol은 Z3와
   SymPy를 선택했으나 두 도구 모두 `MCP tool call requires approval, but approval policy is never`
   오류로 차단됐다. 이 후속 경로에서는 계산하지 않았으며 권한 정책을 바꿔 재시도하지 않았다.
   CLI 종료 코드0은 이 두 도구 호출 성공을 뜻하지 않는다.

네이티브 MCP 구성은 [OpenAI 공식 설정 문서](https://learn.chatgpt.com/docs/config-file/config-reference)의
stdio command·args·enabled_tools 설정을 참고했다. 전역 MCP 등록·권한·신뢰 설정은 변경하지 않았다.
프로세스 종료 뒤 해당 MCP 서버와 IPython 커널이 남지 않았는지 확인했다.

## 실제 독립 검수

- [Sol A 결과](review-a.md), [Sol B 결과](review-b.md).
- 동일 입력 snapshot `d69b646c389b51dbf27d0cb42b594367772a76cb`, 입력97파일 해시 불변 확인.
- 요청·CLI 시작 정보는 모두 `gpt-6.1-sol`. effort override 없이 실제 CLI는 medium을 표시했다.
- A/B의 첫 검토 입력에 상대 결론을 넣지 않았다. 각자 테스트를 실행했다.
- 두 리뷰는 SDK 계산·반례·리허설 코드를 검수했다. 뒤에 추가한 네이티브 MCP 승인 차단 시험은
  별도 관측이며 이 리뷰가 그 경로의 실행 성공을 승인했다는 뜻이 아니다.
- 실제 FEASIBLE 반환과 Z3 UNKNOWN 반환은 이번 실행에서 만들지 않았다.

## 재현 자료와 범위

[검증 스크립트](../../scripts/math_rehearsal/)는 작은 합성 입력용이다. 일반 서비스 솔버가 아니다.
외부 패키지가 설치된 전용 환경에서 다음을 실행한다.

```bash
<전용-python> -B scripts/math_rehearsal/run_libraries.py
<MCP-SDK-python> -B scripts/math_rehearsal/run_mcp.py <리허설-경로> mcp-sympy
```

MCP runner는 지정 경로의 `venv/`, `venv-optimizer/`, 고정 checkout
`sources/mcp-solver/.venv/`, `evidence/`가 이미 준비됐다는 전제를 가진다.
자동 설치기가 아니다. mcp-optimizer probe의 종료0은 **부적합 반례까지 검사 완료**를 뜻하며,
`semantic_acceptance:false`와 분리해서 읽어야 한다.

로컬 전체 로그·설치 버전 목록·원시 MCP 전사는 `tmp/math-rehearsal-2026-11-05/evidence/`에 있다.
공개 요약은 원시 전사 SHA-256과 실제 입력/응답을 포함하며 대량의 상위 MCP 설명문은 복제하지 않았다.
`.harness/checks.json`에 직접 계산 검사를 등록한 `harness.py verify`도 실제 통과했다.
이번에 자동 훅·전체13역할·웹 서비스·실제 Probe를 새로 검증한 것은 아니다.
