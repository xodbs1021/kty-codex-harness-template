# 필요한 Google AIP 원문 선택

아래는 전체 AIP의 사본이 아니라 서비스 과제용 선택 묶음이다.
번호별 링크는 번들 원문이며 각 파일을 필요한 절까지 직접 읽는다.
일반 API 작업의 시작은 121이고 나머지는 실제 동작에 따라 고른다.

| 작업/쟁점 | 읽을 원문과 주요 절 |
| --- | --- |
| AIP의 의미·적용 상태 확인 | [1](aip/0001.md): What is an AIP?, Domain-specific AIPs, States |
| 리소스 경계·표준 동작·무상태 요청 | [121](aip/0121.md): Guidance, Methods, Strong Consistency, Stateless protocol |
| 리소스 식별자·계층·이름 | [122](aip/0122.md): Guidance, Collection identifiers, Resource ID segments |
| 단건 조회 | [131](aip/0131.md): Guidance, Errors |
| 목록 조회·정렬 | [132](aip/0132.md): Guidance, Ordering; [158](aip/0158.md): Guidance, Opacity, Backwards compatibility |
| 생성 | [133](aip/0133.md): Guidance, Errors |
| 부분 수정·필드 누락·기본값 | [134](aip/0134.md): Guidance, PATCH and PUT; [149](aip/0149.md): Guidance |
| 삭제·이미 없는 리소스 | [135](aip/0135.md): Guidance, Errors |
| CRUD로 표현하기 어려운 동작 | [136](aip/0136.md): Guidance, HTTP path, HTTP methods |
| 필드 이름·일관성·타입 | [140](aip/0140.md): Guidance, Case, String vs. bytes; [149](aip/0149.md): Guidance |
| 동시 변경·낙관적 잠금 | [154](aip/0154.md): Guidance |
| 중복 요청·재시도 | [155](aip/0155.md): Guidance; [194](aip/0194.md): Guidance, Retryable codes, Non-retryable codes |
| 기존 API 변경·기본값·필드/의미 호환 | [180](aip/0180.md): Guidance와 해당 변경 유형의 절 |
| 오류 계약·HTTP/JSON 대응 | [193](aip/0193.md): Guidance, Permission Denied, HTTP/1.1+JSON representation |
| 인가 순서·존재 여부 노출 | [211](aip/0211.md): Guidance, Multiple operations; [193](aip/0193.md): Permission Denied |

문서 원본 URL은 `https://google.aip.dev/<번호>`이며 버전은 [snapshot.json](snapshot.json)에 있다.
원문 내부의 `./NNNN.md` 링크는 상류의 다른 AIP를 가리킨다. 위 목록에 없는 AIP·이미지·
사이트 렌더링 자산은 포함하지 않았다. 필요한 내용이 번들 밖이면 미확인 범위를 남기고,
허용된 공개 문서 조회가 가능할 때만 공개 번호/개념으로 확인한다. 읽지 않은 내용을 채택하지 않는다.
실행 중 자동 다운로드나 갱신은 하지 않는다.
