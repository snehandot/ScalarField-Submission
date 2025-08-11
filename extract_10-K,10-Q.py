import re
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup

headers = {"User-Agent": "snehandot@gmail.com"}


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
        eightk_filings = recent_filings[recent_filings['form'] == '10-Q']

        filings_list = []
        for _, filing in eightk_filings.head(max_filings).iterrows():
            accession_number = filing['accessionNumber']
            accession_no_nodash = accession_number.replace("-", "")
            file_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_nodash}/{accession_number}.txt"

            print(f"[INFO] Downloading Form 8-K dated {filing['filingDate']} from {file_url}")
            filing_resp = requests.get(file_url, headers=headers)
            if filing_resp.status_code != 200:
                continue


            filing_entry = {
                "form": filing['form'],
                "filingDate": filing['filingDate'],
                "accessionNumber": accession_number,
                "url": file_url
            }



            filings_list.append(filing_entry)

        results[ticker] = filings_list

    with open("10-Q.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("[INFO] Saved results to FINAL-8-K.json")

# Run
extract_8k()