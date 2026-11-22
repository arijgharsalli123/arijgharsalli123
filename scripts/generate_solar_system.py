#!/usr/bin/env python3
"""Generate a self-contained GitHub Solar System SVG from public GitHub data.

Usage:
  GITHUB_TOKEN=... python scripts/generate_solar_system.py
"""
from __future__ import annotations

import base64
import html
import json
import math
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "arijgharsalli123")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path("assets/solar-system.svg")
WIDTH, HEIGHT = 1200, 780
BG = "#070B17"
FG = "#E8EEF9"
MUTED = "#93A4C2"
GOLD = "#F5C96A"
ACCENTS = ["#69B7FF", "#B58CFF", "#FF8C9B", "#58D6B0", "#F49B55", "#79D5D8", "#D6A6F5"]
LANG_COLORS = {
    "Java": "#F89820", "JavaScript": "#F1E05A", "TypeScript": "#3178C6",
    "Python": "#3572A5", "HTML": "#E34C26", "CSS": "#663399",
    "Kotlin": "#A97BFF", "C": "#555555", "C++": "#F34B7D",
    "C#": "#178600", "PHP": "#4F5D95", "Go": "#00ADD8",
    "Rust": "#DEA584", "Dart": "#00B4AB", "Swift": "#F05138",
    "Ruby": "#701516", "Shell": "#89E051", "Jupyter Notebook": "#DA5B0B",
}

