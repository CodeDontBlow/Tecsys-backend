from .extractor import extract_from_html
from .scrapper import process_pn, DEFAULT_SLEEP_BETWEEN_REQUESTS

pns = {
  "10": "132119RP",
#   "11": "691351500005",
#   "12": "8D2-11LCS",
#   "13": "AHEF1000",
#   "01": "B32932A3224K189",
#   "03": "LLG2G151MELZ25",
#   "06": "STTH102AY",
#   "08": "LTC3625EDE#PBF/LTC3625IDE#PBF",
#   "09": "132119"
}



html_results = {}
for pn in pns.values():
    html_content = process_pn(pn, sleep_between=DEFAULT_SLEEP_BETWEEN_REQUESTS)
    if html_content:
        html_results[pn] = html_content

print(html_results.keys())


target_supplier = 'avnet'

for html in html_results.values():
    result = extract_from_html(html,target_supplier)
    print(result)