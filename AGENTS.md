# 프로젝트: EOL Diagnostic Tester

이 문서는 이 저장소에서 작업하는 agent의 최상위 행동 규칙이다. 이 프로젝트는 양산 현장에서 실제 장비와 통신하는 EOL/진단 프로그램이므로, 빠른 구현보다 정확성, 재현성, 안전한 실패 처리를 우선한다.

## 규칙 우선순위
- CRITICAL 규칙은 편의, 속도, 임시 구현, UI 편의성보다 우선한다.
- 판단 기준은 `AGENTS.md` -> `docs/ADR.md` -> `docs/ARCHITECTURE.md` -> `docs/PRD.md` -> `docs/UI_GUIDE.md` 순서로 확인한다.
- 문서끼리 충돌하거나 요구사항 해석이 둘 이상 가능하면 조용히 선택하지 말고 사용자에게 쟁점을 제시한다.
- 사용자 지시가 문서의 CRITICAL 규칙과 충돌하면 충돌 내용을 설명하고 확인을 받은 뒤 진행한다.
- 확인되지 않은 제품 사양, UDS DID, CAN ID, DTC mapping, 장비 SDK 동작은 추측해서 구현하지 않는다.

## 기술 스택
- 플랫폼/UI: Windows 데스크톱, .NET WPF
- 언어/런타임: C# / .NET
- 아키텍처: MVVM + App, Application, Domain, Infrastructure 계층 구조
- 통신/장비: UDS on CAN, Kvaser CANlib, PEAK PCAN-Basic, Simulator
- 테스트: .NET 단위 테스트, Python harness 테스트

## 아키텍처 헌법
- CRITICAL: UI 계층은 CAN frame, UDS byte, SID, DID, CAN ID, ISO-TP frame, Vendor SDK handle을 직접 만들거나 해석하지 않는다.
- CRITICAL: UI 계층은 Application 계층의 workflow, use case, diagnostic service interface만 호출한다.
- CRITICAL: UI 계층은 Kvaser/PEAK/Simulator 차이를 알면 안 된다. 장비별 차이는 Infrastructure adapter 내부에 둔다.
- CRITICAL: 통신 계층은 UI 상태, ViewModel, WPF 타입에 의존하지 않는다.
- CRITICAL: 수동 검사와 자동 검사는 같은 Diagnostic Service/Application use case를 재사용한다. UI 버튼마다 별도 진단 로직을 중복 구현하지 않는다.
- CRITICAL: 실제 Kvaser/PEAK USB CAN 장비 지원은 MVP 핵심 요구사항이다. Simulator는 개발과 테스트 보조용이며 실제 장비 흐름을 대체하지 않는다.
- CRITICAL: 모든 장기 작업은 async와 cancellation 기반으로 구현한다. 장비 연결 해제 시 진행 중 작업을 안전하게 중단할 수 있어야 한다.
- CRITICAL: CAN Setting은 설정 영역에 둔다. 검사 준비 화면에는 장비 상태와 필요한 이동 경로만 제공하고 전체 CAN 설정을 펼쳐 놓지 않는다.
- App 계층은 WPF Views, ViewModels, navigation, styling을 담당한다.
- Application 계층은 use case, session 상태, 검사 실행, cancellation, report 생성 요청을 담당한다.
- Domain 계층은 순수 도메인 모델, UDS 결과 모델, DTC 모델, validation, judging rule을 담당한다.
- Infrastructure 계층은 Kvaser/PEAK/Simulator 장비, ISO-TP, UDS Client, ProgramData 파일 입출력을 담당한다.

## 구현 전 사고 규칙
- 추측하지 않는다. 불확실한 가정은 명시하고, 위험한 가정이면 질문한다.
- 여러 해석이 가능하면 선택지를 제시하고 각각의 영향 범위를 말한다.
- 더 단순한 방법이 있으면 언급한다. 필요한 경우 사용자 요청의 위험한 방향에 반박한다.
- 이해가 안 되는 부분을 숨기지 않는다. 무엇이 모호한지 말하고 멈춘다.
- 작업이 여러 단계라면 짧은 계획을 세우고 각 단계의 검증 방법을 정한다.

## 단순성 원칙
- 요청한 기능을 해결하는 데 필요한 최소한의 코드를 작성한다.
- 요청하지 않은 기능, 설정 가능성, 확장성, 추상화를 만들지 않는다.
- 일회성 코드에는 추상화를 추가하지 않는다.
- 확인되지 않은 시나리오나 불가능한 경로에 대한 과도한 오류 처리를 넣지 않는다.
- 새 abstraction은 중복 제거, 경계 보호, 테스트 용이성 중 하나를 분명히 개선할 때만 추가한다.

