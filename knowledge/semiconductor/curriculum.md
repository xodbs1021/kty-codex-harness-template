# 4단계 범위와 진행 상태

확인일: 2026-10-30. 단계는 학습/수집 범위이며 출제 확률 순위가 아니다.

| 단계 | 범위 | 상태 |
| --- | --- | --- |
| 1 | 전기·반도체·단위·디지털·제품 분류 기초 | 본문·색인 제공 |
| 2 | PN 접합·MOSFET·CMOS·제조 공정·계측·검사 | 본문·색인 제공 |
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

문제를 받은 뒤에는 전부 순서대로 읽지 말고 index.jsonl의 problem_signals와 aliases로 필요한 항목을 고른다. 단계 3–4의 주제가 검색돼도 앞 단계 정의를 심화 검증 자료로 취급하지 않는다.

## 2단계 읽기 지도

- [P01 PN 접합·공핍층·바이어스](devices-process/pn-junction.md) — 선수: F01, F05, F06
- [P02 MOSFET·문턱전압·동작 영역](devices-process/mosfet.md) — 선수: P01, F03
- [P03 CMOS 인버터·동적 전력·누설](devices-process/cmos-power.md) — 선수: P02, F04, F08
- [P04 공정 흐름·FEOL·배선·후공정](devices-process/process-flow.md) — 선수: F09, P02
- [P05 열산화·산화막·절연](devices-process/oxidation.md) — 선수: F03, F05, P04
- [P06 증착·PVD·CVD·ALD](devices-process/deposition.md) — 선수: P04, F03
- [P07 포토리소그래피·노광·현상](devices-process/lithography.md) — 선수: P04
- [P08 식각·선택비·이방성](devices-process/etch.md) — 선수: P06, P07
- [P09 이온 주입·확산·어닐링](devices-process/implant-anneal.md) — 선수: F06, P04
- [P10 CMP·평탄화·표면 손상](devices-process/cmp.md) — 선수: P06, P08
- [P11 금속 배선·컨택·비아·다마신](devices-process/interconnect.md) — 선수: F02, P06, P08, P10
- [P12 계측·검사·CD·오버레이](devices-process/metrology-inspection.md) — 선수: P07, P08, F09
- [P13 전기적 검사·EPM·웨이퍼 테스트](devices-process/electrical-test.md) — 선수: P02, P11, P12
- [P14 세정·오염·잔사](devices-process/cleaning.md) — 선수: P04, P07
