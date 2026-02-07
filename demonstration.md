(wsl) user@DESKTOP-NBJUPHP:~/ml-tech-assessment$ python demo_api.py

🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
  TRANSCRIPT ANALYSIS API - DEMONSTRATION
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

🌐 Base URL: http://127.0.0.1:8000

Checking if API server is running...
✅ API server is running!


============================================================
  Step 1: Health Check (GET /health)
============================================================

📤 GET http://127.0.0.1:8000/health

✅ Status: 200
   Response: {
  "status": "healthy"
}

============================================================
  Step 2: Analyze Transcript via GET (GET /analyze)
============================================================

📤 GET http://127.0.0.1:8000/analyze?transcript=Team meeting: Decided to launch feature by Friday. Action: Update docs.

✅ Status: 201
   Response: {
  "id": "bf4ff999-9078-42e4-a64e-eeac66e71842",
  "summary": "The team meeting concluded with the decision to launch a new feature by Friday. It was also agreed that documentation needs to be updated accordingly.",
  "action_items": [
    "Confirm the launch date for the feature is set for Friday.",
    "Assign team members to update the documentation before the launch.",
    "Review the documentation updates to ensure accuracy and completeness.",
    "Conduct a final testing of the feature before the launch day."
  ]
}

============================================================
  Step 3: Analyze Transcript via POST (POST /analyze)
============================================================

📤 POST http://127.0.0.1:8000/analyze
   Request Body: {
  "transcript": "\n    John: Good morning everyone. Let's start the sprint planning meeting.\n    Sarah: I've reviewed the backlog and we have three high-priority items.\n    John: Can you walk us through them?\n    Sarah: First, we need to implement user authentication. Second, the dashboard \n    redesign is due. Third, we have several bug fixes for the payment module.\n    Mike: I can take the authentication task. It should take about three days.\n    Sarah: Great. John, can you handle the dashboard?\n    John: Yes, I'll start tomorrow. Let's schedule a follow-up meeting for Wednesday.\n    Sarah: Perfect. Mike, please document the auth flow before you start coding.\n    Mike: Will do. Should I also update the API documentation?\n    John: Yes, that would be helpful. Meeting adjourned.\n    "
}

✅ Status: 201
   Response: {
  "id": "3b06154b-ab61-45f5-bffb-492cde9b5450",
  "summary": "During the sprint planning meeting, the team discussed three high-priority backlog items: user authentication implementation, dashboard redesign, and bug fixes for the payment module. Mike will take on the authentication task, Sarah will handle the dashboard, and both were instructed to document their processes and update API documentation where necessary. A follow-up meeting has been scheduled for Wednesday to check progress.",
  "action_items": [
    "Mike to implement user authentication and document the authentication flow before starting to code.",
    "John to begin the dashboard redesign starting tomorrow.",
    "Mike to update the API documentation while working on authentication.",
    "Schedule a follow-up meeting for Wednesday to review progress on tasks."
  ]
}

💾 Saved analysis ID: 3b06154b-ab61-45f5-bffb-492cde9b5450

============================================================
  Step 4: Retrieve Analysis by ID (GET /analysis/{id})
============================================================

📤 GET http://127.0.0.1:8000/analysis/3b06154b-ab61-45f5-bffb-492cde9b5450

✅ Status: 200
   Response: {
  "id": "3b06154b-ab61-45f5-bffb-492cde9b5450",
  "summary": "During the sprint planning meeting, the team discussed three high-priority backlog items: user authentication implementation, dashboard redesign, and bug fixes for the payment module. Mike will take on the authentication task, Sarah will handle the dashboard, and both were instructed to document their processes and update API documentation where necessary. A follow-up meeting has been scheduled for Wednesday to check progress.",
  "action_items": [
    "Mike to implement user authentication and document the authentication flow before starting to code.",
    "John to begin the dashboard redesign starting tomorrow.",
    "Mike to update the API documentation while working on authentication.",
    "Schedule a follow-up meeting for Wednesday to review progress on tasks."
  ]
}

============================================================
  Step 5: Retrieve Non-existent Analysis (404 Demo)
============================================================

📤 GET http://127.0.0.1:8000/analysis/non-existent-id-12345

❌ Status: 404
   Response: {
  "detail": "Analysis with ID 'non-existent-id-12345' not found"
}

============================================================
  Step 6: Batch Analyze Transcripts (POST /analyze/batch)
============================================================

📤 POST http://127.0.0.1:8000/analyze/batch
   Request Body: {
  "transcripts": [
    "Call with client: Discussed pricing options. Need to send proposal by Monday.",
    "Dev standup: Sprint ends Friday. Two blockers identified in payment integration.",
    "HR meeting: Onboarding new developer next week. Setup workspace required."
  ]
}

✅ Status: 201
   Response: {
  "results": [
    {
      "id": "82f9bd9d-2b66-4f73-959b-202317dd451a",
      "summary": "The client call focused on discussing various pricing options, with a consensus on needing to send a proposal by Monday to move forward in the process.",
      "action_items": [
        "Finalize pricing options discussed during the call.",
        "Draft the proposal document outlining the agreed pricing.",
        "Ensure the proposal is ready and sent to the client by Monday."
      ]
    },
    {
      "id": "237ca3f4-bdfe-4608-8870-135736bee64c",
      "summary": "In the recent dev standup, the team discussed that the current sprint is set to end on Friday. They identified two potential blockers related to payment integration that may impact the completion of the sprint goals.",
      "action_items": [
        "Investigate and resolve the identified blockers in payment integration by Wednesday",
        "Assign team members to work on specific aspects of the integration to ensure progress",
        "Schedule a follow-up meeting on Thursday to review the status of blockers before the sprint ends"
      ]
    },
    {
      "id": "8abb10fb-65f1-47dc-a2af-bc88ecd50d29",
      "summary": "The meeting focused on the onboarding of a new developer scheduled for next week. Key points discussed included the need to set up the workspace for the new hire before their arrival to ensure a smooth integration into the team.",
      "action_items": [
        "Prepare the workspace for the new developer",
        "Ensure all necessary equipment and software are ready before onboarding",
        "Schedule a welcome meeting for the new developer",
        "Assign a mentor or buddy to assist the new hire during their initial days"
      ]
    }
  ]
}

============================================================
  Step 7: Validation Error Demo (Empty Transcript)
============================================================

📤 POST http://127.0.0.1:8000/analyze
   Request Body: {
  "transcript": ""
}

❌ Status: 422
   Response: {
  "detail": [
    {
      "type": "string_too_short",
      "loc": [
        "body",
        "transcript"
      ],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {
        "min_length": 1
      }
    }
  ]
}

============================================================
  Step 8: API Documentation
============================================================

📚 Swagger UI:  http://127.0.0.1:8000/docs
📚 ReDoc:       http://127.0.0.1:8000/redoc
📚 OpenAPI JSON: http://127.0.0.1:8000/openapi.json

============================================================
  ✅ DEMONSTRATION COMPLETE
============================================================

All API endpoints have been tested successfully!
The application is fully functional.