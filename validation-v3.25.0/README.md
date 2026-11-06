# Reproduction notes

The normal ZIP contains editable game HTML/JS/CSS and all runtime art. These authoring and validation scripts use the cloud workspace paths, Node.js, Playwright and Chromium `/usr/bin/chromium`; adjust paths for another machine.

Extract the v3.24.0 release to `/workspace/little-tone-v3.24.0-web`. Use Python 3 with fontTools/Brotli and ImageMagick. `source-art/` contains the generated original transparent sheets. `art.py` extracts the cells with alpha cleanup, `build.py` builds from the previous release and packs front/rear views, and `fonts.py` subsets the complete UI character set using the full fonts from the v3.23.1 release. Its optional Python dependency directory reflects this workspace; install requirements normally elsewhere.

Run browser tests after the final build and fonts step. Do not rebuild during tests. The prior v3.24.0 core fixture is created by that version's `test.cjs`; it is the compatibility input for the new tests. The loading comparison also uses the extracted v3.23.1 release. Browser drivers serve files over localhost. Tests that suppress animation frames use timer polling and await image gates.

`core.cjs`: pricing, crafting options, transactions and actual VIP two-purchase reload. `production.cjs`: four new models manufactured across actual business days and restored. `orders.cjs`: one-unit automatic allocation, pending-order rush conversion and deterministic probability samples. `ui.cjs`: real wall click/move/reload, three props, fractional affection, staff roaming and viewport layouts. `resume.cjs`: truly cold legacy resume, actual furniture pixels and distinct filled/empty custom/VIP composite pixels. `startup.cjs`: normal/degraded artwork, PC/mobile complete tutorial and viewport zoom. `long.cjs` + `long-harness.js`: natural growth and funded late runs. `package.py` asserts reports, checks referenced files, hashes every game file and builds the ZIP.

The final composite-cache invalidation and rounded control styling did not change economic rules; focused tests were rerun after those refinements. Runtime saves/test editions are not included in the normal game ZIP.
