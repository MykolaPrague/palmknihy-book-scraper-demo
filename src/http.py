from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests, time
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "cs,en;q=0.9,uk;q=0.8",
    "Referer": "https://www.palmknihy.cz/",
    "Connection": "keep-alive",
}

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    retries = Retry(total=3, backoff_factor=0.6,
                    status_forcelist=(429, 500, 502, 503, 504),
                    allowed_methods=frozenset(["GET","HEAD"]),
                    raise_on_status=False)
    ad = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    s.mount("http://", ad); s.mount("https://", ad)
    return s

def fetch_soup(session: requests.Session, url: str, delay: float) -> BeautifulSoup:
    r = session.get(url, timeout=20); r.raise_for_status()
    # lxml faster; if not — fallback to built-in parser
    try:
        soup = BeautifulSoup(r.text, "lxml")
    except Exception:
        soup = BeautifulSoup(r.text, "html.parser")
    if delay > 0: time.sleep(delay)
    return soup
