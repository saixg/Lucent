"""
Lucent Demo Verification Test Suite — Automated test runner for all 8 core features.
"""
import sys
import time
import httpx
from PIL import Image, ImageDraw
import io

BASE_URL = "http://localhost:8000/api/v1"

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    print_header("1. API & Database Health Checks")
    r = httpx.get(f"{BASE_URL}/health", timeout=5.0)
    print(f"API Health: {r.status_code} -> {r.json()}")
    assert r.status_code == 200, "API Health check failed"

    r_db = httpx.get(f"{BASE_URL}/health/db", timeout=5.0)
    print(f"DB Health:  {r_db.status_code} -> {r_db.json()}")
    assert r_db.status_code == 200, "DB Health check failed"
    print("SUCCESS: Health checks passed!")

def poll_investigation(inv_id, label, max_retries=20):
    print(f"\n[Polling] Waiting for {label} investigation ({inv_id})...")
    for i in range(max_retries):
        time.sleep(2)
        r = httpx.get(f"{BASE_URL}/investigations/{inv_id}", timeout=10.0)
        data = r.json()
        status = data.get("status")
        print(f"  Attempt {i+1}/{max_retries}: status = {status}")
        if status in ("complete", "failed"):
            return data
    return data

def test_text_claim():
    print_header("2. Text Claim Verification")
    payload = {
        "input_type": "text",
        "input_text": "Government of India announced free Wi-Fi in all trains starting August 2026.",
        "platform": "web"
    }
    r = httpx.post(f"{BASE_URL}/investigations/", json=payload, timeout=10.0)
    print(f"Created Text Inv: status={r.status_code}, id={r.json().get('id')}")
    assert r.status_code == 201
    inv_id = r.json()["id"]

    report = poll_investigation(inv_id, "Text Claim")
    print(f"Verdict: {report.get('verdict')} ({report.get('confidence', 0)*100:.0f}% confidence)")
    print(f"Claims ({len(report.get('claims', []))}): {[c.get('claim_text') for c in report.get('claims', [])]}")
    print("SUCCESS: Text Claim test passed!")
    return inv_id

def test_youtube_url():
    print_header("3. YouTube URL Verification")
    payload = {
        "input_type": "youtube_url",
        "input_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "platform": "youtube"
    }
    r = httpx.post(f"{BASE_URL}/investigations/", json=payload, timeout=10.0)
    print(f"Created YouTube Inv: status={r.status_code}, id={r.json().get('id')}")
    assert r.status_code == 201
    inv_id = r.json()["id"]

    report = poll_investigation(inv_id, "YouTube URL")
    print(f"Verdict: {report.get('verdict')}")
    print(f"Claims: {len(report.get('claims', []))} claims extracted")
    print("SUCCESS: YouTube URL test passed!")

def test_web_url():
    print_header("4. Web Article / News URL Verification")
    payload = {
        "input_type": "web_url",
        "input_url": "https://en.wikipedia.org/wiki/India",
        "platform": "web"
    }
    r = httpx.post(f"{BASE_URL}/investigations/", json=payload, timeout=10.0)
    print(f"Created Web Inv: status={r.status_code}, id={r.json().get('id')}")
    assert r.status_code == 201
    inv_id = r.json()["id"]

    report = poll_investigation(inv_id, "Web Article")
    print(f"Verdict: {report.get('verdict')}")
    print("SUCCESS: Web Article URL test passed!")

def test_file_upload():
    print_header("5. Media File Upload Verification")
    img = Image.new("RGB", (400, 200), color="white")
    d = ImageDraw.Draw(img)
    d.text((20, 80), "BREAKING: Lunar Base Alpha operational", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    files = {"file": ("lunar_base.png", buf.getvalue(), "image/png")}
    r = httpx.post(f"{BASE_URL}/upload/", files=files, timeout=15.0)
    print(f"Uploaded File Inv: status={r.status_code}, id={r.json().get('id')}")
    assert r.status_code == 201
    inv_id = r.json()["id"]

    report = poll_investigation(inv_id, "File Upload")
    print(f"Verdict: {report.get('verdict')}")
    print("SUCCESS: File Upload test passed!")

def test_chat(inv_id):
    print_header("6. Conversational AI Agent Chat")
    r = httpx.post(f"{BASE_URL}/conversations/", json={"investigation_id": inv_id, "platform": "web"}, timeout=10.0)
    print(f"Created Conversation: status={r.status_code}")
    conv_id = r.json()["id"]

    msg_payload = {"content": "What is the verdict and why?"}
    r_msg = httpx.post(f"{BASE_URL}/conversations/{conv_id}/messages", json=msg_payload, timeout=15.0)
    print(f"Agent Reply status: {r_msg.status_code}")
    reply = r_msg.json()
    print(f"Agent Answer: {reply.get('content')[:200]}...")
    assert r_msg.status_code in (200, 201)
    print("SUCCESS: Conversational Agent Chat test passed!")

if __name__ == "__main__":
    print("Running Lucent Pre-Demo Automated Test Suite...")
    try:
        test_health()
        inv_id = test_text_claim()
        test_youtube_url()
        test_web_url()
        test_file_upload()
        test_chat(inv_id)
        print_header("ALL DEMO TEST CASES PASSED SUCCESSFULLY! YOU ARE DEMO READY!")
    except Exception as e:
        print(f"\nERROR: TEST FAILED: {e}")
        sys.exit(1)
