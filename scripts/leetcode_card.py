import json
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = "BlopFlop"
OUTPUT = Path(__file__).resolve().parent.parent / "assets" / "leetcode.svg"

QUERY = """
query($u: String!) {
  matchedUser(username: $u) {
    submitStatsGlobal { acSubmissionNum { difficulty count } }
    languageProblemCount { languageName problemsSolved }
    badges { displayName }
  }
}
"""

SQL_LANGS = {"MySQL", "PostgreSQL", "MS SQL Server", "Oracle", "Pandas"}
PYTHON_LANGS = {"Python", "Python3"}

W, H = 1000, 220
PINK, PURPLE, CYAN, GREEN, YELLOW = "#ff2bd6", "#b14cff", "#00e5ff", "#39ff14", "#ffe600"


def fetch(username: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"u": username}}).encode()
    request = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (profile-card)",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)["data"]["matchedUser"]
    if not data:
        raise SystemExit(f"LeetCode user {username!r} not found")
    return data


def collect(data: dict) -> dict:
    solved = {s["difficulty"]: s["count"] for s in data["submitStatsGlobal"]["acSubmissionNum"]}
    langs = {lang["languageName"]: lang["problemsSolved"] for lang in data["languageProblemCount"]}
    return {
        "total": solved.get("All", 0),
        "medium": solved.get("Medium", 0),
        "python": sum(v for k, v in langs.items() if k in PYTHON_LANGS),
        "sql": sum(v for k, v in langs.items() if k in SQL_LANGS),
        "badges": [b["displayName"] for b in data["badges"]][:3],
    }


def render(stats: dict) -> str:
    tiles = [
        (stats["medium"], "задач Medium", YELLOW),
        (stats["python"], "на Python", CYAN),
        (stats["sql"], "SQL и Pandas", GREEN),
    ]
    tile_svg = []
    for i, (value, label, color) in enumerate(tiles):
        x = 290 + i * 150
        tile_svg.append(
            f'<g class="tile" style="animation-delay:{0.15 * i:.2f}s">'
            f'<text class="num" x="{x}" y="118" text-anchor="middle" style="fill:{color}">{value}</text>'
            f'<text class="lbl" x="{x}" y="146" text-anchor="middle">{escape(label)}</text>'
            f'<rect class="bar" x="{x - 40}" y="160" width="80" height="3" rx="1.5" fill="{color}" '
            f'style="animation-delay:{0.3 + 0.15 * i:.2f}s"/>'
            "</g>"
        )

    badge_svg = []
    for i, name in enumerate(stats["badges"]):
        y = 78 + i * 42
        color = [PINK, PURPLE, CYAN][i % 3]
        badge_svg.append(
            f'<g class="badge" style="animation-delay:{0.5 + 0.2 * i:.2f}s">'
            f'<rect x="730" y="{y - 20}" width="230" height="30" rx="15" fill="none" stroke="{color}" stroke-width="1.6"/>'
            f'<text class="bdg" x="845" y="{y}" text-anchor="middle">{escape(name)}</text>'
            "</g>"
        )

    css = """
text{font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif}
.head{font-size:13px;font-weight:700;letter-spacing:3px;fill:#c9c9ff}
.big{font-size:46px;font-weight:800;fill:#fff}
.sub{font-size:13px;fill:#c9c9ff;letter-spacing:1px}
.num{font-size:40px;font-weight:800}
.lbl{font-size:14px;fill:#c9c9ff}
.bdg{font-size:13px;font-weight:600;fill:#fff}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.ring{transform-origin:130px 115px;animation:spin 6s linear infinite}
.tile,.badge{opacity:0;animation:rise .7s ease-out forwards}
.bar{transform-box:fill-box;transform-origin:center;transform:scaleX(0);animation:grow .8s ease-out forwards}
"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="LeetCode {USERNAME}: решено {stats["total"]} задач, из них {stats["medium"]} Medium">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a0a1f"/><stop offset="1" stop-color="#1a0b2e"/></linearGradient>
  <linearGradient id="ringgrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PINK}"/><stop offset=".5" stop-color="{PURPLE}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="3" result="b1"/><feGaussianBlur stdDeviation="8" result="b2"/>
    <feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>{css}</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <text class="head" x="40" y="36">LEETCODE · {escape(USERNAME.upper())}</text>
  <circle cx="130" cy="115" r="66" fill="none" stroke="#2a2346" stroke-width="10"/>
  <g filter="url(#glow)">
    <circle class="ring" cx="130" cy="115" r="66" fill="none" stroke="url(#ringgrad)" stroke-width="10" stroke-linecap="round" stroke-dasharray="300 115"/>
  </g>
  <text class="big" x="130" y="122" text-anchor="middle" style="stroke:{PINK};stroke-width:.8">{stats["total"]}</text>
  <text class="sub" x="130" y="145" text-anchor="middle">задач решено</text>
  <g filter="url(#glow)">{"".join(tile_svg)}</g>
  <line x1="700" y1="50" x2="700" y2="180" stroke="#2a2346" stroke-width="1.5"/>
  <g filter="url(#glow)">{"".join(badge_svg)}</g>
</g>
</svg>
"""


def main() -> None:
    stats = collect(fetch(USERNAME))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(stats), encoding="utf-8")
    print(f"{OUTPUT}: {stats}")


if __name__ == "__main__":
    sys.exit(main())
