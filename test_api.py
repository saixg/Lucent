import time
import requests

def test_pipeline():
    print("Submitting investigation...")
    # Create investigation
    r = requests.post("http://localhost:8000/api/v1/investigations/", json={
        "input_type": "text",
        "input_text": "The moon landing was faked by Stanley Kubrick.",
        "platform": "web"
    })
    
    if r.status_code != 201:
        print(f"Error creating: {r.status_code} - {r.text}")
        return
        
    inv = r.json()
    inv_id = inv["id"]
    print(f"Created investigation {inv_id}. Polling status...")
    
    # Poll status
    for _ in range(60):
        time.sleep(2)
        r = requests.get(f"http://localhost:8000/api/v1/investigations/{inv_id}/status")
        status_data = r.json()
        print(f"Status: {status_data['status']}")
        if status_data["status"] in ["complete", "failed"]:
            break
            
    print("Pipeline finished.")
    
    # Get full result
    r = requests.get(f"http://localhost:8000/api/v1/investigations/{inv_id}")
    full = r.json()
    print("\n--- RESULT ---")
    print(f"Verdict: {full.get('verdict')}")
    print(f"Confidence: {full.get('confidence')}")
    print(f"Summary: {full.get('summary')}")
    print(f"Claims found: {len(full.get('claims', []))}")
    for c in full.get('claims', []):
        print(f" - {c.get('claim_text')} ({c.get('verdict')}) - {len(c.get('evidence', []))} evidence")

if __name__ == "__main__":
    test_pipeline()
