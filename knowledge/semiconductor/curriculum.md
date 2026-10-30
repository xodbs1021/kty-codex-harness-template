# 4단계 범위와 진행 상태

확인일: 2026-10-30. 단계는 학습/수집 범위이며 출제 확률 순위가 아니다.

| 단계 | 범위 | 상태 |
| --- | --- | --- |
| 1 | 전기·반도체·단위·디지털·제품 분류 기초 | 본문·색인 제공 |
| 2 | PN 접합·MOSFET·CMOS·제조 공정·계측·검사 | 미작성 |
| 3 | DRAM·NAND 동작·HBM·적층·패키징·신뢰성 | 미작성 |
| 4 | 수율·불량·장비 시계열 등 데이터 문제 적용·통합 검증 | 미작성 |

## 1단계 읽기 지도

- [F01 전하·전류·전압](fundamentals/charge-current-voltage.md) — 선수: 없음
- [F02 저항과 옴의 법칙](fundamentals/resistance-ohm.md) — 선수: F01
- [F03 커패시터·정전용량](fundamentals/capacitance.md) — 선수: F01
- [F04 전력·에너지](fundamentals/power-energy.md) — 선수: F01, F02
- [F05 반도체·밴드·전자와 정공](fundamentals/semiconductor-bands.md) — 선수: F01
- [F06 도핑·n형·p형](fundamentals/doping-carriers.md) — 선수: F05
- [F07 비트·바이트·단위 접두어](fundamentals/bits-bytes-prefixes.md) — 선수: 없음
- [F08 디지털 논리·클록·주파수](fundamentals/digital-clock-logic.md) — 선수: F07
- [F09 웨이퍼·다이·IC·패키지](fundamentals/wafer-die-ic.md) — 선수: F05
- [F10 메모리·로직·휘발성 구분](fundamentals/memory-map.md) — 선수: F07, F09
- [F11 용량·대역폭·지연시간](fundamentals/capacity-bandwidth-latency.md) — 선수: F07, F08, F10

문제를 받은 뒤에는 전부 순서대로 읽지 말고 index.jsonl의 problem_signals와 aliases로 필요한 항목을 고른다. 단계 2–4의 주제가 검색돼도 1단계 정의를 심화 검증 자료로 취급하지 않는다.
