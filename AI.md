# AI.md

## Generative AI Tools Used
- ChatGPT (GPT-4, accessed via https://chat.openai.com)

## How AI Was Used

### Code Development
ChatGPT was used to:
- Refactor the `routes.py` file for consistency with the assignment's expected test cases.
- Implement consistent error message formatting and proper field names such as `"id"`, `"created_at"`, `"updated_at"`, etc.
- Ensure the correct handling of JSON vs form-data requests in `POST /analysis`.
- Format timestamps in ISO8601 with and without milliseconds depending on the test requirements.
- Suggest helper functions and design logic for validating parameters (e.g., lab ID and patient ID).
- Implement proper 404 and 400 status codes based on spec expectations.

### Debugging and Test Case Fixes
ChatGPT was used to:
- Interpret failed test outputs from the Docker-based test suite (`uqngarg1/coughoverflow:latest`).
- Suggest how to fix KeyError issues in response JSONs by including missing fields.
- Handle failed assertions due to result mismatches or timestamp formatting issues.
- Guide test debugging strategy (e.g., checking what fields were missing in `PUT` and `GET /analysis` responses).

### Docker & Terminal Help
ChatGPT provided:
- Step-by-step guidance to install Docker image/platform compatibility (`--platform=linux/amd64` for Apple Silicon).
- Instructions to run the PAS Flask service (`./local.sh`) and test container.
- Help with base64 encoding of images and submitting them to the API correctly.

### Testing
ChatGPT assisted in:
- Understanding how the provided GitHub Action test suite connects to the local Flask service.
- Writing `curl` commands to simulate API requests (e.g., POSTing a base64 image).
- Fixing final test errors related to timestamp precision and response formatting.

### Assignment Support
ChatGPT also:
- Explained submission steps (e.g., location of `refs.md` and `AI.md`)
- Helped clarify the expectations for citation and referencing of AI-generated content.

## Extent of Use

- Most of the implementation was done by the student.
- ChatGPT served as a debugging assistant, helping identify why tests failed and suggesting exact code lines to change.
- Critical logic and structure (like Flask routes and data validation) were student-led, with ChatGPT refining the structure and responses to pass all automated tests.
- ChatGPT did not generate entire files but provided guidance on modifying specific sections of code.

All ChatGPT usage was acknowledged in this document, and no generative AI tool was used to write full solutions autonomously.

