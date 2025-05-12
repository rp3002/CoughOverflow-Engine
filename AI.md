# AI.md

I used AI assistance (ChatGPT) during the development and debugging of the Terraform configuration for Stage 3 of the CoughOverflow project.

Specifically:

- When combining outputs from multiple Terraform files (e.g., `main.tf`, `db.tf`, `sqs.tf`), I used AI to ensure all output variable names were unique and consolidated them into a clean `output.tf` structure when needed.

- For the `deploy.sh` script, I used AI to generate a clean deployment workflow that exported necessary environment variables, ran `terraform init`, `terraform apply`, and extracted the Load Balancer DNS into `api.txt`.

- When organizing files, AI also helped me **decide which Terraform files should be kept or removed**, and how to copy or move them properly between the Stage 2 and Stage 3 folders.

- I used AI to assist in writing a cleaner `Dockerfile` by commenting out unnecessary `COPY .` and suggesting the use of `.dockerignore` to avoid bloating the image.

- For `routes.py`, I used AI to **refine the fallback logic** for GET `/labs/results`, ensuring it returned dummy COVID results with valid filtering (`pending`, `covid`) for test scripts. This fixed issues with `curiosity_test.js` and `epidemic_early_test.js` failing due to empty JSON or invalid result types.

- For `celery_worker.py`, AI helped me **set up the Celery app instance**, configure AWS SQS queue connection settings using environment variables, and correctly parse incoming task payloads to run image analysis using `overflowengine`.

Overall, I only relied on AI when facing infrastructure errors or needing formatting help for scripts and file organization. All core logic and understanding were retained by me.

