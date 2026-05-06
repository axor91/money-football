"""
Сбор истории рыночных стоимостей топ-клубов с Transfermarkt
через Wayback Machine.

Берём по 2 снапшота в год (~1 января и ~1 июля) с 2019 по 2026.
Сырой HTML кешируется в data/html/, итог — data/clubs.csv.

Запуск:
    python collect.py
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TARGET_URL = "transfermarkt.com/spieler-statistik/wertvollstemannschaften/marktwertetop"
CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK_RAW = "https://web.archive.org/web/{ts}id_/{url}"

DATA_DIR = Path("data")
HTML_DIR = DATA_DIR / "html"
OUTPUT_CSV = DATA_DIR / "clubs.csv"

TARGET_DATES = [
    datetime(year, month, 1)
    for year in range(2019, 2027)
    for month in (1, 4, 7, 10)
]
MAX_OFFSET_DAYS = 60
TOP_N = 30
SLEEP_BETWEEN = 2.0


@dataclass
class Snapshot:
    target: datetime
    actual: datetime
    timestamp: str
    original: str


def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def fetch_cdx_index(session: requests.Session) -> list[tuple[str, str]]:
    params = [
        ("url", TARGET_URL),
        ("from", "20190101"),
        ("to", "20261231"),
        ("output", "json"),
        ("filter", "statuscode:200"),
        ("filter", "mimetype:text/html"),
        ("collapse", "timestamp:6"),
    ]
    r = session.get(CDX_API, params=params, timeout=60)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        return []
    header, *data = rows
    ts_i = header.index("timestamp")
    orig_i = header.index("original")
    return [(row[ts_i], row[orig_i]) for row in data]


def pick_snapshots(index: list[tuple[str, str]],
                   targets: list[datetime]) -> list[Snapshot]:
    parsed = [
        (datetime.strptime(ts, "%Y%m%d%H%M%S"), ts, orig)
        for ts, orig in index
    ]
    chosen: list[Snapshot] = []
    used: set[str] = set()
    for target in targets:
        if not parsed:
            continue
        candidate = min(parsed, key=lambda x: abs(x[0] - target))
        actual, ts, orig = candidate
        if ts in used:
            continue
        if abs((actual - target).days) > MAX_OFFSET_DAYS:
            continue
        used.add(ts)
        chosen.append(Snapshot(target, actual, ts, orig))
    return chosen


def fetch_html(session: requests.Session, snap: Snapshot) -> str:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    cache = HTML_DIR / f"{snap.timestamp}.html"
    if cache.exists() and cache.stat().st_size > 5_000:
        return cache.read_text(encoding="utf-8", errors="replace")
    url = WAYBACK_RAW.format(ts=snap.timestamp, url=snap.original)
    r = session.get(url, timeout=60)
    r.raise_for_status()
    cache.write_text(r.text, encoding="utf-8")
    return r.text


_VALUE_RE = re.compile(
    r"([\d][\d.,]*)\s*(bill|bil|bn|mrd|mill|mio|m|k|th|млрд|млн|тыс)?",
    re.IGNORECASE,
)


def parse_value_to_eur_m(text: str | None) -> float | None:
    """'€1.23bn' / '500.00m' / '€1,23 Mrd.' / '1,16 Bill. €' / '976,50 Mill. €' -> млн евро.

    На TM в разные годы встречаются разные форматы: en (bn/m), de (Mrd./Mio.),
    и старая локаль 2019 (Bill./Mill.) — биллион тут = англ. billion = млрд.
    """
    if not text:
        return None
    cleaned = text.replace("\xa0", " ").strip()
    match = _VALUE_RE.search(cleaned)
    if not match:
        return None
    num_str, suffix = match.group(1), (match.group(2) or "").lower()

    if "." in num_str and "," in num_str:
        if num_str.rfind(".") > num_str.rfind(","):
            num_str = num_str.replace(",", "")
        else:
            num_str = num_str.replace(".", "").replace(",", ".")
    elif "," in num_str:
        parts = num_str.split(",")
        if len(parts[-1]) == 2:
            num_str = num_str.replace(",", ".")
        else:
            num_str = num_str.replace(",", "")

    try:
        num = float(num_str)
    except ValueError:
        return None

    if suffix in ("bn", "mrd", "bill", "bil", "млрд"):
        return round(num * 1_000, 2)
    if suffix in ("k", "th", "тыс"):
        return round(num / 1_000, 4)
    return round(num, 2)


def parse_clubs(html: str, top_n: int = TOP_N) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.items")
    if not table:
        return []

    out: list[dict] = []
    for tr in table.select("tbody > tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 4:
            continue
        rank_text = tds[0].get_text(strip=True)
        if not rank_text.isdigit():
            continue
        rank = int(rank_text)
        if rank > top_n:
            break

        club_link = (
            tr.select_one("td.hauptlink a")
            or tr.select_one("a.vereinprofil_tooltip")
            or tr.select_one("td:nth-of-type(2) a")
        )
        club = club_link.get_text(strip=True) if club_link else None

        flag = tr.select_one("img.flaggenrahmen")
        country = flag.get("alt") if flag else None

        rechts_cells = tr.select("td.rechts")
        value_text = rechts_cells[-1].get_text(strip=True) if rechts_cells else None
        if not value_text:
            value_text = tds[-1].get_text(strip=True)

        out.append({
            "rank": rank,
            "club": club,
            "country": country,
            "value_text": value_text,
            "value_eur_m": parse_value_to_eur_m(value_text),
        })
    return out


def collect() -> pd.DataFrame:
    DATA_DIR.mkdir(exist_ok=True)
    session = make_session()

    print("→ CDX index...")
    index = fetch_cdx_index(session)
    print(f"  {len(index)} snapshots returned")

    snapshots = pick_snapshots(index, TARGET_DATES)
    print(f"  {len(snapshots)} picked (one per target date, ≤{MAX_OFFSET_DAYS}d offset)")
    if not snapshots:
        print("Нет подходящих снапшотов. Проверь, что Wayback ответил.")
        sys.exit(1)

    rows: list[dict] = []
    for snap in snapshots:
        try:
            html = fetch_html(session, snap)
            clubs = parse_clubs(html)
            for c in clubs:
                c.update({
                    "snapshot_ts": snap.timestamp,
                    "snapshot_date": snap.actual.date().isoformat(),
                    "target_date": snap.target.date().isoformat(),
                })
            rows.extend(clubs)
            status = "OK" if clubs else "EMPTY (проверь html)"
            print(f"  {snap.timestamp} ({snap.actual.date()}): {len(clubs):>2} clubs — {status}")
        except Exception as e:
            print(f"  {snap.timestamp}: FAILED — {e}")
        time.sleep(SLEEP_BETWEEN)

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✓ {len(df)} rows → {OUTPUT_CSV}")
    return df


if __name__ == "__main__":
    collect()
