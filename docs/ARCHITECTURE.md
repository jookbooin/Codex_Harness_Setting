# Architecture

## 원칙
- UI 계층은 CAN/UDS/Vendor SDK 세부 구현을 직접 알지 않는다.
- 통신 계층은 UI 상태나 WPF 타입에 의존하지 않는다.
- 장비 Driver, ISO-TP, UDS, 자동검사, 리포트 생성을 분리한다.
- 모든 장기 작업은 async와 cancellation 기반으로 구현한다.
- 장비 연결 해제는 전역 이벤트로 처리하고 진행 중 작업을 안전하게 중단한다.

## 솔루션 구조

```text
src/
├─ EolDiagnosticTester.App
│  └─ WPF UI, Views, ViewModels, navigation, styling
├─ EolDiagnosticTester.Application
│  └─ use cases, workflow orchestration, DTOs, app services
├─ EolDiagnosticTester.Domain
│  └─ domain models, UDS result models, DTC models, validation, judging rules
├─ EolDiagnosticTester.Infrastructure
│  └─ Kvaser/PEAK adapters, ISO-TP transport, file system, report, mapping loaders
└─ EolDiagnosticTester.Tests
   └─ unit and integration tests
```

## 의존성 방향

```text
App
  -> Application
      -> Domain

Infrastructure
  -> Application abstractions
  -> Domain
```

`Application`은 인터페이스를 정의하고, `Infrastructure`가 구현한다. `App`은 ViewModel에서 UseCase를 호출한다.

## 계층 역할

### App
- WPF 화면과 ViewModel
- 모델 선택, 검사 준비, 기능 메뉴, 자동검사, 수동 기능, 결과 리포트 조회
- 공통 장비 상태 표시
- 사용자의 버튼 클릭과 화면 전환
- CAN frame, UDS parsing, Vendor SDK 직접 호출 금지

### Application
- 사용 사례 조립
- 자동검사 시퀀스 실행
- 수동 시스템 정보 조회, DTC 조회, 고장 소거, 강제구동 실행
- 현재 모델, VIN, 작업자, 검사 세션 관리
- 장비 연결 해제 시 cancellation 처리
- 리포트 데이터 생성 요청

대표 UseCase:

```text
SelectModelUseCase
PrepareInspectionUseCase
ReadSystemInfoUseCase
ReadCurrentDtcUseCase
ReadHistoryDtcUseCase
ClearDtcUseCase
RunActuatorItemUseCase
RunActuatorSequenceUseCase
RunAutoTestUseCase
BuildReportPreviewUseCase
SaveReportUseCase
QueryReportsUseCase
```

### Domain
- 순수 도메인 모델과 판정 규칙
- CAN 설정 검증
- UDS request/response 모델
- Positive/Negative/Timeout 판정
- DTC raw value와 P-Code 매핑 결과 모델
- second 값을 사람이 읽는 시간 형식으로 변환하는 규칙
- 자동검사 결과 모델

### Infrastructure
- Kvaser CANlib 기반 USB 장비 검색/연결/송수신
- PEAK PCAN-Basic 기반 USB 장비 검색/연결/송수신
- Simulator CAN 장비
- ISO-TP 송수신
- UDS Client 구현
- ProgramData 폴더 생성 및 파일 입출력
- DTC JSON 매핑 로더
- model.json 로더
- PDF 생성
- 통신 trace ring buffer

## 통신 계층

통신은 아래 순서로 분리한다.

```text
ViewModel
  -> UseCase
    -> IUdsClient
      -> IIsoTpTransport
        -> ICanDevice
          -> KvaserCanDevice / PeakCanDevice / SimulatorCanDevice
```

### 주요 인터페이스

