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
                "id": company["id"],
                "name": company["properties"].get("name", "Unknown"),
                "industry": company["properties"].get("industry", "Unknown")
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
