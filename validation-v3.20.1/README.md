v3.20.1 정리 및 검증

원본 /workspace/little-tone-v3.20.0-web 및 /workspace/little-tone-v3.20.0-test-web을 보존한 상태에서 python build.py로 정리본을 만듭니다. Node.js·Playwright·/usr/bin/chromium을 사용하며 경로는 각 환경에 맞게 조정할 수 있습니다.
verify-cleanup.cjs는 audit.cjs가 생성한 캐릭터 포즈 그림과 현재 게임 이미지를 픽셀 단위로 비교합니다. 별도 AUDIT-v3.20.1.md의 4건은 수정 범위에 포함하지 않았습니다.
