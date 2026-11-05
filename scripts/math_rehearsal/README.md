# 합성 리허설 재현 스크립트

이 폴더는 [2026-11-05 검증](../../docs/math-rehearsal-2026-11-05/README.md)의 재현 자료다.
`template/`에 포함되지 않으므로 과제 설치본에 복사되거나 자동 실행되지 않는다.

- `run_libraries.py`: 라이브러리 계산·제약 검사·완전 탐색 비교.
- `verify_routes.py`: 작은 합성 경로의 별도 검사기와 정답 기준.
- `run_mcp.py`, `z3_routes.py`: 사전에 준비한 로컬 stdio 서버의 실제 호출 재현.
- `fixture.json`: 실제 시험 자료와 무관한 고정 합성 입력.

`run_mcp.py`에 남은 mcp-optimizer 분기는 **제외 결정을 뒷받침하는 과거 반례 재현용**이다.
현재 하네스 도구 선택·설치·대체 경로는 이를 사용하지 않는다. 새 과제에서 이 분기를 실행하지 않는다.
실제 도구 선택과 허용된 직접 호출 전환은
[하네스 수학 가이드](../../template/.agents/skills/kty-harness/references/math-tools.md)를 따른다.
