#!/usr/bin/env python3
"""Generate the case-study pages + works grid for the Tuqa Lynch portfolio.

Layout (width / alignment of every image block) is transcribed from the live
Framer site tuqalynch.com, measured at a 1440px viewport and normalised to the
content column.  Downloads the exact images into assets/img/<slug>/.
"""
import subprocess, html, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG_ROOT = ROOT / "assets" / "img"
WORK_DIR = ROOT / "work"
FRAMER = "https://framerusercontent.com/images/"
MAXW = 2000
# Bump on any asset swap under the same filename (gen.py always numbers a
# project's local images 01.png, 02.png, ... in flow order) — without this,
# browsers that already fetched the old bytes at that exact path keep
# serving them from cache instead of the replacement. Also drives the
# style.css/main.js cache-busting query strings.
VERSION = "111"

_dims_cache = {}


def dims(path):
    """(width, height) of a local image, read once and cached. Embedding real
    intrinsic size as width/height attributes lets the browser reserve the
    exact box before the (lazy-loaded) image arrives, instead of the page
    reflowing under the scroll position as each one pops in."""
    if path is None:
        return None
    key = str(path)
    if key not in _dims_cache:
        try:
            with Image.open(path) as im:
                _dims_cache[key] = im.size
        except Exception:
            _dims_cache[key] = None
    return _dims_cache[key]


def dim_attrs(path):
    d = dims(path)
    return f' width="{d[0]}" height="{d[1]}"' if d else ""


def R(items, cap=None, w=100, align="left", cols=None, mobile_cols=None):
    """A media row. items: list of 'hash.ext' or ('hash.ext','caption').
    w: width as % of the content column. align: left|center|right.
    cols: images across (default = len(items)). mobile_cols: override how
    many sit side by side at the phone breakpoint (default: the generic
    640px collapse — 2/3/4/5 across all become 2; pass 1 to stack fully, or
    the same number as cols to force it to stay side by side)."""
    return ("row", items, cap, {"w": w, "align": align, "cols": cols, "mobile_cols": mobile_cols})


def HERO(h, cap=None, w=100, align="left"):
    return ("hero", h, cap, {"w": w, "align": align})


def VIDEO(src, cap=None, w=100, align="left"):
    """A single local video file (not Framer-hosted, used as-is) shown the
    same way a one-image R() row is — muted/looping/autoplaying."""
    return ("video", src, cap, {"w": w, "align": align})


def RAW(html_block, w=100, align="left"):
    """A hand-built HTML block (e.g. a lifted SVG animation) dropped in
    verbatim — not escaped, not routed through grab()."""
    return ("raw", html_block, None, {"w": w, "align": align})


# flow kinds: HERO(...) · ("h","Heading") · ("p","para") · ("tags","a · b") ·
#             ("note","small line") · R(...)