```csharp
public interface ICanDevice
{
    Task<IReadOnlyList<CanChannelInfo>> ScanChannelsAsync(CancellationToken ct);
    Task OpenAsync(CanOpenOptions options, CancellationToken ct);
    Task CloseAsync(CancellationToken ct);
    Task SendAsync(CanFrame frame, CancellationToken ct);
    IAsyncEnumerable<CanFrame> ReceiveAsync(CancellationToken ct);
    CanConnectionState ConnectionState { get; }
}

public interface IIsoTpTransport
{
    Task<UdsRawResponse> SendRequestAsync(UdsRawRequest request, CancellationToken ct);
}

public interface IUdsClient
{
    Task<UdsResult> EnterExtendedSessionAsync(CancellationToken ct);
    Task<UdsResult> SendTesterPresentAsync(CancellationToken ct);
    Task<UdsDataResult> ReadDataByIdentifierAsync(ushort did, CancellationToken ct);
    Task<DtcReadResult> ReadCurrentDtcAsync(CancellationToken ct);
    Task<DtcReadResult> ReadHistoryDtcAsync(CancellationToken ct);
    Task<UdsResult> ClearDtcAsync(CancellationToken ct);
    Task<UdsResult> StartIoControlAsync(byte controlId, CancellationToken ct);
    Task<UdsResult> StopIoControlAsync(byte controlId, CancellationToken ct);
}
```

## 상태 및 세션

전역 상태는 명확히 분리한다.

```text
SelectedModelContext
InspectionSessionContext
DeviceConnectionMonitor
OperationCoordinator
TraceStore
```

- `SelectedModelContext`: `Mower / RFS120S`
- `InspectionSessionContext`: VIN, 작업자, 시작/종료 시간, 검사 결과
- `DeviceConnectionMonitor`: 설정된 Driver 기준 연결됨/미연결 감시
- `OperationCoordinator`: 자동검사/수동기능/강제구동 같은 동시 실행 제어
- `TraceStore`: 통신 모니터링 표시용 ring buffer

장비 연결 해제 이벤트 발생 시:
1. 현재 작업 cancellation 요청
2. 진행 중 기능 NG 또는 중단 처리
3. 열려 있는 CAN 장비 close
4. 모델 선택 화면으로 복귀

## 모델 정의

MVP 대상 모델은 `Mower / RFS120S`다.

```text
config/models/Mower/RFS120S/model.json
```

`model.json`은 이후 확장을 위해 아래 정보를 담는 기준 파일로 둔다.

- product group
- model name
- VIN required 여부
- 시스템 정보 DID 목록과 파싱 규칙
- DTC 조회 설정
- 고장 소거 설정
- 강제구동 항목
- 자동검사 순서
- 리포트 표시 항목

MVP에서는 UI 기반 기능 Setting 전체 구현 없이 파일 구조와 로더를 우선 둔다.

## 파일 저장 구조

루트:

```text
C:\ProgramData\DaedongRobotics\EolDiagnosticTester
```

필수 폴더는 앱 시작 시 자동 생성한다.

```text
config/
mapping/DTC/
programming/Mower/RFS120S/packages/
programming/Mower/RFS120S/archive/
reports/pdf/Mower/RFS120S/YYYY/MM/
reports/json/Mower/RFS120S/YYYY/MM/
logs/app/
logs/uds/
logs/can-trace/
exports/
temp/
```

## 통신 모니터링

통신 모니터링은 공통 도구다. MVP는 CAN Trace만 제공한다.

- timestamp
- direction
- CAN ID
- DLC
- data bytes
- pause/resume
- clear
- ID filter

고속 프레임에서도 UI가 멈추지 않도록 다음 원칙을 적용한다.

- 수신 thread와 UI thread 분리
- bounded ring buffer 사용
- 화면 가상화 적용
- UI 업데이트 batching 적용
- pause 상태에서도 내부 trace 정책은 명확히 유지

## 테스트 전략

TDD를 기본으로 한다.

### Unit Tests
- CAN 설정 검증
- UDS response 판정
- DTC P-Code 매핑
- second -> h/m/s 표시 변환
- 시스템 정보 DID 파싱
- 자동검사 판정
- 강제구동 순차 실행 정책

### Integration Tests
- Simulator 기반 전체 자동검사 성공/실패 흐름
- Kvaser/PEAK 장비 검색과 연결 상태 변화
- ISO-TP single-frame/multi-frame 송수신
- DTC JSON 로딩
- PDF/JSON 저장 경로 생성

### Manual Tests
- 실제 USB CAN 장비 연결/해제
- 실제 UDS request 송신/response 수신
- 자동검사 중 장비 해제
- 통신 모니터링 고속 trace 표시
