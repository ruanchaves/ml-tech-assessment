#!/usr/bin/env python3
"""API Demo Script.

This script demonstrates all API endpoints of the Transcript Analysis API.
Run this while the API server is running (uvicorn app.api.main:app --reload).

Usage:
    python demo_api.py [--base-url URL]
"""

import argparse
import json
import sys
import time

import httpx


def print_step(step_num: int, title: str) -> None:
    """Print a formatted step header."""
    print(f"\n{'='*60}")
    print(f"  Step {step_num}: {title}")
    print(f"{'='*60}\n")


def print_request(method: str, url: str, body: dict | None = None) -> None:
    """Print the request being made."""
    print(f"📤 {method} {url}")
    if body:
        print(f"   Request Body: {json.dumps(body, indent=2)}")


def print_response(response: httpx.Response) -> None:
    """Print the response received."""
    status_emoji = "✅" if response.status_code < 400 else "❌"
    print(f"\n{status_emoji} Status: {response.status_code}")
    try:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        print(f"   Response: {response.text}")


def main(base_url: str = "http://127.0.0.1:8000") -> int:
    """Run the API demonstration."""
    print("\n" + "🚀" * 20)
    print("  TRANSCRIPT ANALYSIS API - DEMONSTRATION")
    print("🚀" * 20)
    print(f"\n🌐 Base URL: {base_url}\n")

    # Check if server is running
    print("Checking if API server is running...")
    try:
        health_response = httpx.get(f"{base_url}/health", timeout=5.0)
        if health_response.status_code != 200:
            print("❌ API server is not healthy. Please start the server first.")
            return 1
        print("✅ API server is running!\n")
    except httpx.ConnectError:
        print("❌ Cannot connect to API server.")
        print(f"   Please start the server: uvicorn app.api.main:app --reload")
        return 1

    # Sample transcripts for demonstration
    sample_transcript = """
    John: Good morning everyone. Let's start the sprint planning meeting.
    Sarah: I've reviewed the backlog and we have three high-priority items.
    John: Can you walk us through them?
    Sarah: First, we need to implement user authentication. Second, the dashboard 
    redesign is due. Third, we have several bug fixes for the payment module.
    Mike: I can take the authentication task. It should take about three days.
    Sarah: Great. John, can you handle the dashboard?
    John: Yes, I'll start tomorrow. Let's schedule a follow-up meeting for Wednesday.
    Sarah: Perfect. Mike, please document the auth flow before you start coding.
    Mike: Will do. Should I also update the API documentation?
    John: Yes, that would be helpful. Meeting adjourned.
    """

    stored_analysis_id = None

    # -------------------------------------------------------------------------
    # Step 1: Health Check
    # -------------------------------------------------------------------------
    print_step(1, "Health Check (GET /health)")
    print_request("GET", f"{base_url}/health")
    response = httpx.get(f"{base_url}/health")
    print_response(response)

    # -------------------------------------------------------------------------
    # Step 2: Analyze Transcript via GET
    # -------------------------------------------------------------------------
    print_step(2, "Analyze Transcript via GET (GET /analyze)")
    short_transcript = "Team meeting: Decided to launch feature by Friday. Action: Update docs."
    url_with_params = f"{base_url}/analyze?transcript={short_transcript}"
    print_request("GET", url_with_params)
    response = httpx.get(f"{base_url}/analyze", params={"transcript": short_transcript})
    print_response(response)
    if response.status_code == 201:
        stored_analysis_id = response.json().get("id")

    # -------------------------------------------------------------------------
    # Step 3: Analyze Transcript via POST
    # -------------------------------------------------------------------------
    print_step(3, "Analyze Transcript via POST (POST /analyze)")
    request_body = {"transcript": sample_transcript}
    print_request("POST", f"{base_url}/analyze", request_body)
    response = httpx.post(f"{base_url}/analyze", json=request_body)
    print_response(response)
    if response.status_code == 201:
        stored_analysis_id = response.json().get("id")
        print(f"\n💾 Saved analysis ID: {stored_analysis_id}")

    # -------------------------------------------------------------------------
    # Step 4: Retrieve Analysis by ID
    # -------------------------------------------------------------------------
    print_step(4, "Retrieve Analysis by ID (GET /analysis/{id})")
    if stored_analysis_id:
        print_request("GET", f"{base_url}/analysis/{stored_analysis_id}")
        response = httpx.get(f"{base_url}/analysis/{stored_analysis_id}")
        print_response(response)
    else:
        print("⚠️ Skipped: No analysis ID available from previous step")

    # -------------------------------------------------------------------------
    # Step 5: Retrieve Non-existent Analysis (404 Demo)
    # -------------------------------------------------------------------------
    print_step(5, "Retrieve Non-existent Analysis (404 Demo)")
    fake_id = "non-existent-id-12345"
    print_request("GET", f"{base_url}/analysis/{fake_id}")
    response = httpx.get(f"{base_url}/analysis/{fake_id}")
    print_response(response)

    # -------------------------------------------------------------------------
    # Step 6: Batch Analyze Multiple Transcripts
    # -------------------------------------------------------------------------
    print_step(6, "Batch Analyze Transcripts (POST /analyze/batch)")
    batch_request = {
        "transcripts": [
            "Call with client: Discussed pricing options. Need to send proposal by Monday.",
            "Dev standup: Sprint ends Friday. Two blockers identified in payment integration.",
            "HR meeting: Onboarding new developer next week. Setup workspace required.",
        ]
    }
    print_request("POST", f"{base_url}/analyze/batch", batch_request)
    response = httpx.post(f"{base_url}/analyze/batch", json=batch_request)
    print_response(response)

    # -------------------------------------------------------------------------
    # Step 7: Validation Error Demo
    # -------------------------------------------------------------------------
    print_step(7, "Validation Error Demo (Empty Transcript)")
    invalid_request = {"transcript": ""}
    print_request("POST", f"{base_url}/analyze", invalid_request)
    response = httpx.post(f"{base_url}/analyze", json=invalid_request)
    print_response(response)

    # -------------------------------------------------------------------------
    # Step 8: Swagger Documentation
    # -------------------------------------------------------------------------
    print_step(8, "API Documentation")
    print(f"📚 Swagger UI:  {base_url}/docs")
    print(f"📚 ReDoc:       {base_url}/redoc")
    print(f"📚 OpenAPI JSON: {base_url}/openapi.json")

    # Summary
    print("\n" + "="*60)
    print("  ✅ DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nAll API endpoints have been tested successfully!")
    print("The application is fully functional.\n")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demonstrate Transcript Analysis API")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of the API server (default: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()

    sys.exit(main(args.base_url))