# The 3 looping SVG animations from the live Azaz Labs page (lifted verbatim —
# self-contained SMIL/CSS-keyframe markup, no external JS needed to animate).
AZAZ_ANIMATIONS_HTML = """<div class="cs-anim-card">
<div style="display:flex;justify-content:center;align-items:center;padding:1rem;background:rgba(0,0,0,0)"><svg viewBox="0 0 500 280" style="width:100%;max-width:560px" xmlns="http://www.w3.org/2000/svg"><path d="M40 172 Q250 230 460 172" fill="none" stroke="#ffffff" stroke-width="0.3" opacity="0.08"></path><g><line x1="62" y1="180" x2="250" y2="52" stroke="#ffffff" stroke-width="0.5" opacity="0.12"></line><line x1="62" y1="180" x2="250" y2="52" stroke="#ffffff" stroke-width="0.75" stroke-dasharray="6 114"><animate attributeName="stroke-dashoffset" values="120;0;0" keyTimes="0;0.7;1" dur="4s" begin="0s" calcMode="spline" keySplines="0.4 0 0.6 1;0 0 1 1" repeatCount="indefinite"></animate><animate attributeName="opacity" values="0;0.55;0.55;0" keyTimes="0;0.05;0.68;0.75" dur="4s" begin="0s" repeatCount="indefinite"></animate></line></g><g><line x1="148" y1="196" x2="250" y2="52" stroke="#ffffff" stroke-width="0.5" opacity="0.12"></line><line x1="148" y1="196" x2="250" y2="52" stroke="#ffffff" stroke-width="0.75" stroke-dasharray="6 114"><animate attributeName="stroke-dashoffset" values="120;0;0" keyTimes="0;0.7;1" dur="4s" begin="0.7s" calcMode="spline" keySplines="0.4 0 0.6 1;0 0 1 1" repeatCount="indefinite"></animate><animate attributeName="opacity" values="0;0.55;0.55;0" keyTimes="0;0.05;0.68;0.75" dur="4s" begin="0.7s" repeatCount="indefinite"></animate></line></g><g><line x1="232" y1="204" x2="250" y2="52" stroke="#ffffff" stroke-width="0.5" opacity="0.12"></line><line x1="232" y1="204" x2="250" y2="52" stroke="#ffffff" stroke-width="0.75" stroke-dasharray="6 114"><animate attributeName="stroke-dashoffset" values="120;0;0" keyTimes="0;0.7;1" dur="4s" begin="1.4s" calcMode="spline" keySplines="0.4 0 0.6 1;0 0 1 1" repeatCount="indefinite"></animate><animate attributeName="opacity" values="0;0.55;0.55;0" keyTimes="0;0.05;0.68;0.75" dur="4s" begin="1.4s" repeatCount="indefinite"></animate></line></g><g><line x1="320" y1="204" x2="250" y2="52" stroke="#ffffff" stroke-width="0.5" opacity="0.12"></line><line x1="320" y1="204" x2="250" y2="52" stroke="#ffffff" stroke-width="0.75" stroke-dasharray="6 114"><animate attributeName="stroke-dashoffset" values="120;0;0" keyTimes="0;0.7;1" dur="4s" begin="2.1s" calcMode="spline" keySplines="0.4 0 0.6 1;0 0 1 1" repeatCount="indefinite"></animate><animate attributeName="opacity" values="0;0.55;0.55;0" keyTimes="0;0.05;0.68;0.75" dur="4s" begin="2.1s" repeatCount="indefinite"></animate></line></g><g><line x1="406" y1="196" x2="250" y2="52" stroke="#ffffff" stroke-width="0.5" opacity="0.12"></line><line x1="406" y1="196" x2="250" y2="52" stroke="#ffffff" stroke-width="0.75" stroke-dasharray="6 114"><animate attributeName="stroke-dashoffset" values="120;0;0" keyTimes="0;0.7;1" dur="4s" begin="2.8s" calcMode="spline" keySplines="0.4 0 0.6 1;0 0 1 1" repeatCount="indefinite"></animate><animate attributeName="opacity" values="0;0.55;0.55;0" keyTimes="0;0.05;0.68;0.75" dur="4s" begin="2.8s" repeatCount="indefinite"></animate></line></g><g><line x1="438" y1="180" x2="250" y2="52" stroke="#ffffff" stroke-width="0.5" opacity="0.12"></line><line x1="438" y1="180" x2="250" y2="52" stroke="#ffffff" stroke-width="0.75" stroke-dasharray="6 114"><animate attributeName="stroke-dashoffset" values="120;0;0" keyTimes="0;0.7;1" dur="4s" begin="3.5s" calcMode="spline" keySplines="0.4 0 0.6 1;0 0 1 1" repeatCount="indefinite"></animate><animate attributeName="opacity" values="0;0.55;0.55;0" keyTimes="0;0.05;0.68;0.75" dur="4s" begin="3.5s" repeatCount="indefinite"></animate></line></g><g><text x="250" y="22" text-anchor="middle" fill="#ffffff" font-size="7.5" font-weight="600" opacity="0.55" letter-spacing="0.12em" style="font-family:inherit">FUND</text><circle cx="250" cy="44" fill="none" stroke="#ffffff" stroke-width="0.5"><animate attributeName="r" values="8;22;8" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0;0.18;0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle><circle cx="250" cy="44" fill="#ffffff"><animate attributeName="r" values="6;8;6" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0.55;0.9;0.55" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle></g><g><text x="62" y="202" text-anchor="middle" fill="#ffffff" font-size="7" opacity="0.3" letter-spacing="0.1em" style="font-family:inherit">PORTCO A</text><circle cx="62" cy="180" fill="none" stroke="#ffffff" stroke-width="0.5"><animate attributeName="r" values="3.5;10;3.5" dur="4s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0;0.14;0" dur="4s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle><circle cx="62" cy="180" fill="#ffffff"><animate attributeName="r" values="3;3.8;3" dur="4s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0.3;0.65;0.3" dur="4s" begin="0s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle></g><g><text x="148" y="218" text-anchor="middle" fill="#ffffff" font-size="7" opacity="0.3" letter-spacing="0.1em" style="font-family:inherit">PORTCO B</text><circle cx="148" cy="196" fill="none" stroke="#ffffff" stroke-width="0.5"><animate attributeName="r" values="3.5;10;3.5" dur="4s" begin="0.7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0;0.14;0" dur="4s" begin="0.7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle><circle cx="148" cy="196" fill="#ffffff"><animate attributeName="r" values="3;3.8;3" dur="4s" begin="0.7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0.3;0.65;0.3" dur="4s" begin="0.7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle></g><g><text x="232" y="226" text-anchor="middle" fill="#ffffff" font-size="7" opacity="0.3" letter-spacing="0.1em" style="font-family:inherit">PORTCO C</text><circle cx="232" cy="204" fill="none" stroke="#ffffff" stroke-width="0.5"><animate attributeName="r" values="3.5;10;3.5" dur="4s" begin="1.4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0;0.14;0" dur="4s" begin="1.4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle><circle cx="232" cy="204" fill="#ffffff"><animate attributeName="r" values="3;3.8;3" dur="4s" begin="1.4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0.3;0.65;0.3" dur="4s" begin="1.4s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle></g><g><text x="320" y="226" text-anchor="middle" fill="#ffffff" font-size="7" opacity="0.3" letter-spacing="0.1em" style="font-family:inherit">PORTCO D</text><circle cx="320" cy="204" fill="none" stroke="#ffffff" stroke-width="0.5"><animate attributeName="r" values="3.5;10;3.5" dur="4s" begin="2.1s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0;0.14;0" dur="4s" begin="2.1s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle><circle cx="320" cy="204" fill="#ffffff"><animate attributeName="r" values="3;3.8;3" dur="4s" begin="2.1s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0.3;0.65;0.3" dur="4s" begin="2.1s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle></g><g><text x="406" y="218" text-anchor="middle" fill="#ffffff" font-size="7" opacity="0.3" letter-spacing="0.1em" style="font-family:inherit">PORTCO E</text><circle cx="406" cy="196" fill="none" stroke="#ffffff" stroke-width="0.5"><animate attributeName="r" values="3.5;10;3.5" dur="4s" begin="2.8s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0;0.14;0" dur="4s" begin="2.8s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle><circle cx="406" cy="196" fill="#ffffff"><animate attributeName="r" values="3;3.8;3" dur="4s" begin="2.8s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0.3;0.65;0.3" dur="4s" begin="2.8s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle></g><g><text x="438" y="202" text-anchor="middle" fill="#ffffff" font-size="7" opacity="0.3" letter-spacing="0.1em" style="font-family:inherit">PORTCO F</text><circle cx="438" cy="180" fill="none" stroke="#ffffff" stroke-width="0.5"><animate attributeName="r" values="3.5;10;3.5" dur="4s" begin="3.5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0;0.14;0" dur="4s" begin="3.5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle><circle cx="438" cy="180" fill="#ffffff"><animate attributeName="r" values="3;3.8;3" dur="4s" begin="3.5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate><animate attributeName="opacity" values="0.3;0.65;0.3" dur="4s" begin="3.5s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"></animate></circle></g></svg></div>
<div style="position:relative;height:280px;background:rgba(0,0,0,0);overflow:hidden;display:flex;justify-content:center;align-items:center"><style>@keyframes personFade{0%,100%{opacity:.08}50%{opacity:.75}}</style><svg viewBox="0 0 300 280" style="display:block;width:100%;height:100%" xmlns="http://www.w3.org/2000/svg"><g transform="translate(150, 60)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 0s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(150, 145)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 0.5s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(100, 145)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 0.8s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(200, 145)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 0.8s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(150, 230)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 1s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(100, 230)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 1.3s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(200, 230)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 1.3s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(50, 230)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 1.6s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g><g transform="translate(250, 230)" fill="#ffffff" style="animation:personFade 3.5s ease-in-out 1.6s infinite"><circle cx="0" cy="-15" r="10"></circle><path d="M -18 20 C -18 2 -12 -6 0 -6 C 12 -6 18 2 18 20 Z"></path></g></svg></div>
<div style="width:100%;background:rgb(17,17,17)"><svg viewBox="0 0 600 422" width="100%" style="display:block;overflow:visible"><line x1="8" y1="145" x2="592" y2="145" stroke="#2C2C2C" stroke-width="1" stroke-dasharray="4 4"></line><line x1="8" y1="283" x2="592" y2="283" stroke="#2C2C2C" stroke-width="1" stroke-dasharray="4 4"></line><g transform="translate(222 55) rotate(-7)"><g><rect x="-35" y="-29" width="70" height="58" fill="none" stroke="#5D5D5D" stroke-width="1.2" rx="2"></rect><line x1="-35" y1="-19" x2="35" y2="-19" stroke="#5D5D5D" stroke-width="1.2"></line><line x1="-29" y1="-4.64" x2="29" y2="-4.64" stroke="#5D5D5D" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="6.96" x2="29" y2="6.96" stroke="#5D5D5D" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="18.56" x2="29" y2="18.56" stroke="#5D5D5D" stroke-width="1" stroke-opacity="0.45"></line></g></g><g transform="translate(274 55) rotate(4)"><g><rect x="-35" y="-29" width="70" height="58" fill="none" stroke="#737373" stroke-width="1.2" rx="2"></rect><line x1="-35" y1="-19" x2="35" y2="-19" stroke="#737373" stroke-width="1.2"></line><line x1="-29" y1="-4.64" x2="29" y2="-4.64" stroke="#737373" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="6.96" x2="29" y2="6.96" stroke="#737373" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="18.56" x2="29" y2="18.56" stroke="#737373" stroke-width="1" stroke-opacity="0.45"></line></g></g><g transform="translate(326 55) rotate(-3)"><g><rect x="-35" y="-29" width="70" height="58" fill="none" stroke="#494949" stroke-width="1.2" rx="2"></rect><line x1="-35" y1="-19" x2="35" y2="-19" stroke="#494949" stroke-width="1.2"></line><line x1="-29" y1="-4.64" x2="29" y2="-4.64" stroke="#494949" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="6.96" x2="29" y2="6.96" stroke="#494949" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="18.56" x2="29" y2="18.56" stroke="#494949" stroke-width="1" stroke-opacity="0.45"></line></g></g><g transform="translate(378 55) rotate(5)"><g><rect x="-35" y="-29" width="70" height="58" fill="none" stroke="#646464" stroke-width="1.2" rx="2"></rect><line x1="-35" y1="-19" x2="35" y2="-19" stroke="#646464" stroke-width="1.2"></line><line x1="-29" y1="-4.64" x2="29" y2="-4.64" stroke="#646464" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="6.96" x2="29" y2="6.96" stroke="#646464" stroke-width="1" stroke-opacity="0.45"></line><line x1="-29" y1="18.56" x2="29" y2="18.56" stroke="#646464" stroke-width="1" stroke-opacity="0.45"></line></g></g><path d="M 222 84 C 222 119, 300 172, 300 184" fill="none" stroke="#B0B0B0" stroke-width="1.2"></path><path d="M 274 84 C 274 119, 300 172, 300 184" fill="none" stroke="#B0B0B0" stroke-width="1.2"></path><path d="M 326 84 C 326 119, 300 172, 300 184" fill="none" stroke="#B0B0B0" stroke-width="1.2"></path><path d="M 378 84 C 378 119, 300 172, 300 184" fill="none" stroke="#B0B0B0" stroke-width="1.2"></path><g transform="translate(200 184)"><g><rect width="200" height="60" fill="#1B1B1B" rx="3"></rect><text x="100" y="30" text-anchor="middle" dominant-baseline="central" fill="#FFC760" font-size="24" font-weight="700" font-family="system-ui, -apple-system, \'Helvetica Neue\', sans-serif" letter-spacing="6">AZAZ</text></g></g><path d="M 300 244 L 300 298" fill="none" stroke="#B0B0B0" stroke-width="1.2"></path><g transform="translate(97 298)"><g><rect width="130" height="44" fill="none" stroke="#505050" stroke-width="1" rx="2"></rect><line x1="0" y1="10" x2="130" y2="10" stroke="#505050" stroke-width="0.75" stroke-opacity="0.5"></line><path d="M 7 30 L 20 22 L 33 28 L 46 17 L 59 25 L 72 14 L 85 23" fill="none" stroke="#545454" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"></path><circle cx="118" cy="24" r="4" fill="#CF4444"></circle><circle cx="116.5" cy="22.5" r="1.5" fill="rgba(255,255,255,0.3)"></circle></g></g><g transform="translate(235 298)"><g><rect width="130" height="44" fill="none" stroke="#505050" stroke-width="1" rx="2"></rect><line x1="0" y1="10" x2="130" y2="10" stroke="#505050" stroke-width="0.75" stroke-opacity="0.5"></line><rect x="7" y="25" width="64" height="9" fill="#383838" stroke="#505050" stroke-width="0.75" rx="1"></rect><rect x="71" y="25" width="50" height="9" fill="#545454" stroke="#686868" stroke-width="0.75" rx="1"></rect></g></g><g transform="translate(373 298)"><g><rect width="130" height="44" fill="none" stroke="#505050" stroke-width="1" rx="2"></rect><line x1="0" y1="10" x2="130" y2="10" stroke="#505050" stroke-width="0.75" stroke-opacity="0.5"></line><rect x="1" y="1" width="3" height="42" fill="#FFC760" rx="1"></rect></g></g></svg></div>
</div>"""


