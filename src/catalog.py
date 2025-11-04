import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

CATALOG_CARD = ".selling-card__text"
TITLE = ".selling-card__title"
AUTHORS = ".selling-card__authors"
FORMATS = ".selling-card__formats"
PRICEBOX = ".selling-card__basket"
LINK_IN_TITLE = ".selling-card__title a"
NBSP = u"\xa0"

def _text(el): return el.get_text(strip=True) if el else ""

def _parse_price_block(txt: str):
    if not txt: return "", "", "", "0"
    t = txt.replace(NBSP, " ")
    nums = re.findall(r"\d+[.,]?\d*", t)
    now = nums[-1].replace(",", ".") if nums else ""
    before = nums[0].replace(",", ".") if len(nums) >= 2 else ""
    disc = ""
    if before and now:
        try:
            b, n = float(before), float(now)
            if b > 0 and n <= b: disc = f"{round((b-n)/b*100)}%"
        except: pass
    is_from = "1" if "od" in t.lower() else "0"
    return txt, now, before, is_from

def parse_catalog_page(soup: BeautifulSoup) -> list[dict]:
    out = []
    for card in soup.select(CATALOG_CARD):
        title_el, author_el = card.select_one(TITLE), card.select_one(AUTHORS)
        format_el, price_el = card.select_one(FORMATS), card.select_one(PRICEBOX)
        link_el = card.select_one(LINK_IN_TITLE) or card.find("a", href=True)

        nazev_knihy = _text(title_el)
        author = _text(author_el)
        format_k = _text(format_el)
        cena_text, cena_num, cena_before, from_price = _parse_price_block(_text(price_el))
        raw_link = (link_el["href"].strip() if link_el and link_el.has_attr("href") else "")
        detail_url = urljoin("https://www.palmknihy.cz", raw_link) if raw_link else ""
        out.append({
            "nazev_knihy": nazev_knihy,
            "author": author,
            "format_k": format_k,
            "cena_text": cena_text,
            "cena_num": cena_num,
            "cena_before": cena_before,
            "discount": "",          # заповнимо потім, якщо треба
            "from_price": from_price,
            "detail_url": detail_url,
        })
    # підрахунок знижки якщо є стара+нова
    for r in out:
        if r["cena_before"] and r["cena_num"]:
            try:
                b, n = float(r["cena_before"]), float(r["cena_num"])
                if b > 0 and n <= b: r["discount"] = f"{round((b-n)/b*100)}%"
            except: pass
    return out
