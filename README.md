# AI-Powered Sales/Onboarding Assistant

### Project Overview

The **AI-Powered Sales/Onboarding Assistant** is a full-stack web application designed to automate and streamline the client onboarding process. The system uses an intelligent agent to listen to sales call recordings, transcribe the conversation, and automatically extract key client information. This extracted data is then presented to an onboarder for review, approval, and final storage in a centralized database.

This project was developed as a final year capstone, showcasing a practical application of modern web development and artificial intelligence technologies.

### Key Features

* **Secure User Authentication:** Onboarders can securely log in to access the application's features.
* **Audio Transcription:** An AI agent powered by the **Groq API** transcribes call recordings with low latency.
* **AI-Powered Data Extraction:** A custom agent, configured with the **Model Context Protocol (MCP)**, extracts structured information (client name, company, contact details) from the call transcripts.
* **Review & Approval Workflow:** A dedicated dashboard allows human onboarders to review, edit, and either approve or reject the AI-extracted data.
* **Centralized Client Database:** All approved client information is saved to a clean, searchable database for easy access.
* **Responsive Frontend:** A modern **ReactJS** frontend ensures a seamless user experience on both desktop and mobile devices.

### Technologies Used

#### Backend
* **Framework:** Django (Python)
* **API:** Django REST Framework
* **Database:** PostgreSQL
* **Asynchronous Tasks:** Celery with Redis as a message broker
* **AI Integration:** Groq API for Speech-to-Text and LLM-based information extraction
* **Microservice Protocol:** Model Context Protocol (MCP)

#### Frontend
* **Framework:** ReactJS
* **UI/Styling:** Standard CSS (responsive design)
* **State Management:** React hooks (`useState`, `useEffect`)
* **API Client:** Axios

### Getting Started (Local Development)

To run this project locally, follow these steps.

#### Prerequisites
* Python 3.9+
* Node.js and npm
* PostgreSQL
* Redis
* Groq API Key (`.env` file)

#### 1. Backend Setup
1.  Navigate to the `backend/` directory.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your PostgreSQL database and user.
4.  Create a `.env` file with your credentials:
    ```ini
    GROQ_API_KEY="your_api_key_here"
    DB_NAME="ai_onboarding_db"
    DB_USER="onboarding_user"
    DB_PASSWORD="your_password"
    ```
5.  Run database migrations and create a superuser:
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```
6.  Start the backend services in separate terminals:
    ```bash
    # Terminal 1: Django server
    python manage.py runserver

    # Terminal 2: Celery worker
    celery -A core worker -l info -P solo

    # Terminal 3: Redis server
    redis-server
    ```
7.  Ensure your `mcpserver` is also running in a separate terminal:
    ```bash
    # Terminal 4: MCP server
    uvicorn main:mcp_app --host 0.0.0.0 --port 8001
    ```

#### 2. Frontend Setup
1.  Navigate to the `frontend/` directory.
2.  Install Node.js packages:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```

The application will be accessible at `http://localhost:5173`.

### API Endpoints

The project exposes a RESTful API with the following key endpoints:

* `POST /api/token/`: Authenticates a user and returns an auth token.
* `POST /api/call-recordings/`: Uploads a new audio file for processing.
* `GET /api/call-recordings/`: Retrieves a list of all call recordings for the current user.
* `GET /api/extracted-info/{id}/`: Fetches the AI-extracted data for a specific call.
* `POST /api/extracted-info/{id}/approve/`: Approves the extracted data and saves it to the final `Client` table.
* `POST /api/extracted-info/{id}/reject/`: Rejects the extracted data.
* `GET /api/clients/`: Retrieves a list of all approved client records.