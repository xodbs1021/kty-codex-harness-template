해는 **\(x=3,\;4\)**입니다.

\[
x^2-7x+12=(x-3)(x-4)=0
\]

원식 대입도 모두 통과했습니다.

- \(x=3:\;9-21+12=0\)
- \(x=4:\;16-28+12=0\)

지정된 역할·프로필·원칙·읽기 전용 절차와 `math-tools.md`를 읽고 적용했습니다. 실수 방정식이므로 설치된 SymPy의 정확한 기호 계산을 선택했습니다.

실제 실행은 REQUEST의 Python 경로에 `-B -c`로 메모리 내 계산 코드를 전달했습니다.

```text
/Users/kty/Documents/ChatGPT/sk-hynix-hackathon/tmp/math-rehearsal-2026-11-05/venv/bin/python -B -c '<계산·검증 코드>'
```

실제 결과:

```text
Python: 3.13.14
SymPy: 1.14.0
baseline: {2, 3}
roots: {3, 4}
independent integer residuals: {3: 0, 4: 0}
factor expansion: PASS
elapsed_seconds: 0.018046
exit_code: 0
```

기준 사례를 먼저 확인했고, 실제 해는 SymPy와 별도의 Python 정수 연산으로 재검산했습니다.

MCP의 앞선 `MCP tool call requires approval, but approval policy is never` 차단은 REQUEST에 기록된 사실이며, 이번에는 재호출하지 않았습니다. 별도로 허용된 로컬 계산만 성공했습니다. 파일 수정·설치·설정 변경·다른 에이전트·전체 개발 파이프라인은 수행하지 않았습니다.

계산 자체가 금지된 환경이라면 직접 라이브러리 호출로도 전환하지 않고, 계산·검증을 미실행으로 보고해야 합니다.
