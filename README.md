# 🏋️ Real-Time AI Gym Coach

A real-time AI-powered workout coaching application that uses computer vision to track exercises, count repetitions, analyze workout form, provide AI-generated coaching feedback, and convert feedback into voice guidance.

The application uses a webcam to analyze body movements in real time and provides exercise-specific metrics through an interactive Streamlit interface.

---

## 🚀 Features

- Real-time human pose detection using MediaPipe
- Real-time exercise tracking through webcam
- Automatic repetition counting
- Exercise-specific form analysis
- Support for multiple exercises
- AI-generated workout coaching using Groq
- Voice feedback using Google Text-to-Speech
- Workout progress tracking
- Set and repetition tracking
- Workout history stored using SQLite
- User login system
- Interactive Streamlit interface
- Dark-themed responsive UI

---

## 🏋️ Supported Exercises

The application currently supports:

- Squats
- Push-ups
- Biceps Curls (Dumbbell)
- Shoulder Press
- Lunges

Each exercise has its own detection logic and form-related metrics.

---

## 🧠 How It Works

The application follows a real-time processing pipeline:

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Pose Landmarker
   ↓
Exercise Detector
   ↓
Exercise Metrics
   ↓
Workout Progress
   ↓
AI Coaching
   ↓
Text-to-Speech
```

### 1. Webcam Input

The user's webcam provides live video frames through `streamlit-webrtc`.

### 2. Pose Detection

MediaPipe detects body landmarks such as:

- Shoulders
- Elbows
- Wrists
- Hips
- Knees
- Ankles

These landmarks are used to calculate body angles and movement.

### 3. Exercise Detection

Each exercise has its own detector.

For example, the squat detector analyzes body landmarks to determine:

- Knee angle
- Squat depth
- Back angle
- Repetition state

### 4. Metrics

The detected movement is converted into exercise-specific metrics.

Examples include:

- Repetitions
- Elbow Angle
- Knee Angle
- Depth Status
- Body Alignment
- Hip Status
- Balance Status
- Back Arch Status

### 5. AI Coaching

The detected workout information is passed to the coaching pipeline.

The application uses a Groq-hosted language model to generate short coaching feedback.

### 6. Voice Feedback

The generated coaching message is converted into speech using Google Text-to-Speech.

This allows the application to provide spoken feedback while the user is exercising.

### 7. Workout History

Completed sets are stored in a SQLite database.

The application keeps track of:

- Exercise
- Repetitions
- Sets
- Workout time
- Date

---

## 🛠️ Tech Stack

### Application

- Python
- Streamlit

### Computer Vision

- OpenCV
- MediaPipe
- streamlit-webrtc

### AI Coaching

- Groq API
- Large Language Model

### Voice

- Google Text-to-Speech (gTTS)

### Data Storage

- SQLite

### Data Processing

- Pandas

### Configuration

- python-dotenv

---

## 📁 Project Structure

```text
Real-Time AI Gym Coach/
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── core/
│   ├── base_exercise.py
│   └── __init__.py
│
├── detectors/
│   ├── biceps_curl.py
│   ├── lunges.py
│   ├── pushup.py
│   ├── shoulder_press.py
│   ├── squat.py
│   └── __init__.py
│
├── ml_models/
│   ├── pose_landmarker_full.task
│   └── __init__.py
│
├── services/
│   ├── auth/
│   │   └── login_wall.py
│   │
│   ├── coaching/
│   │   ├── llm.py
│   │   ├── tts.py
│   │   └── voice_pipeline.py
│   │
│   ├── config/
│   │   └── workout_config.py
│   │
│   ├── persistence/
│   │   └── excercise_repository.py
│   │
│   ├── state/
│   │   └── session_state.py
│   │
│   ├── tracking/
│   │   └── metrics.py
│   │
│   ├── ui/
│   │   └── style_loader.py
│   │
│   └── vision/
│       └── exercise_video_processor.py
│
└── static/
    └── style.css
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd "Real-Time AI Gym Coach"
```

### 2. Create a Virtual Environment

It is recommended to use a virtual environment for the project.

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you can activate the environment through Command Prompt or Git Bash instead.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

The AI coaching functionality requires a Groq API key.

Create a file named:

```text
.env
```

in the project root.

Add:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace `your_groq_api_key_here` with your own Groq API key.

### Important

The `.env` file is intentionally **not included in the repository**.

Never commit your API key to GitHub.

The application loads the API key using:

```python
from dotenv import load_dotenv

load_dotenv()
```

---

## ▶️ Run the Application

Start the Streamlit application with:

```bash
uv run streamlit run main.py
```

The application will open in your browser.

---

## 🖥️ How to Use

### 1. Login

Create or enter your username through the login interface.

### 2. Select an Exercise

Choose one of the supported exercises from the workout plan.

### 3. Set Workout Targets

Configure:

- Repetitions per set
- Number of sets

### 4. Start the Workout

Start the workout and allow the application to access your webcam.

Position yourself so your body landmarks are clearly visible.

### 5. Perform the Exercise

The application tracks your movement in real time.

It displays exercise-specific metrics and automatically counts repetitions.

### 6. Receive Coaching

The AI coaching system can provide short feedback about detected form issues.

Voice feedback is generated for supported workout events and form issues.

### 7. View Workout History

Completed workout sets are saved to the SQLite database and displayed in the Workout History section.

---

## 🤖 AI Coaching Pipeline

The coaching system follows this pipeline:

```text
Workout Event
      ↓
Form Issue Detection
      ↓
LLM Coach
      ↓
Text Feedback
      ↓
Text-to-Speech
      ↓
Voice Feedback
```

The application uses exercise metrics to identify possible form issues before sending relevant information to the AI coaching layer.

Examples include:

- Squat depth issues
- Forward leaning
- Push-up alignment
- Hip position
- Biceps curl swinging
- Elbow drifting
- Excessive back arch during shoulder press
- Balance issues during lunges

---

## 💾 Workout Data

Workout information is stored locally using SQLite.

The database contains workout records associated with users.

Stored information includes:

- Exercise
- Repetitions
- Sets
- Time
- Created Date

The local database file is excluded from Git using `.gitignore`.

---

## 🔒 Security

The project uses environment variables for API credentials.

Sensitive files such as:

```text
.env
```

are excluded from version control.

Other local files such as the Python virtual environment, cache files, and local database are also excluded from the repository.

---

## 🔮 Future Improvements

Possible future improvements include:

- More exercise detectors
- Improved pose tracking
- More advanced form analysis
- Personalized workout plans
- Workout analytics and visualizations
- User profiles
- Cloud database support
- Improved voice coaching
- Mobile support
- Model-based exercise classification
- More detailed workout statistics

---

## 📌 Project Status

The current version supports:

- Real-time exercise tracking
- Repetition counting
- Exercise-specific metrics
- AI coaching
- Voice feedback
- User authentication
- Workout history

---

## 👨‍💻 Author

**Arsh Shaikh**

AI/ML Developer | Data Analytics | Computer Vision | Generative AI