## 수술적 변경 원칙
- 꼭 필요한 파일과 코드만 변경한다.
- 인접한 코드, 주석, 서식, 이름을 이유 없이 개선하지 않는다.
- 정상 동작하는 기존 코드를 요청 없이 리팩터링하지 않는다.
- 기존 스타일, naming, folder boundary를 따른다.
- 관련 없는 unused code를 발견해도 삭제하지 말고 필요한 경우 언급만 한다.
- 본인 변경으로 생긴 unused import, dead variable, 깨진 참조는 직접 정리한다.
- 변경된 모든 줄은 사용자 요청 또는 검증 실패 해결과 직접 연결되어야 한다.

## 테스트와 검증
- CRITICAL: 새 기능은 테스트를 먼저 작성하고, 실패하는 테스트를 통과시키는 구현을 작성한다. TDD를 기본으로 한다.
- CRITICAL: 버그 수정은 가능하면 재현 테스트를 먼저 작성한다.
- 기존 테스트를 깨뜨린 상태로 작업을 완료하지 않는다.
- Unit test는 실제 CAN 장비 없이 실행 가능해야 한다.
- 실제 Kvaser/PEAK 장비가 필요한 테스트는 manual 또는 integration test로 분리한다.
- Simulator는 deterministic해야 하며, 테스트 결과가 시간/순서/환경에 불안정하게 의존하면 안 된다.
- UDS positive response, negative response, timeout 판정은 테스트로 보호한다.
- 테스트를 실행하지 못했으면 최종 응답에 이유와 남은 위험을 명확히 적는다.

## 하드웨어와 현장 안전
- 장비 연결 해제, timeout, negative response는 성공처럼 처리하지 않는다. 명확한 NG, 중단, 재시도 가능 상태 중 하나로 표현한다.
- 예외를 삼키고 정상 결과처럼 반환하지 않는다.
- `.Result`, `.Wait()` 같은 sync-over-async 패턴을 사용하지 않는다.
- 작업자 화면에는 CAN/UDS 세부 지식을 과도하게 노출하지 않는다.
- trace/log는 장애 분석에 충분해야 하지만, UI 흐름을 복잡하게 만들면 안 된다.
- ProgramData, CAN ID, DID, DTC mapping, vendor path를 임의로 하드코딩하지 않는다. 문서화된 설정 또는 Domain/Application 모델을 통해 관리한다.

## 데이터와 설정
- 설정 파일은 사람이 검토할 수 있는 구조를 유지하고, 필드 의미가 불명확하면 문서 또는 타입으로 설명한다.
- 기존 설정/리포트/로그 파일 형식을 바꿀 때는 backward compatibility 또는 migration 방안을 고려한다.
- VIN, 작업자명, 검사 결과, trace log처럼 현장 데이터에 가까운 값은 테스트 fixture와 실제 데이터가 섞이지 않게 한다.
- 리포트와 export 결과는 재현 가능해야 한다. 같은 입력과 같은 검사 결과는 같은 판정과 같은 핵심 리포트 내용을 만들어야 한다.

## UI와 작업자 경험
- 작업자용 화면은 반복 작업에 최적화한다. 장비 상태, VIN, 진행 상태, 결과 판정이 빠르게 읽혀야 한다.
- 위험하거나 되돌리기 어려운 동작은 상태와 결과를 명확히 표시한다.
- 오류 메시지는 작업자가 다음 행동을 알 수 있게 작성한다. 내부 exception 문자열만 그대로 노출하지 않는다.
- 관리자/개발자용 설정 화면과 작업자 검사 흐름을 섞지 않는다.
- UI는 `docs/UI_GUIDE.md`의 Windows 11/Fluent 스타일 방향을 따른다.

## 완료 기준
- 관련 요구사항과 ADR/Architecture 규칙을 확인했다.
- 관련 테스트를 추가하거나 수정했고, 가능한 검증 명령을 실행했다.
- App/Application/Domain/Infrastructure 경계를 위반하지 않았다.
- cancellation, 장비 연결 해제, timeout 영향이 있는 변경이면 해당 흐름을 검토했다.
- 설정, 로그, 리포트, export 경로를 바꾸는 경우 저장 위치와 기존 데이터 호환성을 확인했다.
- 최종 응답에는 변경 요약, 실행한 검증, 실행하지 못한 검증을 포함한다.

## 개발 프로세스
- 구현 전 `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md`, `docs/UI_GUIDE.md`에서 관련 요구사항과 결정사항을 확인한다.
- 변경 범위는 요청된 기능과 관련 모듈로 제한한다.
- commit 메시지는 conventional commits 형식을 따른다. 예: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.

## 현재 사용 가능한 명령어
```bash
python -m pytest scripts/test_execute.py --basetemp=.pytest_tmp -o cache_dir=.pytest_cache
python scripts/execute.py {task-name}
python scripts/execute.py {task-name} --push
```

.NET 앱 소스가 생성된 뒤에는 프로젝트 구조에 맞는 build/test 명령을 사용한다.

```bash
dotnet build
dotnet test
dotnet run --project src/EolDiagnosticTester.App
```
