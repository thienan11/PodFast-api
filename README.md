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