PROJECTS = [
 {
  "slug": "canada-water-library",
  "title": "Canada Water Library",
  "grid_label": "Brand identity  ·  Print  ·  Signage",
  "white_page": True,
  "flow": [
   HERO("85k9sdvKwGG53VC2FSoCtsI07s.jpg", "Brand book & assets"),
   ("h", "Overview"),
   ("p", "This project consists of a brand identity system for Canada Water Library governed by triangular marks derived from the angles of the building itself, and a colour palette sourced from the library’s material environment: the red of its timber bridge, the blues of the surrounding water, and the orange of the interior wood."),
   ("tags", "Brand identity  ·  Print  ·  Signage  ·  Editorial design  ·  Social media"),
   R([("cw-logo.png", "Logo"), ("gZh8WjtZhM8t598e5AqsfrEMoM.jpg", "Library Exterior")], cols=2),
   R(["8CplwnILsBU2NhQ6v0321pB8K5s.png"], "Brand guidelines"),
   R(["ZY5vHRPM0n06eficYs9TfxmiUc0.png"]),
   R([("EK0umuCOFMkxWdvIqPaZ4tENu6w.jpg", "Brand booklets"),
      ("Qxs2inOEIf79bdpGKhPyp3E1Jk.jpg", "Theatre tickets")], mobile_cols=1),
   R(["cw-photo-bus.jpg"], "Street bus advertising"),
   R(["696UUrCCL10cHGYVxmgXNEDrSQ.png", "MTnnFfoY22uUGBxR0ADca9hmoU.png",
      "dtx3LTsoozdYbt19NBVPlL3yM.png"], "Social media posts", mobile_cols=3),
   R(["ytGMHe1AMsv83zhT6HYnVC7IR5c.jpg"]),
   R(["DdrC9p3v1l2veE75EprzTtQXcc.jpg", "UoWC1dKZbZZfgDfMRCcrU4EhgBE.jpg"],
     "'About our Library' booklet"),
   R(["Dd64zAPEau3tPtYFv0I7eNyiy0k.png"]),
   R(["cw-photo-business-cards.jpg"], "Business cards"),
   R(["vsLqr6tDNVersIrx3dwsKmRA1MY.jpg", "cw-photo-booklet-spread2.jpg"],
     "Spreads from brand booklet", cols=2, mobile_cols=1),
   R(["HxRjXkheYSqiO8vzQrUubjOXOo.jpg"], "Laser cut entrance sign"),
   R(["cw-mockup-card.jpg"], "Business card", w=55, align="center"),
   ("h", "Process & experimentation"),
   ("p", "My process expanded from extracting the buildings’ ‘DNA’ by measuring various angles, which I thought would allow me to connect the architectural source to context such as the water and history. This allowed for infinite variations under the same systemic constraints."),
   R(["MAlDchCF4fBdidxZblApE0gh4n8.png"], w=63, align="right"),
   R(["vzKMu1W6a5oRNqDlDZCWH6g4wwY.png"], w=63, align="right"),
  ],
 },
 {
  "slug": "andromeda",
  "title": "Andromeda AI",
  "grid_label": "Brand identity  ·  Type  ·  Art direction",
  "white_page": True,
  "flow": [
   HERO("andromeda-hero-linkedin.png", "LinkedIn banner"),
   ("h", "Overview"),
   ("p", "Andromeda AI is a bespoke AI automation studio I co-founded, where I design both the client-facing products we build and the brand and website that represent the studio itself. I built the identity around the Andromeda name itself, using one saturated violet (#5D22D6), a halftone dot texture standing in for stellar dust, and a sharp four-point sparkle mark paired with Cabinet Grotesk and Erode type to give the brand a bolder, more graphic feel."),
   ("tags", "Brand identity  ·  Type design  ·  Art direction  ·  Print  ·  Social media"),
   ("note", "“We don't believe in one-size-fits-all automation.”"),
   R(["andromeda-lockup-light.png", "andromeda-lockup-dark.png"],
     "Wordmark lockup, light and dark", cols=2),
   R(["andromeda-poster.jpg", "andromeda-event-screen.jpg"],
     "In the wild: a poster and an event screen", cols=2, mobile_cols=1),
   R(["andromeda-type-display.png", "andromeda-type-text.png"],
     "Cabinet Grotesk for display, Erode for text", cols=2, mobile_cols=1),
   R([("andromeda-business-card.jpg", "Business card"), ("andromeda-appicon.jpg", "App icon")], cols=2, mobile_cols=1),
   R(["andromeda-palette.png"], "Colour palette", w=44, align="center"),
   R(["andromeda-merch.jpg"], "Merch: embroidered tee and cap"),
   R(["andromeda-social-posts.jpg"], "Social media posts"),
   VIDEO("assets/video/andromeda/site-walkthrough.mp4", "Site walkthrough"),
   R(["andromeda-social-tile.png", "andromeda-social-halftone.png"],
     "Social tile treatments", cols=2),
   R(["andromeda-mark-filled.png", "andromeda-mark-outline.png", "andromeda-mark-icon.png"],
     "The mark, in every version", cols=3, mobile_cols=3),
  ],
 },
 {
  "slug": "holistic-transformation-management",
  "title": "Holistic Transformation Management",
  "grid_label": "Brand identity · UI/UX · Product",
  "hero_video": "assets/video/holistic-transformation-management/hero.mp4",
  "grid_video": "assets/video/holistic-transformation-management/hero.mp4",
  "grid_still": "assets/img/holistic-transformation-management/thumb-logo.png",
  "flow": [
   HERO("hfbuvHbszQkGUeORzJdL8QLBlms.png"),
   ("h", "Overview"),
   ("p", "HTM is a full brand and web identity for a business transformation consultancy, built around a “holistic” positioning. The design channels that positioning visually to signal a firm that treats leadership and organisational health as inseparable from delivery, rather than a typical slide-deck consultancy."),
   ("tags", "Brand identity  ·  UI/UX  ·  Product design  ·  Web design  ·  Motion"),
   VIDEO("assets/video/holistic-transformation-management/mobile.mp4", "Mobile UI in motion"),
   ("h", "Home page"),
   ("p", "The key decision was to pair a restrained, rigorous typographic system with soft, organic imagery like flowing silk and fabric folds, so the identity itself embodies HTM's “holistic” positioning: structure and precision balanced against something more human and sensory. I led with a deep green giving the brand a calmer, more considered feel that signals long-term transformation rather than transactional advisory work."),
   RAW('<div class="cs-flush-band" style="background:#030F0F">'
       '<img src="../assets/img/holistic-transformation-management/colour-scheme.png?v={v}" alt="Colour palette">'
       '</div><p class="row-cap">Colour palette</p>'.format(v=VERSION)),
   R(["6RAewKElGp9GzGfgtbrHBw3pyKE.png", "ubUjkj5zEe87Wej71v9DBWbTT0.png",
      "7IPGFLUtn35kZ9INGuYj4ENs.png", "96FynJx03vGbs044IivbAJKLdRM.png",
      "xLyiFYz99CjmkPxfcihJET77zE.png", "besNuuGa4MjmEJu0xmUEXHHTYVA.png",
      "3uaaAYZbZ90VVcudqhmjUH4leU.png", "kXZKAAOUfkkWuhwQSrshbIMUw.png"],
     "Website mobile UI", cols=4),
   ("h", "About page"),
   ("p", "A consistent grid and generous section spacing keep each block distinct without turning into a wall of consultancy text, letting the structure itself signal the rigour and operational discipline HTM sells."),
   VIDEO("assets/video/holistic-transformation-management/scroll.mp4", "Full site scroll-through"),
   ("h", "Process & experimentation"),
   ("p", "Before any visual direction was locked in, I wireframed the site structure in Figma, testing different ways to organise HTM's three practices."),
   ("p", "Once the structure held, I ran parallel brand explorations from more traditional corporate photography through to the softer, organic visual language eventually chosen. Each round went back to the client for feedback, narrowing from broad concept options down to a single direction that balanced authority with HTM's “holistic,” human-centred positioning."),
   R(["a7jwgqNNquZKgPNNNJNDAcvm8m8.png"], "Wireframe", w=63, align="right"),
   R(["H5v5ZPxIvzIOwGXYQswEA3Iqw.png", "ukY0s8JINeBV3jGn7C2XTzj6Po.png",
      "SxvRevIrd6IRtOwTRFbg8blzMM.png"], "Initial identity concepts",
     w=57, align="right"),
  ],
 },
 {
  "slug": "azaz-labs",
  "title": "Azaz Labs",
  "grid_label": "Web · Product · UI/UX",
  "grid_video": "assets/video/azaz-labs/hero.mp4",
  "grid_video_loop": False,
  "grid_still": "assets/img/azaz-labs/01.png",
  "flow": [
   HERO("XYYdqZQNnCt3NhgU2dny6xcADhA.png", "Site homepage"),
   ("h", "Overview"),
   ("p", "Azaz Labs is a B2B product site for an AI-driven portfolio monitoring platform built for private equity deal teams and family offices. I opted for the design to lean into a dark, precise, data-forward aesthetic, consisting of sharp typography against a near-black palette with a single sharp accent colour to match the seriousness and rigour the platform promises its C-suite and deal-team audience."),
   ("tags", "Web design  ·  Product design  ·  UI/UX  ·  Motion  ·  Interaction design"),
   VIDEO("assets/video/azaz-labs/hero.mp4", "The homepage on load"),
   ("h", "Product page"),
   ("p", "The page is built around animations and hover microinteractions throughout, so the site itself performs the platform's promise of continuous, real-time intelligence rather than reading like a static brochure."),
   VIDEO("assets/video/azaz-labs/rest.mp4", "Scrolling through the rest of the site"),
   ("h", "Animations"),
   ("p", "To make Azaz's complex portfolio-monitoring software tangible rather than abstract, I built looping SVG animations that visualise the platform's real processes, like scattered portco data flowing into one unified view, so users grasp what the product actually does at a glance, before reading through a wall of feature copy."),
   RAW(AZAZ_ANIMATIONS_HTML),
   R(["l0tRx2C4I45VSWKmYsij8YCXgDs.jpg", "I045z5WynfGe04FoyT2UWo1I99Q.jpg",
      "X90bGpbybrnfE1uV1mWYx9Eifs4.jpg", "5fON0jQke2u1JARwjByyr1Ql7g.jpg",
      "yykXq0dKyq4bKFiHilfIAva22q0.jpg", "QVaZByDPnlj6rd8Kb5J9x40cs0.jpg",
      "4iJDSNd3hJON1sx5iGpmVvJJvpY.jpg", "ID15FyIgpb7K9buMgf5vUyQ6E.jpg"],
     "Website mobile UI", cols=4),
  ],
 },
 {
  "slug": "scrapage",
  "title": "Scrapage",
  "grid_label": "Brand identity  ·  Packaging  ·  UI/UX",
  "white_page": True,
  "flow": [
   HERO("SZwge61pCllw0wFgE2KoPQnt4Sc.png", "Scrapage homepage"),
   ("h", "Overview"),
   ("p", "Scrapage is a secondary business venture of the United Repair Centre, turning textile waste into playful new products. Focused on consumers rather than B2B, it promotes self-expression, creativity and sustainability."),
   ("tags", "Brand identity  ·  Packaging  ·  UI/UX  ·  Motion  ·  Campaign design"),
   ("note", "Collaboration project with the talented designers Elisha Ayres and Millie Mason."),
   R(["ReieQoTOuPTsJQOgBgI8DrSzWk.png"], "Brand colours & icons"),
   R(["7DsjVDQ4UQL9ZcJgchrhUSkPVjs.png"], "Packaging, stickers & posters"),
   R(["R3F89GpnXvoJMJSI2pg3sfNogmY.png"], "Street sticker campaign"),
   R(["assets/video/scrapage/anim-2.mp4", "assets/video/scrapage/anim-1.mp4",
      "assets/video/scrapage/anim-3.mp4"], "Square-format animations", cols=3),
   VIDEO("assets/video/scrapage/recording.mp4", "The website on load"),
  ],
 },
 {
  "slug": "islamic-patterns",
  "title": "The Computation of Islamic Geometry",
  "grid_label": "Interaction · Publishing · UI/UX",
  "hero_video": "assets/video/islamic-patterns/showreel.mp4",
  "flow": [
   HERO("BT8dmbYsiXdDHR2SIIuD0kEvqg.jpg", "Physical publication"),
   ("h", "Overview"),
   ("p", "This project responds to my dissertation question — how the computation of Islamic geometry alters its contemplative and metaphysical qualities — through a box, publication and construction manual designed to be accessible to non-Muslim audiences without requiring theological depth, centred on the argument that intentionality behind creation matters more than the tool used to make it. Alongside the physical publication, I built a digital generative tool that enacts this same argument by contrast, setting the slow, unpredictable, skill-dependent nature of hand construction against the instant, exact output of computation."),
   ("tags", "Interaction design  ·  Publishing  ·  UI/UX  ·  Print  ·  Product design  ·  Creative coding"),
   R(["PRE80yxZ79FM2JWdQpiFavMokZM.jpg"]),
   R(["CuqAbKOMYFFGGsWCMLNUI5Mfc.jpg"], "Digital tool"),
   R(["uOlkTQWLcP8H8Fx48VPWUiM3IQ.jpg"], "Publication spread"),
   R(["LtzWNtNCCnOLu1Ww94bYeIJxw.jpg", "X4Bp44hfzFAEY8MSwen8DWsnW9s.jpg"],
     "Mobile UI", mobile_cols=1),
   ("h", "Process & experimentation"),
   ("p", "For the manual, I worked through a consistent page grid that could hold both dense geometric diagrams and short instructional text without feeling cluttered, mirroring the patterns themselves in their symmetry. I then tested various formats alongside the publication, such as a zine on red paper as displayed on the right."),
   ("p", "For the digital tool, I experimented with translating those same hand-drawn construction rules (symmetry groups, star points, interlace depth) into code, then iterated on the interface until adjusting a single parameter could visibly show how computation strips away the slowness and unpredictability of hand construction."),
   R(["xIjO7mpSCc0xQ0JgYyCHVwf2POM.png"], "Layout tests", w=63, align="right"),
   R(["yAJHkhnoGwMZOH3YChEEQtqg7w.png"], "Zine experiment", w=63, align="right"),
   R(["3jIHHEf88pVlOmvuN98idP5Pho.png"], "Laser cutting", w=63, align="right"),
  ],
 },
 {
  "slug": "fasila",
  "title": "Fasila",
  "grid_label": "Type · Conceptual · Publishing",
  "white_page": True,
  "flow": [
   HERO("ahzxF8OQVrGgQg2rEeY49O8404.jpg", "Fasila written in a variety of styles"),
   ("h", "Overview"),
   ("p", "Fasila began with my interest in asemic writing and a personal connection to Arabic's calligraphic tradition, which led me to ask what a writing system built for the space between Arabic and English, rather than despite it, might look like. It's presented as a black cloth box containing a Japanese stab-bound publication documenting the system, alongside a set of loose calligraphic cards showing the script across registers, from precise geometric digital forms to large gestural ink work."),
   ("tags", "Type design  ·  Conceptual design  ·  Publishing  ·  Print  ·  Calligraphy"),
   R(["KS1J7vcQB92JLMpcQtptX6Gmy7c.jpg"], "Publication box"),
   R(["jyHgrqiMyJpMa8jIVbDGlgwP1uw.png"], "Poem written in Fasila"),
   R(["2Fm7jPfMBaWUzWTgxu9YC1HtX0Y.jpg", "sOBYgFHsedIBp1209tEPodFrErg.jpg"], mobile_cols=1),
   R(["vTBua1QqZLZx3Owze104tWM6Q.png"], "Translation guide - IPA to Fasila"),
   R(["SWthJnkHzMrsCuad0IotMBAF0.png"], "'Between worlds' written in Fasila"),
   ("h", "Process & experimentation"),
   ("p", "I started by mapping and analysing a range of existing asemic and constructed scripts, looking at how each balanced structure against illegibility. Alongside this, I built my own IPA chart cross-referencing Arabic and English phonemes, identifying where the two languages share articulation points, which became the phonetic logic underpinning Fasila's letterforms."),
   ("p", "From there I iterated the actual shapes through both analogue and digital methods, testing gestural ink strokes by hand to find forms with real calligraphic weight, then refining those into precise digital letterforms, moving back and forth between the two until the script held together as one coherent system rather than two competing styles."),
   R(["zxvPPLYoHDAP43Lv4rYFKCJjR0U.png"], "Analysing asemic scripts", w=63, align="right"),
   R(["flcvO8R7wjCkYRz4bl8gnusVwvE.png"], "Mapping Arabic & English sounds", w=63, align="right"),
   R(["oevs0QuqhymtPN6U8pu2CASX3w.png"], "Script development", w=63, align="right"),
  ],
 },
 {
  "slug": "into-the-light",
  "title": "Into the Light",
  "grid_label": "UI/UX  ·  Interaction  ·  Web design",
  "hero_video": "assets/video/into-the-light/homepage.mp4",
  "grid_video": "assets/video/into-the-light/homepage.mp4",
  "grid_still": "assets/img/into-the-light/thumb-laptop.jpg",
  "flow": [
   ("h", "Overview"),
   ("p", "Into the Light is an interactive website raising awareness of moth ecology and the impact of artificial light pollution on UK moth populations, built by combining ecological research with coded interaction rather than static information design. Throughout the site the user acts as the light source itself as moths are drawn to the cursor, disappear on contact, and visibly decline across a data-driven timeline from 1900 to 2024, making the reader complicit in the problem rather than a passive observer of it."),
   ("tags", "UI/UX  ·  Interaction design  ·  Web design  ·  Creative coding  ·  Data visualisation"),
   R(["JK0zWubc8ukot7iaPLqtwdLf04.png"], "Typography guidelines", w=50, align="center"),
   VIDEO("assets/video/into-the-light/moth.mp4", "The Moth"),
   VIDEO("assets/video/into-the-light/threat.mp4", "The Threat"),
   VIDEO("assets/video/into-the-light/takeaction.mp4", "Take Action"),
   ("h", "Process & experimentation"),
   ("p", "I began by sketching wireframes by hand to work out the site's structure, how a visitor would move between The Moth, The Threat, The Archive, and Take Action, so the narrative arc came together before any of it existed in code. From there I iterated through many different coded interactions for the cursor-as-light mechanic, testing different moth movement patterns, timing for disappearance on contact, and how aggressively they'd swarm, refining each version until the interaction felt like it was making an argument about complicity rather than just showing off a hover effect."),
   R(["S0fg6Ff6Rrrhd7POSHLv8Ovf0.png"], w=63, align="right"),
   R(["Pz0cb46evbNqjaNFITYKndcowk.png"], "Wireframes", w=63, align="right"),
  ],
 },
]

