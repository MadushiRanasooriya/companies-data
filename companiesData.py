import requests
from flask import Flask, jsonify
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}"
}

def get_companies():
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    headers = HEADERS
    params = {
        "properties": "name,industry",
        "limit": 100
    }

    all_companies = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        for company in data.get("results", []):
            company_info = {
                "id": company.get("id", "Unknown"),
                "name": company.get("properties", {}).get("name", "Unknown"),
                "industry": company.get("properties", {}).get("industry", "Unknown")
            }
            all_companies.append(company_info)

        if "paging" in data and "next" in data["paging"]:
            params["after"] = data["paging"]["next"]["after"]
        else:
            break

    return all_companies

@app.route("/companies")
def companies():
    companies = get_companies()
    return jsonify(companies)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


# import requests
# from flask import Flask, jsonify
# import os
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

# HEADERS = {
#     "Authorization": f"Bearer {HUBSPOT_TOKEN}"
# }

# def get_deals_with_companies():
#     url = "https://api.hubapi.com/crm/v3/objects/deals"
#     params = {
#         "limit": 100,
#         "associations": "companies"
#     }

#     deals = []

#     while True:
#         response = requests.get(url, headers=HEADERS, params=params)
#         data = response.json()
#         deals.extend(data.get("results", []))

#         if "paging" in data and "next" in data["paging"]:
#             params["after"] = data["paging"]["next"]["after"]
#         else:
#             break

#     company_ids = set()
#     for deal in deals:
#         associations = deal.get("associations", {})
#         companies = associations.get("companies", {}).get("results", [])
#         for company in companies:
#             company_ids.add(company["id"])

#     return list(company_ids)

# def get_companies_by_ids(company_ids):
#     industry_counts = {}
#     for i in range(0, len(company_ids), 100):
#         batch = company_ids[i:i+100]
#         ids = ",".join(batch)
#         url = f"https://api.hubapi.com/crm/v3/objects/companies/batch/read"
#         payload = {
#             "properties": ["industry"],
#             "inputs": [{"id": cid} for cid in batch]
#         }

#         response = requests.post(url, headers=HEADERS, json=payload)
#         data = response.json()
#         for company in data.get("results", []):
#             industry = company.get("properties", {}).get("industry") or "Unknown"
#             industry_counts[industry] = industry_counts.get(industry, 0) + 1

#     return industry_counts

# @app.route("/")
# def industry_counts_for_companies_with_deals():
#     company_ids = get_deals_with_companies()
#     counts = get_companies_by_ids(company_ids)
#     return jsonify(counts)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)