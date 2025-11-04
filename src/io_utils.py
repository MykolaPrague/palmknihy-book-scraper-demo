import os, csv

FIELDNAMES = [
    "nazev_knihy","author","format_k","cena_text","cena_num","detail_url",
    "nazev_detail","isbn","ean","nakladatel","jazyk","pocet_stran","datum_vydani",
    "vazba","rozmer","hmotnost","kategorie","dostupnost",
    "cena_text_detail","cena_num_detail","popis",
    "cena_before","discount","from_price",
]

def write_csv(rows: list[dict], file: str):
    write_header = not os.path.exists(file) or os.path.getsize(file) == 0
    with open(file, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        if write_header: w.writeheader()
        w.writerows(rows)
