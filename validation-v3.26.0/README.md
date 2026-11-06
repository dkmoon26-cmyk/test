# v3.26.0 편집·검사 자료

게임 실행용 파일은 상위의 일반 게임 ZIP에 있습니다. 이 폴더의 저장 JSON은 자동 검사 전용이며 배포 게임 ZIP에는 포함하지 않았습니다.

source-art에는 새로 제작한 24종 앞뒤 바디 시트, 하드웨어, 문양, 재질의 고해상도 PNG가 있습니다. art.json은 추출 좌표·마스크 메타데이터입니다.

빌드는 이전 일반 게임 ZIP을 /workspace/little-tone-v3.25.0-web에 풀고 이 폴더를 /workspace/little-tone-v3.26.0-validation에 둔 환경을 기준으로 합니다. premium_art.py → build.py → fonts.py 순서로 실행합니다. ImageMagick, Python fontTools·Brotli가 필요합니다. fonts.py의 원본 폰트 경로와 Python 의존성 경로는 실행 환경에 맞게 지정하세요. PNG 원본이 source-art에 있으면 premium-sources.json에 기록된 생성 당시 임시 경로는 필요하지 않습니다.

브라우저 검사는 Chromium과 Playwright가 설치된 경로를 각 .cjs 파일 상단에서 지정합니다. module.cjs는 옵션·문양·실제 제작을, sales.cjs는 새 상품의 실제 판매를, modular-resume.cjs는 지연 로딩 상태의 첫 이어하기 표시를 검사합니다. 여러 검사를 동시에 실행할 경우 각 서버 포트가 달라야 합니다.

경제 장기 검사는 long.cjs growth new 90 17,2026,731 및 long.cjs late new 45 17,2026,731로 실행했습니다. 결과·검사 범위·한계는 상위 VALIDATION-v3.26.0.json을 참고하세요.
