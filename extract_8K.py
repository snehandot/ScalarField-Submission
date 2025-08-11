import re
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup

headers = {"User-Agent": "snehandot@gmail.com"}

def clean_text(text):
    return re.sub(r'[\ud800-\udfff]', '', text)

def strip_exhibits(raw_text: str) -> str:
    patterns = [
        r"(?i)\bEX-101",         # XBRL exhibit start
        r"(?i)\bGRAPHIC\b",      # embedded image start
        r"begin 644 ",           # uuencoded image start
        r"(?i)\bSIGNATURES\b"    # signatures section
    ]
    for pat in patterns:
        m = re.search(pat, raw_text)
        if m:
            raw_text = raw_text[:m.start()]
    return raw_text

def strip_binary_chunks(raw_text: str) -> str:
    # Remove long uuencode/base64-like lines starting with M
    return re.sub(r"(?:\nM[ -~]{50,}\n?){5,}", "\n", raw_text)

def extract_8k_items(html_text):
    html_text = clean_text(html_text)
    html_text = strip_exhibits(html_text)
    html_text = strip_binary_chunks(html_text)

    try:
        soup = BeautifulSoup(html_text, "lxml")
    except Exception:
        soup = BeautifulSoup(html_text, "html.parser")

    results = []
    
    # XML-style <itemInformation>
    xml_items = soup.find_all("iteminformation")
    if xml_items:
        for it in xml_items:
            num_tag = it.find("itemnumber")
            title_tag = it.find("itemtitle")
            desc_tag = it.find("itemdescription")
            num = num_tag.get_text(strip=True) if num_tag else None
            title = title_tag.get_text(strip=True) if title_tag else None
            desc = desc_tag.get_text(separator="\n", strip=True) if desc_tag else it.get_text(separator="\n", strip=True)
            results.append({"item_number": num, "item_title": title, "item_text": desc})
        return results

    # Fallback regex scan
    text = soup.get_text("\n")
    pattern = re.compile(r"(?i)(ITEM\s+(\d{1,2}(?:\.\d+)?))")
    matches = list(pattern.finditer(text))
    
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        item_no = m.group(2)
        
        title_line = text[m.start():start].strip()
        title = title_line.replace(f"ITEM {item_no}", "").strip(" .:-\n\t")
        
        content = text[start:end].strip()
        results.append({
            "item_number": item_no,
            "item_title": title if title else None,
            "item_text": content
        })
    
    return results

def extract_8k(top_n=6, max_filings=500):
    print("[INFO] Fetching companies from SEC ticker list...")
    companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
    companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
    companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)

    results = {}

    for _, row in companyData.head(top_n).iterrows():
        cik = row['cik_str']
        ticker = row['ticker']
        print(f"\n[INFO] Processing: {ticker} (CIK: {cik})")

        sub_resp = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers)
        if sub_resp.status_code != 200:
            continue

        sub_json = sub_resp.json()
        recent_filings = pd.DataFrame(sub_json['filings']['recent'])
        eightk_filings = recent_filings[recent_filings['form'] == '8-K']

        filings_list = []
        for _, filing in eightk_filings.head(max_filings).iterrows():
            accession_number = filing['accessionNumber']
            accession_no_nodash = accession_number.replace("-", "")
            file_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_nodash}/{accession_number}.txt"

            print(f"[INFO] Downloading Form 8-K dated {filing['filingDate']} from {file_url}")
            filing_resp = requests.get(file_url, headers=headers)
            if filing_resp.status_code != 200:
                continue

            items_data = extract_8k_items(filing_resp.text)

            filing_entry = {
                "form": filing['form'],
                "filingDate": filing['filingDate'],
                "accessionNumber": accession_number,
                "url": file_url
            }

            for item in items_data:
                key = f"ITEM {item['item_number']}" if item['item_number'] else "ITEM"
                filing_entry[key] = item['item_text']

            filings_list.append(filing_entry)

        results[ticker] = filings_list

    with open("FINAL-8-K.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("[INFO] Saved results to FINAL-8-K.json")

# Run
extract_8k()