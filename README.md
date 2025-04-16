AI English Teacher

Overview

The AI English Teacher is an interactive web application built using Streamlit to help users learn English through gamified exercises. It supports learning at multiple levels, from alphabets to conversational skills, with features like handwriting recognition, text-to-speech, and grammar exercises. The app tracks user progress with a leveling system and streaks, making learning engaging and rewarding.

Features





Level-Based Learning: Four levels of difficulty:





Level 1 - Alphabets: Learn and practice writing letters with pronunciation and handwriting recognition.



Level 2 - Basic Words: Practice spelling and pronunciation of common words.



Level 3 - Sentences: Learn grammar rules and complete sentences.



Level 4 - Conversations: Engage in dialogue practice with AI.



Handwriting Recognition: Uses Tesseract OCR to recognize handwritten letters/words drawn on a canvas (optional, can fall back to text input).



Text-to-Speech: Powered by gTTS for pronunciation feedback.



Gamification: Earn XP, level up, and maintain streaks for correct answers.



Grammar Lessons: Covers verb tenses, articles, prepositions, pronouns, and more with explanations.



Interactive Canvas: Draw letters/words using streamlit_drawable_canvas.



Progress Tracking: Displays XP, level, and streak in a sidebar with a progress bar.

Prerequisites

To run the application, ensure you have the following installed:





Python 3.8+



Tesseract OCR (for handwriting recognition, optional):





Install from Tesseract GitHub.



Update the Tesseract path in the code:

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



System Dependencies (for OpenCV and Tesseract):





On Windows: Ensure Tesseract is in the system PATH or specify the path.



On Linux: sudo apt-get install tesseract-ocr libtesseract-dev



On macOS: brew install tesseract

Installation





Clone the Repository:

git clone <repository-url>
cd ai-english-teacher



Set Up a Virtual Environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



Install Dependencies: Create a requirements.txt with the following:

streamlit
streamlit-drawable-canvas
pillow
pytesseract
googletrans==4.0.0-rc1
gtts
opencv-python
numpy

Then run:

pip install -r requirements.txt



Verify Tesseract Installation (if using handwriting recognition):

tesseract --version

If not installed, handwriting recognition will be disabled, and the app will use text input.

Running the Application





Start the Streamlit App:

streamlit run app.py

Replace app.py with the name of your Python script.



Access the App: Open your browser and navigate to http://localhost:8501.

Usage





Select a Level: Choose from Levels 1–4 in the dropdown menu.



Complete Activities:





Level 1: Select a letter, listen to its pronunciation, and draw it on the canvas (or type it if Tesseract is unavailable).



Level 2: Learn a word, hear its pronunciation, and write it on the canvas or type it.



Level 3: Complete sentences by filling in the blank with the correct word, guided by grammar hints.



Level 4: Respond to conversational prompts and continue dialogues.



Track Progress: View your level, XP, and streak in the sidebar.



Clear Canvas: Use the "Clear Canvas" button to reset drawings.



Get Feedback: Receive instant feedback on answers, with explanations for grammar in Level 3.

File Structure

ai-english-teacher/
├── app.py                # Main Streamlit application script
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── venv/                 # Virtual environment (if created)

Notes





Handwriting Recognition:





Requires Tesseract OCR and pytesseract.



For best results, draw letters/words large, bold, and centered on the canvas.



Preprocessing (resizing, denoising, thresholding) improves OCR accuracy.



Text-to-Speech:





Uses gTTS, which requires an internet connection.



Temporary audio files are created and deleted after playback.



Session State:





Streamlit’s session state is used to persist user progress, canvas keys, and activity states.



Canvas and input keys are incremented to reset fields after successful attempts.



Limitations:





Handwriting recognition may struggle with unclear or small drawings.



Tesseract must be installed for handwriting features to work.



The app is designed for single-user sessions; progress is not saved across sessions.

Troubleshooting





Tesseract Not Found:





Ensure Tesseract is installed and the path in the code is correct.



Install pytesseract via pip install pytesseract.



Canvas Not Recognizing Input:





Draw larger and bolder letters/words.



Check the debug images (raw and preprocessed) displayed by the app.



Audio Not Playing:





Verify internet connectivity for gTTS.



Check for errors in the Streamlit console.



Streamlit Errors:





Ensure all dependencies are installed (pip install -r requirements.txt).



Run streamlit run app.py from the correct directory.

Future Enhancements





Add more activities (e.g., vocabulary games, listening quizzes).



Implement persistent storage for user progress (e.g., SQLite).



Support multiple languages for translations.



Improve handwriting recognition with machine learning models.



Add user authentication for personalized progress tracking.

Contributing

Contributions are welcome! Please:





Fork the repository.



Create a feature branch (git checkout -b feature-name).



Commit changes (git commit -m "Add feature").



Push to the branch (git push origin feature-name).



Open a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for details.