ALIGN = {"left": "flex-start", "center": "center", "right": "flex-end"}


def img_url(h):
    return f"{FRAMER}{h}?width={MAXW}"


def dl(slug, h, idx):
    ext = h.split(".")[-1].split("?")[0]
    outdir = IMG_ROOT / slug
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{idx:02d}.{ext}"
    if out.exists() and out.stat().st_size > 1000:
        return out
    r = subprocess.run(["curl", "-sL", "--fail", "-o", str(out), img_url(h)])
    if r.returncode != 0 or not out.exists() or out.stat().st_size < 500:
        print("  !! failed", img_url(h)); return None
    return out


def rel_from_work(p):
    return "../" + str(p.relative_to(ROOT)) + f"?v={VERSION}"


def esc(s):
    return html.escape(s, quote=True)


def render_project(proj):
    slug, title = proj["slug"], proj["title"]
    local, counter = {}, [0]

    def grab(h):
        if h in local:
            return local[h]
        counter[0] += 1
        local[h] = dl(slug, h, counter[0])
        return local[h]

    parts, hero_src, hero_dims, hero_cap, hero_w, hero_align = [], "", "", "", 100, "flex-start"
    intro_text, intro_tags = "", ""
    for item in proj["flow"]:
        kind = item[0]
        if kind == "hero":
            _, h, cap, lay = item
            p = grab(h)
            hero_src = rel_from_work(p) if p else ""
            hero_dims = dim_attrs(p)
            hero_cap = f'<figcaption>{esc(cap)}</figcaption>' if cap else ''
            hero_w = lay["w"]
            hero_align = ALIGN[lay["align"]]
        elif kind == "h" and not parts and not intro_text:
            continue   # the leading "Overview" heading — folded into the intro band below
        elif kind == "p" and not parts and not intro_text:
            intro_text = item[1]
        elif kind == "tags" and not parts and not intro_tags:
            intro_tags = item[1]
        elif kind == "h":
            parts.append(f'<h2 class="cs-h">{esc(item[1])}</h2>')
        elif kind == "p":
            parts.append(f'<p class="cs-p">{esc(item[1])}</p>')
        elif kind == "tags":
            parts.append(f'<p class="cs-tags">{esc(item[1])}</p>')
        elif kind == "note":
            parts.append(f'<p class="cs-note">{esc(item[1])}</p>')
        elif kind == "video":
            _, src, cap, lay = item
            capm = f'<figcaption>{esc(cap)}</figcaption>' if cap else ''
            parts.append(
                f'<div class="media-row" data-align="{lay["align"]}">'
                f'<div class="media-inner cols-1" style="--w:{lay["w"]}%">'
                f'<figure class="shot"><video autoplay muted loop playsinline '
                f'src="../{src}?v={VERSION}"></video>{capm}</figure></div></div>')
        elif kind == "raw":
            _, html_block, _cap, lay = item
            parts.append(
                f'<div class="media-row" data-align="{lay["align"]}">'
                f'<div class="media-inner cols-1" style="--w:{lay["w"]}%">'
                f'{html_block}</div></div>')
        elif kind == "row":
            _, entries, shared, lay = item
            n = len(entries)
            ncols = lay["cols"] or n
            figs = []
            for e in entries:
                h, cap = e if isinstance(e, tuple) else (e, None)
                capm = f'<figcaption>{esc(cap)}</figcaption>' if cap else ''
                if h.split("?")[0].rsplit(".", 1)[-1].lower() in ("mp4", "mov", "webm"):
                    # a local video file used as-is, not Framer-hosted
                    figs.append(
                        f'<figure class="shot"><video autoplay muted loop playsinline '
                        f'src="../{h}?v={VERSION}"></video>{capm}</figure>')
                    continue
                p = grab(h)
                if not p:
                    continue
                figs.append(
                    f'<figure class="shot"><img loading="lazy" decoding="async"{dim_attrs(p)} '
                    f'src="{rel_from_work(p)}" alt="{esc(cap or title)}">{capm}</figure>')
            if shared:
                figs.append(f'<p class="row-cap">{esc(shared)}</p>')
            colcls = f' cols-{ncols}' if n > 1 else ' cols-1'
            if lay.get("mobile_cols"):
                colcls += f' mcols-{lay["mobile_cols"]}'
            parts.append(
                f'<div class="media-row" data-align="{lay["align"]}">'
                f'<div class="media-inner{colcls}" style="--w:{lay["w"]}%">'
                f'{"".join(figs)}</div></div>')

    body_class = "case-study" + (" cs-white" if proj.get("white_page") else "")

    if proj.get("hero_video"):
        hero_tag = (f'<video autoplay muted loop playsinline '
                    f'src="../{proj["hero_video"]}?v={VERSION}"></video>')
    else:
        hero_tag = f'<img src="{hero_src}" alt="{esc(title)}" decoding="async"{hero_dims}>'

    return PAGE_TMPL.format(
        title=esc(title), slug=slug, hero_tag=hero_tag, hero_cap=hero_cap,
        hero_w=hero_w, hero_align=hero_align, label=esc(proj["grid_label"]),
        intro_text=esc(intro_text), intro_tags=esc(intro_tags), body_class=body_class,
        body="\n".join(parts), v=VERSION)


