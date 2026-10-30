# 5단계 범위와 진행 상태

확인일: 2026-10-30. 단계는 학습/수집 범위이며 출제 확률 순위가 아니다.

| 단계 | 범위 | 상태 |
| --- | --- | --- |
| 1 | 전기·반도체·단위·디지털·제품 분류 기초 | 본문·색인 제공 |
| 2 | PN 접합·MOSFET·CMOS·제조 공정·계측·검사 | 본문·색인 제공 |
| 3 | DRAM·NAND 동작·리프레시·타이밍·오류·ECC 기초 | 본문·색인 제공 |
| 4 | HBM·TSV·적층·본딩·패키징·열/전력·신뢰성 | 미작성 |
| 5 | 수율·불량·장비 시계열 등 데이터 문제 적용·통합 검증 | 미작성 |

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

문제를 받은 뒤에는 전부 순서대로 읽지 말고 index.jsonl의 problem_signals와 aliases로 필요한 항목을 고른다. 단계 4–5의 주제가 검색돼도 앞 단계 정의를 심화 검증 자료로 취급하지 않는다.

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

## 3단계 읽기 지도

- [M01 DRAM 셀·전하 공유·센싱·복원](memory-operation/dram-cell.md) — 선수: F03, P02
- [M02 DRAM 채널·랭크·뱅크·행 버퍼](memory-operation/dram-organization.md) — 선수: M01, F09
- [M03 DRAM 명령·tRCD·tRP·tRAS·CL](memory-operation/dram-timing.md) — 선수: M02, F08
- [M04 DRAM 리프레시·retention·tREFI·tRFC](memory-operation/dram-refresh.md) — 선수: M01, M03
- [M05 DDR 전송률·버스트·유효 대역폭](memory-operation/ddr-transfer.md) — 선수: M02, F07, F11
- [M06 NAND 셀·전하 저장·문턱전압](memory-operation/nand-cell.md) — 선수: P02, F10
- [M07 NAND 페이지·블록·물리 용량](memory-operation/nand-geometry.md) — 선수: M06, F07, F09
- [M08 NAND 읽기·프로그램·소거·상태 확인](memory-operation/nand-operations.md) — 선수: M06, M07
- [M09 SLC·MLC·TLC·QLC·상태 분포](memory-operation/nand-multilevel.md) — 선수: M06, F07
- [M10 NAND retention·read disturb·P/E 이력](memory-operation/nand-retention-disturb.md) — 선수: M08, M09
- [M11 ECC·코드워드·SECDED·보호 범위](memory-operation/ecc-codeword.md) — 선수: F08, M01, M06
- [M12 FTL·GC·TRIM·쓰기 증폭](memory-operation/ftl-gc-waf.md) — 선수: M07, M08
- [M13 메모리 오류 지표·RBER·UBER·분모](memory-operation/memory-error-metrics.md) — 선수: M11, F07

DRAM은 M01 → M02 → M03/M04/M05, NAND는 M06 → M07/M09 → M08/M10/M12 순으로 읽는다.
오류 지표를 해석할 때는 M11 → M13을 함께 읽는다. 실측 원인 분석·통계 검증은 5단계 범위다.
