# Dynatrace Release Summarizer Agent

## Project Structure
- `backend`: FastAPI backend
- `frontend`: React frontend (Vite)

## Getting Started

### Backend (FastAPI)
1. Create and activate your Conda environment.
2. Install dependencies:
   ```sh
   pip install -r backend/requirements.txt
   ```
3. Run the backend:
   ```sh
   uvicorn backend.main:app --reload
   ```

### Frontend (React)
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm run dev
   ```