PAGE_TMPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>if("scrollRestoration" in history){{history.scrollRestoration="manual"}}window.scrollTo(0,0)</script>
<title>{title} — Tuqa Lynch</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css?v={v}">
</head>
<body class="{body_class}">
<div class="topbar show">
  <a class="mark topbar-mark" href="../index.html" data-words="Tuqa,Lynch" data-collapse-delay="0" aria-label="Tuqa Lynch"></a>
  <nav class="topbar-nav">
    <a href="../index.html#work">Work</a>
    <a href="../index.html#about">About me</a>
  </nav>
</div>

<main class="cs-wrap">
  <a class="cs-back" href="../index.html#work">&larr; Selected work</a>
  <div class="cs-title-block">
    <h1 class="cs-title">{title}</h1>
    <p class="cs-label">{label}</p>
  </div>

  <figure class="cs-hero-full">
    {hero_tag}
    {hero_cap}
  </figure>

  <section class="cs-intro">
    <p class="cs-intro-tag">{title}<br><span>{label}</span></p>
    <p class="cs-intro-text">{intro_text}</p>
  </section>

  <table class="cs-meta">
    <tr><th>{title}</th><td>Case study</td></tr>
    <tr><td>Role</td><td>{label}</td></tr>
    <tr><td>Services</td><td>{intro_tags}</td></tr>
  </table>

  <div class="cs-body">
    {body}
  </div>