def request_json(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-solar-system-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def get_bytes(url: str) -> bytes | None:
    try:
        headers = {"User-Agent": f"{USERNAME}-solar-system-readme"}
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read()
    except Exception as exc:
        print(f"Avatar download skipped: {exc}")
        return None

def esc(value) -> str:
    return html.escape(str(value), quote=True)

def shorten(value: str, limit: int) -> str:
    value = " ".join((value or "").split())
    return value if len(value) <= limit else value[:limit - 1] + "…"

def text(x, y, value, size=16, fill=FG, weight=400, anchor="start", family="monospace"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" font-family="{family}">{esc(value)}</text>')

def circle(x, y, r, fill, opacity=1, stroke="none", sw=1):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>')

def build():
    user = request_json(f"https://api.github.com/users/{USERNAME}")
    repos = request_json(
        f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated&type=owner"
    )
    repos = [r for r in repos if not r.get("fork") and not r.get("archived")]
    repos.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)

    language_totals: dict[str, int] = {}
    repo_details = []
    for repo in repos[:60]:
        try:
            langs = request_json(repo["languages_url"])
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            print(f"Skipping language data for {repo['name']}: {exc}")
            langs = {}
        for language, count in langs.items():
            language_totals[language] = language_totals.get(language, 0) + count
        repo_details.append({
            "name": repo["name"],
            "description": repo.get("description") or "A project in my developer universe",
            "html_url": repo["html_url"],
            "language": repo.get("language") or "Other",
            "pushed_at": repo.get("pushed_at") or "",
            "stars": repo.get("stargazers_count", 0),
        })

    total_bytes = sum(language_totals.values())
    languages = sorted(language_totals.items(), key=lambda item: item[1], reverse=True)[:7]
    recent_repos = repo_details[:6]

    avatar_data = get_bytes(user.get("avatar_url", ""))
    avatar_href = ""
    if avatar_data:
        # GitHub profile SVGs can display an embedded raster avatar without a remote dependency.
        avatar_href = "data:image/png;base64," + base64.b64encode(avatar_data).decode("ascii")

    cx, cy = 600, 350
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<defs>',
        '<radialGradient id="space" cx="50%" cy="45%" r="75%"><stop offset="0%" stop-color="#17233D"/><stop offset="55%" stop-color="#0B1224"/><stop offset="100%" stop-color="#050812"/></radialGradient>',
        '<radialGradient id="sun"><stop offset="0%" stop-color="#FFF5C8"/><stop offset="55%" stop-color="#F6C967"/><stop offset="100%" stop-color="#D88736"/></radialGradient>',
        '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="12" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>',
        '<linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#17243B" stop-opacity=".9"/><stop offset="1" stop-color="#0A1020" stop-opacity=".95"/></linearGradient>',
        '</defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="28" fill="url(#space)"/>',
        '<rect x="1" y="1" width="1198" height="778" rx="27" fill="none" stroke="#263B60" stroke-width="2"/>',
    ]

    # Deterministic star field.
    for i in range(105):
        x = (i * 197 + 43) % WIDTH
        y = (i * 113 + 29) % HEIGHT
        r = 0.7 + (i % 4) * 0.35
        op = 0.22 + (i % 5) * 0.12
        parts.append(circle(x, y, r, "#DCE8FF", op))

    parts += [
        text(52, 58, f"SOLAR SYSTEM  /  @{USERNAME.upper()}", 17, GOLD, 700),
        text(52, 88, "A living map of my open-source universe", 13, MUTED),
        text(1145, 58, f"{len(repos)} PUBLIC PROJECTS", 12, MUTED, 600, "end"),
        text(1145, 82, f"{len(languages)} LANGUAGE ORBITS", 12, MUTED, 600, "end"),
    ]

    # Orbit rings.
    for idx, (rx, ry) in enumerate([(145, 82), (235, 132), (335, 190), (445, 250)]):
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#8296BE" stroke-opacity="{0.20 - idx*0.025}" stroke-width="1.2" stroke-dasharray="3 9"/>')

    # Sun glow and central avatar.
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="86" fill="#F3B94F" opacity=".12" filter="url(#soft)"/>')
    parts.append(circle(cx, cy, 51, "url(#sun)", 1, GOLD, 3))
    parts.append(circle(cx, cy, 43, "#111827", 1, "#FFF0BD", 2))
    if avatar_href:
        parts.append(f'<clipPath id="avatarClip"><circle cx="{cx}" cy="{cy}" r="39"/></clipPath>')
        parts.append(f'<image x="{cx-39}" y="{cy-39}" width="78" height="78" xlink:href="{avatar_href}" preserveAspectRatio="xMidYMid slice" clip-path="url(#avatarClip)"/>')
    else:
        parts.append(text(cx, cy+8, esc(USERNAME[:2].upper()), 27, "#111827", 800, "middle", "sans-serif"))
    parts.append(text(cx, cy+72, shorten(user.get("name") or USERNAME, 24), 15, FG, 700, "middle", "sans-serif"))
    parts.append(text(cx, cy+91, "THE SUN · DEVELOPER", 9, GOLD, 700, "middle"))

    # Language planets on elliptical orbits.
    planet_positions = {}
    if languages:
        for i, (language, amount) in enumerate(languages):
            orbit_index = i % 4
            rx, ry = [(145, 82), (235, 132), (335, 190), (445, 250)][orbit_index]
            angle = (-145 + i * 48) * math.pi / 180
            px = cx + rx * math.cos(angle)
            py = cy + ry * math.sin(angle)
            radius = 10 + 15 * math.sqrt(amount / max(language_totals.values()))
            color = LANG_COLORS.get(language, ACCENTS[i % len(ACCENTS)])
            planet_positions[language] = (px, py)
            parts.append(circle(px, py, radius+8, color, .10))
            parts.append(circle(px, py, radius, color, 1, "#FFFFFF", 1))
            if language in ("Java", "JavaScript", "TypeScript", "Python"):
                parts.append(circle(px-radius*.25, py-radius*.28, radius*.28, "#FFFFFF", .32))
            percent = amount / total_bytes * 100 if total_bytes else 0
            parts.append(text(px, py+radius+17, language, 12, FG, 700, "middle"))
            parts.append(text(px, py+radius+31, f"{percent:.1f}%", 10, MUTED, 500, "middle"))
    else:
        parts.append(text(cx, cy+145, "Language data will appear after the first workflow run", 13, MUTED, 400, "middle"))

    # Project moons: six recent repositories with small orbital markers and labels.
    # These are linked visually to each repository's primary language planet where possible.
    moon_y = 635
    parts.append(f'<rect x="35" y="{moon_y-38}" width="1130" height="108" rx="18" fill="url(#panel)" stroke="#293B5C"/>')
    parts.append(text(58, moon_y-10, "MOONS  /  RECENTLY UPDATED REPOSITORIES", 12, GOLD, 700))
    if recent_repos:
        col_w = 1100 / min(6, len(recent_repos))
        for i, repo in enumerate(recent_repos):
            x = 60 + i * col_w
            color = LANG_COLORS.get(repo["language"], ACCENTS[i % len(ACCENTS)])
            parts.append(circle(x+8, moon_y+19, 5, color, 1, "#FFFFFF", .8))
            parts.append(text(x+21, moon_y+23, shorten(repo["name"], 17), 11, FG, 700))
            parts.append(text(x+8, moon_y+44, shorten(repo["language"], 15), 9, MUTED))
            parts.append(text(x+8, moon_y+59, f"★ {repo['stars']}", 9, GOLD))
    else:
        parts.append(text(58, moon_y+30, "No public repositories found yet.", 12, MUTED))

    parts += [
        text(55, 758, "PLANETS = LANGUAGES   ·   MOONS = REPOSITORIES   ·   DATA = GITHUB API", 10, MUTED),
        text(1145, 758, "AUTO-GENERATED", 10, GOLD, 700, "end"),
        '</svg>',
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Generated {OUT} ({OUT.stat().st_size:,} bytes)")
    print("Languages:", ", ".join(f"{name} {value}" for name, value in languages))
    print("Repositories:", len(repos))

if __name__ == "__main__":
    build()
