# PRD: EOL Diagnostic Tester

## 목표
양산 제품 출하 전 `Mower / RFS120S` 제어기를 검사하는 Windows EOL 및 진단 프로그램을 만든다.

프로그램은 실제 Kvaser/PEAK USB CAN 장비를 인식하고, 설정된 CAN 통신 조건으로 실제 UDS 메시지를 송수신해야 한다. 작업자는 복잡한 CAN/UDS 세부 지식 없이 모델 선택, VIN 입력, 검사 실행, 결과 확인, 리포트 저장을 안정적으로 수행할 수 있어야 한다.

## 대상 사용자
- 양산 라인 작업자: VIN 입력, 장비 연결 확인, 자동검사 실행, 결과 확인
- 개발자/관리자: CAN 설정, 모델별 기능 설정, DTC 매핑 관리, 통신 trace 확인
- 품질/서비스 담당자: 저장된 검사 리포트 조회 및 PDF 확인

## MVP 대상
- 제품군: `Mower`
- 모델: `RFS120S`
- 플랫폼: Windows desktop
- UI 기술: `.NET WPF`
- 통신: UDS on CAN, Kvaser/PEAK USB CAN 장비

## 핵심 기능

### 화면 흐름
1. 모델 선택
   - MVP에서는 `Mower / RFS120S`를 선택한다.
   - 모델 선택 화면은 확장성을 위한 진입점이며 상세 정보를 많이 표시하지 않는다.
2. 검사 준비
   - VIN 입력은 필수다.
   - 작업자 입력은 권장이다.
   - 설정된 CAN Driver 기준의 장비 상태를 `연결됨 / 미연결`로 표시한다.
   - VIN 입력과 장비 연결이 만족되어야 기능 메뉴에 진입할 수 있다.
   - CAN Setting은 설정 영역에서 접근하며, 검사 준비 화면에는 전체 설정을 펼쳐놓지 않는다.
3. 기능 메뉴
   - 실제 EOL/진단 기능만 배치한다.
4. 결과 확인
   - 자동검사 완료 후 리포트 미리보기를 보여준다.
   - 저장 시 PDF와 내부 JSON을 생성한다.

### 기능 메뉴
- 자동검사
- 시스템 사양정보
- 현재 고장 진단
- 과거 고장 진단
- 고장 소거
- 강제구동
- 리프로그래밍
- 프리즈 프레임 조회
- 결과 리포트 조회

`리프로그래밍`과 `프리즈 프레임 조회`는 MVP에서 메뉴만 제공하고 세부 구현은 제외한다.

### 설정 및 도구
- 설정
  - CAN Setting
  - 기능 Setting
- 도구
  - 통신 모니터링

통신 모니터링은 MVP에서 CAN Trace 기능만 제공한다. Manual Transmit과 별도 로그 화면은 MVP에서 제외한다.

## CAN 및 장비 요구사항
- Driver: `Kvaser`, `PEAK`, `Simulator`
- 현장 MVP 기준은 실제 Kvaser/PEAK USB CAN 장비다.
- Simulator는 개발과 테스트 보조용이다.
- CAN Type: `Classic CAN`, `CAN FD`
- ID Type: `Standard 11-bit`, `Extended 29-bit`
- Classic CAN 설정:
  - bitrate
- CAN FD 설정:
  - arbitration bitrate
  - data bitrate
  - BRS
  - ISO CAN FD
- TX/RX ID 설정을 지원한다.
- Channel은 기본 자동 선택이다.
  - 연결된 채널이 1개면 자동 선택한다.
  - 여러 채널이 감지되는 경우 선택 가능하도록 확장한다.
- 모든 화면에서 장비 연결 상태를 공통 표시한다.
- 장비 연결이 해제되면 진행 중 기능을 중지하고 모델 선택 화면으로 복귀한다.

## UDS 요구사항
기준 문서: `reference/uds/20260427_SRS_MOWER_UDS_ON_CAN.pptx`

### 공통 판정
- Positive Response: 해당 request 성공
- Negative Response: NG
- Timeout: NG
- 응답 없음: NG
- 장비 미연결: NG 또는 실행 차단

### Tester Present
- 전체 강제구동 순차 실행 중 `0x3E 00`을 `2000ms` 주기로 송신한다.
- 개별 강제구동은 짧은 실행이므로 별도 Tester Present 유지 송신을 하지 않는다.

### 시스템 사양정보
- `ReadDataByIdentifier(0x22)`로 Basic Data를 조회한다.
- 표시 항목 예:
  - Model Name
  - Part Number
  - HW 버전
  - SW 버전
  - 생산년도
  - 생산월
  - 생산일
  - WCU 총 누적 구동시간
- 하나의 DID 응답이 여러 표시 항목으로 파싱될 수 있어야 한다.
  - 예: 생산일자 DID 1개를 생산년도/생산월/생산일로 분리 표시
- 초기화 버튼은 두지 않고 `읽기` 중심으로 구성한다.

### 고장 진단
- 현재 고장 조회: `0x19 0x02 0x09`
- 과거 고장 조회: `0x19 0x02 0x08`
- 수동 조회에서는 DTC 존재 여부가 NG가 아니다.
  - Positive Response면 조회 성공이다.
  - DTC는 화면에 표시한다.
