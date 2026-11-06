# v3.27.0 빌드·검사 자료

이 폴더를 /workspace/little-tone-v3.27.0-validation에, 이전 일반 게임 ZIP을 /workspace/little-tone-v3.26.0-web에 풀어 둔 환경을 기준으로 build.py를 실행합니다. ImageMagick과 Python이 필요합니다. fonts.py는 fontTools·Brotli와 이전 폰트 원본 경로를 실행 환경에 맞춰 지정합니다.

source-art에는 새 진열대 앞뒤 원화가 있습니다. cases.js는 실제 비율·진열·선택 판정, custom.js는 색상 합성과 문양 범위, events.js는 이미지 준비 후 캐시 갱신을 처리합니다. 최종 실행 소스 전체는 일반 게임 ZIP의 app-*.js에 포함됩니다.

검사 .cjs는 Chromium·Playwright와 /workspace의 이전 버전 검사 픽스처 경로를 사용합니다. 해당 의존성·경로를 조정한 뒤 실행하세요. extended-display-save.json은 검사 전용이며 일반 게임 ZIP에는 포함하지 않습니다.

후반 경제 검사는 long.cjs late new 45 17,2026,731로 실행했습니다. 자세한 결과와 한계는 상위 VALIDATION-v3.27.0.json을 참고하세요.
