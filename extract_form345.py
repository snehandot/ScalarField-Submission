import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
import time
import re

headers = {"User-Agent": "snehandot@gmail.com"}

def clean_text(text):
    return re.sub(r'[\ud800-\udfff]', '', text)

print("[INFO] Fetching top 10 companies from SEC ticker list...")
companyTickers = requests.get(
    "https://www.sec.gov/files/company_tickers.json",
    headers=headers
)
companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)

results = {}

for company_num, (_, row) in enumerate(companyData.head(6).iterrows(), start=1):
    cik = row['cik_str']
    ticker = row['ticker']
    print(f"\n[INFO] Processing company {company_num}: {ticker} (CIK: {cik})")
    
    print(f"[INFO]   → Fetching submission data for {ticker}...")
    sub_resp = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers)
    if sub_resp.status_code != 200:
        print(f"[WARN]   → Failed to fetch data for {ticker}, skipping...")
        continue

    sub_json = sub_resp.json()
    recent_filings = pd.DataFrame(sub_json['filings']['recent'])

    tenk_filings = recent_filings[recent_filings['form'] == '5']
    print(f"[INFO]   → Found {len(tenk_filings)} 10-Q filings for {ticker}")
    
    filings_list = []
    for file_idx, filing in tenk_filings.head(500).iterrows():
        accession_number = filing['accessionNumber']
        accession_no_nodash = accession_number.replace("-", "")
        file_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_nodash}/{accession_number}.txt"

        print(f"[INFO]     Downloading 10-Q #{len(filings_list)+1} dated {filing['filingDate']} from {file_url}")
        
        filing_resp = requests.get(file_url, headers=headers)
        if filing_resp.status_code != 200:
            print(f"[WARN]       Could not download filing {accession_number}, skipping...")
            continue

        soup = BeautifulSoup(filing_resp.text, "xml")  # XML parser
        reporting_owner = soup.find_all("reportingOwner")
        non_derivative = soup.find_all("nonDerivativeTable")
        derivative = soup.find_all("derivativeTable")


        # soup = None
        # try:
        #     soup = BeautifulSoup(filing_resp.text, "html.parser")
        # except Exception as e:
        #     print("[WARN] html.parser failed, retrying with lxml...", e)
        #     try:
        #         soup = BeautifulSoup(filing_resp.text, "lxml")
        #     except Exception as e2:
        #         print("[WARN] lxml failed, retrying with html5lib...", e2)
        #         try:
        #             soup = BeautifulSoup(filing_resp.text, "html5lib")
        #         except Exception as e3:
        #             print(f"[ERROR] All parsers failed for {accession_number}, skipping...")
        #             continue  # Skip this filing

        # try:
        #     text = clean_text(soup.get_text(separator="\n"))
        # except Exception as e:
        #     print(f"[ERROR] Failed to extract text for {accession_number}, skipping...", e)
        #     continue

        filings_list.append({
            "form": filing['form'],
            "filingDate": filing['filingDate'],
            "accessionNumber": accession_number,
            "url": file_url,
            "reportingOwner": [str(tag) for tag in reporting_owner],
            "nonDerivativeTable": [str(tag) for tag in non_derivative],
            "derivativeTable": [str(tag) for tag in derivative]
        })

        # time.sleep(0.01)

    results[ticker] = filings_list
    print(f"[INFO] → Finished {ticker}: Retrieved {len(filings_list)} filings.")

print("\n[INFO] Saving all filings to all_10q_top6.json...")
with open("FINAL-form5.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("[INFO] Done! File saved as all_10q_top6.json")