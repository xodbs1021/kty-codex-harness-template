<!-- kty-codex-harness:start -->
## KTY Codex 하네스

코드 변경·계획·검수는 `.agents/skills/kty-harness/SKILL.md`를 읽고 수행한다.
프로젝트 사실은 `.harness/project-profile.md`, 원칙은 `.harness/principles.md`,
검증 명령은 `.harness/checks.json`이 정본이다.
실행 모델은 `gpt-6.1-sol`, 추론 강도는 `xhigh`다.
진행 상태는 `.harness/work/progress.md`에 남기고 최신 코드에서
`python3 .harness/harness.py verify`를 실행한 결과를 보고한다.
시험 모드에서는 제공 환경 안에서 작업하고 외부 push·게시·전송을 하지 않는다.
<!-- kty-codex-harness:end -->
