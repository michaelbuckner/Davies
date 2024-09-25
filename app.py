from flask import Flask, render_template, jsonify, request
from datetime import datetime
import requests  # To send the REST API call to ServiceNow

app = Flask(__name__)

# Mock data for insurance claims with longer descriptions
claims = [
    {
        "id": 1,
        "claimant": "John Doe",
        "policy_number": "POL12345",
        "claim_type": "Auto",
        "description": ("The claimant was involved in a vehicular collision at an intersection on September 1, 2024. "
                        "According to the police report, the accident occurred when another driver ran a red light, "
                        "resulting in a side-impact crash. The claimant's vehicle sustained significant damage to the "
                        "front and side panels, and the airbags were deployed. The claimant reports minor injuries "
                        "requiring medical attention, specifically a fractured wrist. The estimated repair cost for the "
                        "vehicle amounts to $1,500, while the claimant is also seeking coverage for medical bills related "
                        "to the injury. Further investigation is needed to verify the police report and medical documentation."),
        "amount": 1500.00,
        "status": "Pending",
        "submission_date": "2024-09-01",
        "last_updated": "2024-09-05",
        "adjuster": "Jane Adjuster"
    },
    {
        "id": 2,
        "claimant": "Jane Smith",
        "policy_number": "POL67890",
        "claim_type": "Home",
        "description": ("The claimant experienced water damage to their home following a severe storm that occurred on "
                        "August 21, 2024. The storm resulted in heavy rainfall and strong winds that caused part of the "
                        "roof to collapse. The claimant has submitted photographs and a detailed report from a licensed "
                        "contractor estimating the repair cost at $5,000. In addition to the structural damage, the claimant "
                        "also reports water damage to several personal belongings inside the house, including furniture and "
                        "electronics. The insurance policy covers storm-related damage, and further assessment is required "
                        "to confirm the extent of the damage and ensure compliance with policy terms."),
        "amount": 5000.00,
        "status": "Approved",
        "submission_date": "2024-08-21",
        "last_updated": "2024-09-02",
        "adjuster": "John Adjuster"
    },
]

# ServiceNow API credentials and endpoint
SERVICENOW_API_URL = "https://<instance>.service-now.com/api/x_snc_davies/create_and_summarize_case/createandsummarize"
SERVICENOW_USERNAME = ""
SERVICENOW_PASSWORD = ""

@app.route('/')
def index():
    return render_template('index.html', claims=claims)

# API to summarize the claim (calls ServiceNow API)
@app.route('/api/summarize/<int:claim_id>', methods=['POST'])
def summarize_claim(claim_id):
    # Find the claim by ID
    claim = next((c for c in claims if c['id'] == claim_id), None)
    if not claim:
        return jsonify({"success": False, "message": "Claim not found."}), 404

    # Prepare the data payload for the ServiceNow API
    payload = {
        "claimant": claim['claimant'],
        "policy_number": claim['policy_number'],
        "claim_type": claim['claim_type'],
        "description": claim['description'],
        "amount": claim['amount'],
        "status": claim['status'],
        "submission_date": claim['submission_date'],
        "adjuster": claim['adjuster']
    }
        # Send the POST request to ServiceNow and handle the response directly
    try:
        # Send the POST request to ServiceNow
        response = requests.post(SERVICENOW_API_URL, json=payload, auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD))
        
        # Log the raw response for debugging
        print("ServiceNow API Raw Response:", response.text)
        
        # Parse the JSON response
        service_now_data = response.json()
        
        # Corrected: Access the summary from the "result" object
        summary = service_now_data.get("result", {}).get("summary", "No summary available.")
        
        # Return the summary to the frontend
        return jsonify({"success": True, "message": "Claim summarized and created in ServiceNow.", "summary": summary})
    
    except Exception as e:
        return jsonify({"success": False, "message": "Error calling ServiceNow API.", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)