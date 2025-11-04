
# 📚 Palmknihy Book Scraper (Python Demo Project)

This repository contains an educational web scraper for extracting book data from an online bookstore (Palmknihy.cz).It is designed to practice **Python, BeautifulSoup, data extraction, and CSV export**.

> ⚠️ This project is for learning and personal research only.
> Please respect website Terms of Service and robots.txt rules.

---

## ✨ Features

- Scrapes book catalog pages
- Follows links to book detail pages
- Extracts book information:
  - Title & author
  - ISBN / EAN
  - Publisher
  - Language
  - Number of pages
  - Binding
  - Dimensions & weight (if available)
  - Categories / genres
  - Availability
  - Price / old price / discount / “from” price
  - Book description
- Saves output to CSV
- Configurable:
  - max pages
  - max items
  - delay between requests
  - detail page scraping toggle
- Retry & User-Agent headers to avoid blocks

---

## 🧰 Tech Stack

| Library            | Purpose          |
| ------------------ | ---------------- |
| `requests`       | HTTP requests    |
| `beautifulsoup4` | HTML parsing     |
| `lxml`           | fast HTML parser |
| Python CSV         | file output      |

---

## 🚀 Usage

### Install requirements

```bash
pip install -r requirements.txt
Run scraper

python src/palmknihy_scraper.py --max-pages 2 --max-items 50 --delay 1.2 --out books.csv
CLI options
Argument	Default	Meaning
--max-pages	3	limit catalog pages
--max-items	50	limit total books
--delay	1.2	delay between requests
--out	knihy.csv	output file
--no-detail	disabled	skip detail pages

Example — catalog only (no detail pages):

python src/palmknihy_scraper.py --max-pages 5 --no-detail


📂 Project Structure

src/
 ├─ http.py              # session & request helpers
 ├─ catalog.py           # catalog page parsing
 ├─ detail.py            # detail page parsing
 ├─ io_utils.py          # CSV writing
 └─ palmknihy_scraper.py # CLI entrypoint
examples/
 └─ sample_output.csv
 └─ preview.png
requirements.txt
README.md

📊 Example Output


### 📊 Data Preview

Below is a preview of the scraped dataset (VS Code view):

![Output](https://github.com/MykolaPrague/palmknihy-book-scraper-demo/blob/main/examples/preview.png)




(Full CSV file in examples/ folder)

🛡️ Legal Notice
Educational / portfolio purposes only

Do not use for commercial automation without permission

Respect target website rules

You are responsible for your usage

⭐ Support
If this project helped you — feel free to star ⭐ the repository 🙂

👤 Author
Mykola S. — Python & Web Scraping Enthusiast
```
