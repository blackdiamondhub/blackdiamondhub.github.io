# blackdiamondhub.github.io

Public landing page for [Black Diamond Hub](https://github.com/blackdiamondhub/BlackDiamondHub).
Static HTML/CSS served by GitHub Pages from `main`. Screenshots in `img/` are from the Sun Peaks hub.

CI (`.github/workflows/check.yml`) runs `tools/check_site.py`: no missing local files, no dangling `#anchors`, every `<img>` has alt text, and no unused images in `img/`.
