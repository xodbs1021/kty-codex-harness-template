# 출처와 이식 범위

확인일: 2026-10-27.

## 개인 하네스 원본

- 저장소: https://github.com/xodbs1021/kty-claude-harness-template (비공개)
- 기준: `origin/main`, `ab266415be98badcee06d06253c43921e1449614`
- 유지한 설계: 도메인 프로필 슬롯, 단일 공학 원칙, 요구 확인·설계·계획 검증·구현·검수·
  변경 설명·완료 감사, 선행 결정 조회, 작업 진행 상태, 실제 검증 근거.
- 이식한 구성: `.claude` 에이전트·Skill → 저장소 `AGENTS.md`·`.agents/skills/kty-harness`;
  검증 누락 확인 → Codex 네이티브 SessionStart·Stop와 코드 지문·검증 영수증.
- 제거한 실행 의존: Claude Code, Opus/Sonnet 호출, Claude+Codex 이종 듀얼 리뷰,
  Claude 전용 훅·MCP 가드·전역 에이전트 배포, claude-mem·superpowers 플러그인,
  자동 push·PR·개인 지식 저장소 반영.
- 시험용 조정: 반복 무지적 횟수 충족을 강제하지 않고 시간 안에 필수 동작과 검증을 완결.
  스타일 가이드 원문 대량 사본 대신 공개 원문과 프로젝트 formatter·linter를 확인.
- 메인 모델과 추론 강도: `gpt-6.1-sol`·`xhigh`. 다른 모델 자동 폴백 없음.

본인 소유 비공개 저장소는 같은 GitHub 계정으로 fork할 수 없으므로 독립 파생 저장소로
구성했다. 공개 배포할 코드·범용 지침만 새 이력으로 담았으며 원본의 비공개 과거 커밋·
작업 기록·도메인 프로필·개인 파일·시험 안내 PDF는 포함하지 않는다.

## ECC

- 공개 저장소: https://github.com/affaan-m/everything-claude-code
- 기준 커밋: `25278e7d7b6cf6e6a4e7a6c8e10f14ff22f0eb5b`
- Codex 지원 확인: 해당 커밋 `.codex/AGENTS.md`, `.codex/config.toml`, `.agents/skills/`.
- 배포 원문: `rules/common/coding-style.md`, `rules/common/testing.md`,
  `rules/common/security.md`의 원문을 Skill 하위 `references/vendor/ecc/`에 보관.
- 라이선스: MIT, Copyright (c) 2026 Affaan Mustafa. 동 폴더의 `LICENSE` 유지.
- 적용 예외는 `references/ecc-quality.md`에 명시했다. ECC 전체 설치본이라고 주장하지 않는다.

## OpenAI 공식 문서

- 모델: https://developers.openai.com/api/docs/models/gpt-6.1-sol
- 저장소 Skill 발견: https://learn.chatgpt.com/docs/build-skills
- AGENTS: https://learn.chatgpt.com/docs/agent-configuration/agents-md
- 설정: https://learn.chatgpt.com/docs/config-file/config-reference
- 네이티브 훅·신뢰·입출력: https://learn.chatgpt.com/docs/hooks

실제 시험 플랫폼의 기능 가용성과 관리 정책은 아직 미확인이다.