</main>

<footer class="site-foot">
  <div class="foot-inner">
    <a class="foot-big" href="mailto:tuqalynchgraphics@gmail.com">tuqalynchgraphics@gmail.com</a>
    <a class="foot-big" href="tel:+447476608500">+44 7476 608500</a>
    <a class="foot-big" href="https://www.linkedin.com/in/tuqalynch/" target="_blank" rel="noopener">LinkedIn</a>
  </div>
  <p class="foot-copy">Tuqa Lynch</p>
</footer>

<script src="../assets/js/main.js?v={v}"></script>
</body>
</html>
"""


# three thumbnails flicked through on card hover (indices into assets/img/<slug>/)
GRID_FRAMES = {
    "canada-water-library": ("01", "06", "19", "08"),
    "holistic-transformation-management": ("01", "03", "13"),
    "andromeda": ("05", "mac2", "04", "08"),
    "azaz-labs": ("01", "02", "06"),
    "scrapage": ("03", "01", "04"),
    "islamic-patterns": ("01", "02", "04"),
    "fasila": ("01", "02", "04"),
    "into-the-light": ("01", "02", "03"),
}


SUMMARIES = {
    "canada-water-library": "A brand identity system for a London library, drawn from the angles of the building itself",
    "holistic-transformation-management": "Brand and web identity for a business transformation consultancy",
    "andromeda": "A visual identity rebuilt around a bold violet, a halftone dust texture and a sharp four-point mark",
    "azaz-labs": "A dark, data-forward product site for an AI portfolio-monitoring platform",
    "scrapage": "A consumer brand turning textile waste into playful new products",
    "islamic-patterns": "A publication and generative tool exploring Islamic geometry by hand and by code",
    "fasila": "A constructed writing system for the space between Arabic and English",
    "into-the-light": "An interactive site on moth ecology and light pollution in the UK",
}


def render_grid():
    total = len(PROJECTS)

    def panel(n, p):
        d = IMG_ROOT / p["slug"]
        def fpath(idx):
            g = sorted(d.glob(idx + ".*"))
            return (f"assets/img/{p['slug']}/{g[0].name}?v={VERSION}", g[0]) if g else (None, None)
        num = f"{total - n:02d}"

        if p.get("grid_video"):
            # A still (the "laptop mockup") at rest; a short muted/looping
            # clip crossfades in on hover instead of the old multi-frame
            # image flick — see .proj-video in style.css / setActive() in
            # main.js for the play/pause + opacity toggle.
            still = p["grid_still"]
            loop_attr = "" if p.get("grid_video_loop") is False else " loop"
            media = (
                f'<img loading="lazy" decoding="async"{dim_attrs(ROOT / still)} '
                f'src="{still}?v={VERSION}" alt="{esc(p["title"])}">'
                f'<video class="proj-video" muted{loop_attr} playsinline preload="none" '
                f'src="{p["grid_video"]}?v={VERSION}"></video>'
            )
            frames_attr = ""
        else:
            idxs = GRID_FRAMES.get(p["slug"], ("01", "03", "05"))
            found = [fpath(i) for i in idxs]
            frames = [fp for fp, _ in found if fp]
            src = frames[0] if frames else ""
            srcpath = next((lp for fp, lp in found if fp), None)
            # Two stacked layers so the hover flick-through can crossfade
            # between frames (a straight src-swap on one <img> is an
            # instant hard cut, which is what reads as "glitchy") — see
            # .proj-frame in style.css and the lane/setActive logic in
            # main.js for the alternating fade.
            media = (
                f'<img class="proj-frame is-shown" loading="lazy" decoding="async"'
                f'{dim_attrs(srcpath)} src="{src}" alt="{esc(p["title"])}">'
                f'<img class="proj-frame" alt="{esc(p["title"])}">'
            )
            frames_attr = f' data-frames="{",".join(frames)}"'

        return (
          f'''    <a class="proj reveal" href="work/{p['slug']}.html"{frames_attr}>
      <span class="proj-media">{media}</span>
      <span class="proj-idx">{num}</span>
      <span class="proj-cap">
        <span class="proj-title">{esc(p['title'])}</span>
        <span class="proj-summary">{esc(SUMMARIES.get(p['slug'], ''))}</span>
        <span class="proj-role">{esc(p['grid_label'])}</span>
      </span>
    </a>''')

    rows = []
    for i in range(0, total, 2):
        pair = "\n".join(panel(i + j, p) for j, p in enumerate(PROJECTS[i:i + 2]))
        rows.append(f'  <div class="proj-row">\n{pair}\n  </div>')
    return "\n".join(rows)


if __name__ == "__main__":
    for p in PROJECTS:
        print("::", p["slug"])
        (WORK_DIR / f"{p['slug']}.html").write_text(render_project(p), encoding="utf-8")
    (ROOT / "build" / "work_grid.html").write_text(render_grid(), encoding="utf-8")
    print("done.")
