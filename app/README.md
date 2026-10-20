# Archive File Extractor Service

This is a Flask web service that lets you upload a zip or tar archive and find specific files inside it (even inside nested zip/tar files) using a glob search pattern. The app saves the matches to a database and exposes endpoints to check the status and see the results.

## Why I built it this way (My Assumptions)
1. **Background Processing:** Unzipping large files takes time and can time out a web request. I used a standard `ThreadPoolExecutor` to handle the work in the background. When a user uploads a file, they instantly get a `202 Accepted` response with a job ID so they can poll for the status later.
2. **Safety Depth Limit:** To make sure the server doesn't run out of disk space or get stuck in an infinite loop (like a zip bomb), I added a check to stop processing if archives are nested deeper than 5 layers.
3. **Database Writes:** Instead of opening a database connection and inserting a row for every single file found, I collect all matches in a list and use `db.session.bulk_save_objects()` at the very end to save them efficiently in one go.

## How to Set Up and Run Locally

1. Create a virtual environment and install the requirements:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set up your environment variables for your PostgreSQL database (change these to match your local setup):
```powershell
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="extractor"
```

3. Start the Flask server:
```powershell
$env:PYTHONPATH="."
flask run --port=8080
```

## Running the Tests
I wrote 17 unit tests using pytest to mock the file routing and database logic, plus 1 integration test that uses a real zip file on disk. Run them using:
```powershell
$env:PYTHONPATH="."
pytest -v
```

## API Routes

### 1. Health Check
* `GET /health` -> Returns `{"status": "healthy"}` to show the server is up.

### 2. Upload an Archive
* `POST /extractions` -> Upload a file using form-data.
  * Key: `archive` (select your zip file)
  * Key: `pattern` (e.g., `**/*.json`)
* Returns: `202 Accepted` with a `job_id`.

### 3. Check Status
* `GET /extractions/<job_id>` -> Returns whether the job is PENDING, RUNNING, COMPLETED, or FAILED.

### 4. Get Results (With Pagination)
* `GET /extractions/<job_id>/results?limit=10&offset=0` -> Returns a list of files found.

