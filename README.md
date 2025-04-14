# PodFast API

A backend Flask-based API for summarizing podcasts!

This API powers the PodFast web application, enabling users to upload, transcribe, and generate concise summaries of podcast episodes using AI models.

## How to run (locally)
Requires Python 3.11 and up.

1. **Clone the repository:** 
    ```bash
    git clone https://github.com/your-username/podfast-api.git
    cd podfast-api
    ```

2. **Create a virtual environment and activate it:**  
    ```bash
    python -m venv venv  
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. **Install dependencies:**  
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    - Create a .env file and configure database connection, API keys, and other required settings.

5. **Run the application:**
    ```bash
    python3 app.py 
    ```

6. **Access the API**
    - The API will be available at `http://127.0.0.1:8000`

## API Usage
Example POST request to `/api/summarize`:

Request body:
```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

Response:
```json
{
  "video_info": {
    "title": "Podcast Title",
    "channel": "Channel Name",
    "duration": 3600,
    "description": "Video description..."
  },
  "summary": "Formatted summary of the podcast..."
}
```

This is an example curl POST request:
```bash
curl -X POST http://localhost:8000/api/summarize -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=example"}'
```

This command:
- Makes a POST request to your local API endpoint (example has development endpoint at localhost:8000)
- Sets the Content-Type header to application/json
- Sends a JSON payload with a YouTube URL to summarize
- Will return the summary results (or error) as JSON

## Current Features
1. Temporary Processing: No database storage - audio files are temporarily downloaded, processed, and then deleted
2. Comprehensive Summaries: Structured output with overview, insights, highlights, and recommendations