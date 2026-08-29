# WarrantyWise Backend

FastAPI backend for WarrantyWise item and warranty management. Data is stored in MongoDB Atlas and optional item photos are uploaded to a public Google Drive folder.

## Setup

1. Create a virtual environment and install dependencies: `python -m venv .venv` then `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` and set the MongoDB, frontend, JWT, and Google Drive values.
3. Run with `uvicorn app.main:app --reload`.

Interactive API documentation: `http://localhost:8000/docs`.

## API

Authentication: `POST /register`, `POST /login`. Both return a bearer access token. Authenticated user management: `PUT /user/update` and `DELETE /user/delete`.

Authenticated item endpoints: `POST /create`, `GET /get-all`, `GET /get-one?id=<item-id>`, `PUT /update?id=<item-id>`, `DELETE /delete?id=<item-id>`, and `DELETE /bulk-delete` with a JSON array of item IDs.

The two MongoDB collections are `users` and `items`. Passwords are stored as bcrypt hashes, and users can only access their own items. Dates are returned in `DD-MM-YYYY` format. For image uploads, send multipart form data with the `photo` field; `photo_url` can also store an existing URL.

`PUT /user/update` accepts any combination of `name`, `email`, and `password`. `DELETE /user/delete` permanently deletes the authenticated user and that user's items.

## Google Drive

Share the configured folder publicly and provide service-account credentials through `GOOGLE_DRIVE_CREDENTIALS_JSON` or `GOOGLE_DRIVE_CREDENTIALS_FILE`. Grant the service account access to the folder. The API sets `photo` to `true` when a URL exists and `false` otherwise.

## Start script

On macOS/Linux or Git Bash, run `./start.sh`. `HOST` and `PORT` can be overridden, for example: `PORT=8080 ./start.sh`.
