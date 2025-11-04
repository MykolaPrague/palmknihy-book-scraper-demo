import argparse, sys, os
from typing import List, Dict
from src.http import make_session, fetch_soup
from src.catalog import parse_catalog_page
from src.detail import parse_detail_page
from src.io_utils import write_csv

BASE_URL = "https://www.palmknihy.cz/tistene-knihy"
SORT = "PUBLISH_DATE_DESC"

def run(max_pages: int, max_items: int, delay: float, out_file: str, fetch_detail: bool):
    session = make_session()
    total, pages, page = 0, 0, 1
    seen_urls = set()

    # уникаємо дублів при дозапуску
    if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
        pass

    print(f"→ writing to: {out_file}")
    while True:
        if max_pages and pages >= max_pages: break
        if max_items and total >= max_items: break

        url = f"{BASE_URL}?sort={SORT}&page={page}"
        print(f"[{pages+1}] catalog: {url}")
        try:
            soup = fetch_soup(session, url, delay)
        except Exception as e:
            print(f"! catalog error: {e} — skipping"); page += 1; continue

        rows = parse_catalog_page(soup)
        if not rows: print("end of catalog."); break

        out_rows: List[Dict] = []
        for r in rows:
            if max_items and total >= max_items: break
            detail_url = r.get("detail_url","")
            if fetch_detail and detail_url:
                try:
                    dsoup = fetch_soup(session, detail_url, delay)
                    details = parse_detail_page(dsoup)
                    r.update(details)
                except Exception as e:
                    print(f"! detail error: {e} [{detail_url}]")

            out_rows.append(r); total += 1

        if out_rows: write_csv(out_rows, out_file)
        pages += 1; page += 1

    print(f"✓ done. saved {total} rows → {out_file}")

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Palmknihy.cz scraper (catalog + detail)")
    p.add_argument("--max-pages", type=int, default=3)
    p.add_argument("--max-items", type=int, default=50)
    p.add_argument("--delay", type=float, default=1.2)
    p.add_argument("--out", type=str, default="knihy.csv")
    p.add_argument("--no-detail", action="store_true")
    return p.parse_args(argv)

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    run(max(0,args.max_pages), max(0,args.max_items),
        max(0.0,args.delay), args.out, fetch_detail=not args.no_detail)
