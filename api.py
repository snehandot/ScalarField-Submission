from sec_api import ExtractorApi


API_KEY="8b60dde50ff4bcfd02f003e6b941054eb4fe222305ab290a5a349f86a9e597d6"

filing_10_k_url = 'https://www.sec.gov/Archives/edgar/data/1318605/000156459021004599/tsla-10k_20201231.htm'

def order(url,sec):
    extractorApi = ExtractorApi(API_KEY)
    print(url,sec[0])
    try:
        item_1_text = extractorApi.get_section(url, sec[0], 'text')
    except Exception as e:
        item_1_text = None
        print(f"Error: {e}")
    print('Extracted Item 1 (Text)')

    return item_1_text

# order("2")