# Reproduction notes

Game sources are inside the normal ZIP. These scripts build from the v3.23.1 release extracted to `/workspace/little-tone-v3.23.1-web`; output is `/workspace/little-tone-v3.24.0-web`.

The authoring scripts use Python 3 with fontTools and Brotli (see requirements.txt), Node.js, Playwright and Chromium `/usr/bin/chromium`. Their local runtime paths and `/workspace` paths reflect the cloud workspace and can be adjusted for another machine. Use a local HTTP server; browser scheduling and image decode are asynchronous. Tests that suppress animation frames must use timer-based polling and await required image gates after loading a save.

`build.py` → `fonts.py` produces the app. `test.cjs` writes the core fixture needed by `sales.cjs`. Run the other browser drivers after building; do not rebuild while tests are using the files. Reports are stored beside the scripts. `package.py` verifies reports, builds the ZIP/manifest and copies release files to `/workspace/test`.

`startup.cjs` additionally uses the existing v3.23.1 prop-mask fixture and the v3.23.0 baseline; `loading.cjs` compares the extracted v3.23.1 directory. Existing historical validation scripts remain in their versioned directories. No test save is shipped in the game ZIP.
