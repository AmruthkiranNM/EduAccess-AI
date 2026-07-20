# EduAccess AI

EduAccess AI is a web application that helps teachers instantly generate lesson plans and quizzes using Generative AI. It is designed to assist educators, especially in rural and under-resourced schools, by saving time in preparation.

## 🚀 Features
- **Lesson Plan Generation**: Instantly creates structured lesson plans.
- **Quiz Generation**: Provides multiple-choice quizzes with answer keys.
- **Multilingual Support**: Generate content in the preferred language.

## 🛠️ Setup Instructions (Local)

1. Ensure you have Python 3.8+ installed.
2. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` in the root folder of the project (`EduAccess-AI/`) and add your Gemini API Key.
5. Run the application:
   ```bash
   python app.py
   ```
6. Open your browser and navigate to `http://localhost:5000`.

## ☁️ AWS Deployment (High Level)
1. Launch an EC2 Instance (Ubuntu).
2. Install Python, Nginx, and Gunicorn.
3. Clone this repository.
4. Set up an environment variable `GEMINI_API_KEY` on the server.
5. Configure Nginx as a reverse proxy to Gunicorn running the Flask app on port 5000.
