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

def get_stage_labels():
    url = "https://api.hubapi.com/crm/v3/pipelines/deals"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    
    stage_map = {}
    for stage in data["results"][0]["stages"]:
        stage_map[stage["id"]] = stage["label"]
    return stage_map

def get_deals_with_companies():
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    params = {
        "limit": 100,
        "associations": "companies",
        "properties": "dealstage"
    }

    all_deals = []
    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        all_deals.extend(data.get("results", []))

        if "paging" in data and "next" in data["paging"]:
            params["after"] = data["paging"]["next"]["after"]
        else:
            break

    return all_deals

def get_company_industries(company_ids):
    industries = {}

    for i in range(0, len(company_ids), 100):
        batch = company_ids[i:i+100]
        url = "https://api.hubapi.com/crm/v3/objects/companies/batch/read"
        payload = {
            "properties": ["industry"],
            "inputs": [{"id": cid} for cid in batch]
        }

        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()

        for company in data.get("results", []):
            cid = company.get("id")
            industry = company.get("properties", {}).get("industry") or "Unknown"
            industries[cid] = industry

    return industries

@app.route("/")
def industry_counts_for_deal_closed_won():
    stage_labels = get_stage_labels()
    all_deals = get_deals_with_companies()

    # Filter to only DEAL CLOSED - WON deals
    closed_won_deals = []
    company_ids_needed = set()

    for deal in all_deals:
        props = deal.get("properties", {})
        stage_id = props.get("dealstage")
        stage_name = stage_labels.get(stage_id, "Unknown")

        if stage_name == "DEAL CLOSED - WON":
            associations = deal.get("associations", {})
            companies = associations.get("companies", {}).get("results", [])
            deal_entry = {
                "id": deal.get("id"),
                "company_id": companies[0]["id"] if companies else None
            }
            closed_won_deals.append(deal_entry)
            if companies:
                company_ids_needed.add(companies[0]["id"])

    # Get industries for all needed companies
    company_industries = get_company_industries(list(company_ids_needed))

    # Count industries per deal
    industry_counts = {}
    for deal in closed_won_deals:
        company_id = deal["company_id"]
        industry = company_industries.get(company_id, "Unknown")
        industry_counts[industry] = industry_counts.get(industry, 0) + 1

    return jsonify(industry_counts)

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