- 고장 소거: `0x14 FF FF FF`
  - 제품을 판매 가능한 새 제품 상태로 만들기 위한 필수 EOL 단계다.
  - 확인 팝업 후 실행한다.
- 자동검사에서는 고장 소거 후 과거 고장 조회에서 DTC가 남아 있으면 NG다.

### DTC 표시
- UDS response의 2-byte DTC를 P-Code로 변환한다.
- UI에는 P-Code와 Description 중심으로 표시한다.
- raw 2-byte DTC는 내부 JSON/trace/디버깅 데이터에 보관한다.
- 매핑 실패 시 UI에는 `Unknown(0xNNNN)`으로 표시한다.
- DTC 매핑:
  - 원본 관리 파일: `reference/dtc/dtc_map.xlsx`
  - 앱 실행 파일: `C:\ProgramData\DaedongRobotics\EolDiagnosticTester\mapping\DTC\dtc-map.json`
  - JSON 필드: `Ecu`, `Dtc2Byte`, `PCode`, `Severity`, `Description`
- Excel은 사람이 관리하는 원본이며, 앱은 JSON을 읽는다.

### 강제구동
- UDS 서비스: `InputOutputControl 0x2F B0 xx`
- Start: `0x03`
- Stop: `0x00`
- 상태:
  - `N/A`
  - `RUN`
  - `OK`
  - `NG`
- 기본 실행 시간: 4초
- 전체 순차 실행 항목 간 기본 텀: 1초
- 전체 순차 실행 대상:
  - Error IND `0x1E`
  - BMS IND `0x1F`
  - Motor L/M/R IND `0x20`
  - Motor S IND `0x21`
  - Motor L `0x22`
  - Motor M `0x23`
  - Motor R `0x24`
  - Motor S `0x25`
- `ALL ON 0x26`은 전체 순차 실행에서 제외한다.
- 일반 NG는 해당 항목에 표시하고 다음 항목으로 진행한다.
- 사용자 전체 정지 시 현재 RUN 항목에 Stop을 시도하고 종료한다.
- Start가 성공한 항목은 Stop을 최대한 보장한다.

## 자동검사

### 실행 순서
1. 시스템 정보 조회
2. 현재 고장 조회
3. 고장 소거
4. 과거 고장 조회
5. 강제구동
6. 결과 리포트 미리보기

### 화면 표시
- 상단에는 `현재 단계`와 `진행률`만 표시한다.
- 본문에는 단계별 실제 결과 패널을 누적 표시한다.
  - 시스템 사양정보 결과 테이블
  - 현재 고장 진단 P-Code 결과
  - 고장 소거 결과 메시지
  - 과거 고장 진단 P-Code 결과
  - 강제구동 항목별 결과
- 각 단계는 수동 기능 화면과 같은 결과 테이블 컴포넌트를 재사용한다.
- raw TX/RX는 기본 숨김이며 단계별 상세 보기에서만 확인한다.

### 자동검사 판정
- 시스템 정보 조회: 모든 request가 Positive Response면 OK
- 현재 고장 조회: Positive Response면 OK, DTC는 화면에 표시
- 고장 소거: Positive Response면 OK
- 과거 고장 조회: Positive Response이고 DTC가 없으면 OK, DTC가 남아 있으면 NG
- 강제구동: 각 항목 Start/Stop Positive Response면 OK, NG가 있어도 다음 항목 진행

## 결과 리포트
- 검사 완료 후 화면 미리보기를 제공한다.
- HTML은 파일로 저장하지 않고 미리보기 렌더링에만 사용한다.
- `저장하기`를 누르면 PDF와 내부 JSON을 저장한다.
- 저장하지 않고 화면을 나가려 하면 확인 팝업을 띄운다.
- PDF는 사용자용 최종 리포트다.
- JSON은 결과 리포트 조회, PDF 재생성, 분석을 위한 내부 데이터다.
- 결과 리포트 조회는 현재 선택 모델(`Mower / RFS120S`)의 리포트만 조회한다.

## 파일 저장 위치
기본 루트는 다음 경로를 사용한다.

```text
C:\ProgramData\DaedongRobotics\EolDiagnosticTester
```

앱 시작 시 필요한 폴더가 없으면 자동 생성한다.

```text
C:\ProgramData\DaedongRobotics\EolDiagnosticTester
├─ config
│  ├─ appsettings.json
│  ├─ can-settings.json
│  └─ models
│     └─ Mower
│        └─ RFS120S
│           └─ model.json
├─ mapping
│  └─ DTC
│     ├─ dtc-map.json
│     └─ dtc_map.xlsx
├─ programming
│  └─ Mower
│     └─ RFS120S
│        ├─ packages
│        └─ archive
├─ reports
│  ├─ pdf
│  │  └─ Mower
│  │     └─ RFS120S
│  │        └─ YYYY
│  │           └─ MM
│  └─ json
│     └─ Mower
│        └─ RFS120S
│           └─ YYYY
│              └─ MM
├─ logs
│  ├─ app
│  ├─ uds
│  └─ can-trace
├─ exports
└─ temp
```

## MVP 제외
- 리프로그래밍 세부 구현
- 프리즈 프레임 조회 세부 구현
- 센서데이터 조회
- 통신 모니터링 Manual Transmit
- 별도 로그 조회 화면
- 기능 Setting UI 전체 구현
