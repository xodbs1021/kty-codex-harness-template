<!-- kty-codex-harness:start -->
## KTY Codex 하네스

사용자가 하네스 설치·적용·설정 이어가기를 요청하면 파일 복사에서 멈추지 말고
`.harness/setup.md`를 읽어 과제 설정·활성화 확인·검증까지 수행한다.
진행과 남은 사용자 조치는 `.harness/setup-status.md`에 남긴다.
코드 변경·계획·검수는 `.agents/skills/kty-harness/SKILL.md`를 읽고 수행한다.
프로젝트 사실은 `.harness/project-profile.md`, 원칙은 `.harness/principles.md`,
검증 명령은 `.harness/checks.json`이 정본이다.
실무 평가 과제의 요구·판단 출처·구현과 실제 검증 근거는 `.harness/task-evidence.md`에 연결한다.
실행 모델은 `gpt-6.1-sol`이다. 추론 강도는 고정하지 않고 Codex의 실제 설정을 따른다.
진행 상태는 `.harness/work/progress.md`에 남기고 최신 코드에서
`python3 .harness/harness.py verify`를 실행한 결과를 보고한다.
시험 모드에서는 제공 환경 안에서 작업하고 외부 push·게시·전송을 하지 않는다.
<!-- kty-codex-harness:end -->
