"""Static checks for the landing page: broken local refs, bad anchors, missing alt text, unused images."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.errors = [], set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("src", "href"):
            if a.get(key):
                self.refs.append(a[key])
        if a.get("srcset"):
            self.refs += [c.strip().split()[0] for c in a["srcset"].split(",") if c.strip()]
        if tag == "img" and "alt" not in a:
            self.errors.append(f"<img src={a.get('src')!r}> has no alt text")


def main():
    errors, used = [], set()
    for page in sorted(ROOT.glob("*.html")):
        p = Page()
        p.feed(page.read_text(encoding="utf-8"))
        errors += [f"{page.name}: {e}" for e in p.errors]
        for ref in p.refs:
            u = urlsplit(ref)
            if u.scheme or ref.startswith("//"):
                continue
            if not u.path:
                if u.fragment and u.fragment not in p.ids:
                    errors.append(f"{page.name}: anchor #{u.fragment} has no matching id")
                continue
            target = (page.parent / unquote(u.path)).resolve()
            used.add(target)
            if not target.is_file():
                errors.append(f"{page.name}: missing file {ref}")

    for css in ROOT.glob("*.css"):
        for ref in re.findall(r"url\(\s*['\"]?([^'\")]+)", css.read_text(encoding="utf-8")):
            if urlsplit(ref).scheme:
                continue
            target = (css.parent / ref).resolve()
            used.add(target)
            if not target.is_file():
                errors.append(f"{css.name}: missing file {ref}")

    for img in sorted((ROOT / "img").iterdir()):
        if img.resolve() not in used:
            errors.append(f"unused image img/{img.name} (delete it or reference it)")

    for e in errors:
        print(f"::error::{e}")
    print(f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
