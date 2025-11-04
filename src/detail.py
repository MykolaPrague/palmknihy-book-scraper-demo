import re, json
from bs4 import BeautifulSoup

def _t(el): return el.get_text(strip=True) if el else ""
def _sel(soup, css): return soup.select_one(css)

def _param_li(soup, name):
    el = _sel(soup, f'[data-cy="detail-{name}"] li')
    return _t(el) if el else ""

def _parse_price_num(txt: str):
    if not txt: return ""
    m = re.search(r"\d+(?:[.,]\d+)?", txt.replace("\xa0"," ").replace(" ",""))
    return m.group(0).replace(",", ".") if m else ""

def _parse_jsonld(soup: BeautifulSoup) -> dict:
    data = {}
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            block = json.loads(tag.string or "")
        except Exception:
            continue
        cand = block if isinstance(block, list) else [block]
        for obj in cand:
            if not isinstance(obj, dict): continue
            typ = obj.get("@type") or obj.get("@graph", [{}])[0].get("@type")
            types = [typ] if isinstance(typ, str) else (typ or [])
            types = [t.lower() for t in types if isinstance(t, str)]
            if any(t in ("book","product") for t in types):
                if "name" in obj: data.setdefault("nazev_detail", obj["name"])
                if "isbn" in obj: data.setdefault("isbn", obj["isbn"])
                pub = obj.get("publisher") or obj.get("brand")
                if isinstance(pub, dict) and "name" in pub:
                    data.setdefault("nakladatel", pub["name"])
                elif isinstance(pub, str):
                    data.setdefault("nakladatel", pub)
                if "inLanguage" in obj: data.setdefault("jazyk", obj["inLanguage"])
                if "numberOfPages" in obj: data.setdefault("pocet_stran", str(obj["numberOfPages"]))
                if "description" in obj: data.setdefault("popis", obj["description"])
                offers = obj.get("offers")
                if isinstance(offers, dict):
                    price = offers.get("price"); cur = offers.get("priceCurrency","")
                    if price:
                        data.setdefault("cena_num_detail", str(price))
                        if cur: data.setdefault("cena_text_detail", f"{price} {cur}")
                cats = obj.get("category") or obj.get("keywords")
                if isinstance(cats, list):
                    data.setdefault("kategorie", " > ".join(map(str, cats)))
                elif isinstance(cats, str):
                    data.setdefault("kategorie", cats)
    return data

def _from_gtm(soup: BeautifulSoup) -> dict:
    g = _sel(soup, ".gtm-data"); out = {}
    if g:
        out["datum_vydani"] = g.get("data-year-published", "")
        out["dostupnost"]   = g.get("data-availability", "")
        out["jazyk_gtm"]    = g.get("data-book-language", "")
        out["pocet_gtm"]    = g.get("data-total-pages", "")
        out["nakladatel_gtm"]= g.get("data-publisher", "")
        out["cena_gtm"]     = g.get("data-price", "")
    return out

def parse_detail_page(soup: BeautifulSoup) -> dict:
    result = {
        "nazev_detail": _t(_sel(soup, "h1.product-detail__title")),
        "isbn": _t(_sel(soup, '[data-cy="detail-isbn"] li')),
        "ean": _t(_sel(soup,  '[data-cy="detail-ean"] li')),
        "nakladatel": _param_li(soup, "publisher"),
        "jazyk": _param_li(soup, "language"),
        "pocet_stran": _param_li(soup, "total-pages"),
        "datum_vydani": "",
        "vazba": _param_li(soup, "binding"),
        "rozmer": " x ".join([p for p in (
            _param_li(soup, "width"),
            _param_li(soup, "height"),
            _param_li(soup, "depth")) if p]),
        "hmotnost": _param_li(soup, "weight"),
        "kategorie": " > ".join([_t(a) for a in soup.select('[data-cy="detail-category"] a')]),
        "dostupnost": _t(_sel(soup, ".availability")) or _t(_sel(soup, ".delivery-time")),
        "cena_text_detail": _t(_sel(soup, '[item-price="sale"]')),
        "cena_num_detail": "",
        "popis": _t(_sel(soup, ".description__detail--full")) or _t(_sel(soup, ".description__detail--short-desktop")),
    }

    if not result["isbn"]:
        m = re.search(r'\b97[89]\d{10}\b', soup.get_text(" ", strip=True))
        if m: result["isbn"] = m.group(0)

    if not result["cena_num_detail"]:
        result["cena_num_detail"] = _parse_price_num(result["cena_text_detail"])

    # JSON-LD добиває порожні поля
    j = _parse_jsonld(soup)
    for k, v in j.items():
        if v and not result.get(k): result[k] = v

    # GTM добиває ще трохи
    g = _from_gtm(soup)
    if g.get("datum_vydani") and not result["datum_vydani"]:
        result["datum_vydani"] = g["datum_vydani"]
    if g.get("dostupnost") and not result["dostupnost"]:
        result["dostupnost"] = g["dostupnost"]
    if g.get("jazyk_gtm") and not result["jazyk"]:
        result["jazyk"] = g["jazyk_gtm"]
    if g.get("pocet_gtm") and not result["pocet_stran"]:
        result["pocet_stran"] = g["pocet_gtm"]
    if g.get("nakladatel_gtm") and not result["nakladatel"]:
        result["nakladatel"] = g["nakladatel_gtm"]
    if g.get("cena_gtm") and not result["cena_num_detail"]:
        result["cena_num_detail"] = _parse_price_num(g["cena_gtm"])
        if not result["cena_text_detail"]:
            result["cena_text_detail"] = f'{g["cena_gtm"]} Kč'
    return result
