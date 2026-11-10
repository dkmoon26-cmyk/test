# v3.28.0 검사

실제 배포 폴더를 HTTP 정적 서버로 제공하고 Chromium/Playwright로 검사했습니다. 상세 결과는 루트 VALIDATION-v3.28.0.json 및 각 *-results.json을 참고하세요. ui.cjs의 화면 검사는 실제 메뉴 열기·주문·제작 조작·정산과 다음 날·저장 가져오기를 포함합니다. dialogs.cjs의 보조 창 검사는 DOM에 존재하는 창을 열어 공통 색상·글꼴·범위를 검사합니다.

스크립트의 /workspace 경로와 Chromium, Playwright 경로는 실행 환경에 맞춰 수정해야 합니다. 구형 저장 회귀 검사는 이전 validation 폴더의 fixture를 참조합니다. 테스트 세이브는 일반 게임 ZIP에 포함하지 않았습니다. 파일 직접 실행은 관리자 정책으로 차단되어 검사하지 못했습니다.
