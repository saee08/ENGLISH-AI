import streamlit as st
import random
import tempfile
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import pytesseract
import numpy as np
from googletrans import Translator
from gtts import gTTS
import os
import cv2

# Streamlit Page Configuration
st.set_page_config(page_title="AI English Teacher", page_icon="📚")
st.title("Welcome to Your AI English Classroom! 👋")
st.markdown("### Powered by AI")

# Set Tesseract path explicitly for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Check Tesseract availability
tesseract_available = False
try:
    pytesseract.get_tesseract_version()
    tesseract_available = True
except Exception as e:
    st.error(
        f"Tesseract OCR is not installed or not found at '{pytesseract.pytesseract.tesseract_cmd}'. "
        "Handwriting recognition is disabled. Please install Tesseract OCR from: "
        "https://github.com/UB-Mannheim/tesseract/wiki and ensure `pytesseract` is installed "
        "(`pip install pytesseract`). Error: {e}"
    )

# Initialize session state for user progress and canvas
if "user" not in st.session_state:
    class User:
        def __init__(self):
            self.xp = 0
            self.level = 1
            self.streak = 0
        
        def earn_xp(self, amount):
            self.xp += amount
            if self.xp >= self.level * 10:
                self.level += 1
                self.xp = 0
                st.success(f"🎉 Level Up! Welcome to Level {self.level}!")
        
        def maintain_streak(self, correct):
            self.streak = self.streak + 1 if correct else 0
    
    st.session_state.user = User()

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

# Define learning levels with activities
levels = {
    "Level 1 - Alphabets": [
        "Learn the alphabet with pronunciation",
        "Practice letter writing",
        "Letter tracing game",
        "Alphabet song (Audio-Visual)",
        "Speech practice with AI",
        "Flashcards for letter-to-sound association"
    ],
    "Level 2 - Basic Words": [
        "Common words with meanings",
        "Pronunciation test with AI",
        "Word association game",
        "Spelling quizzes",
        "Listening comprehension (Audio)",
        "Word tracing exercises"
    ],
    "Level 3 - Sentences": [
        "Forming basic sentences",
        "Fill in the blanks exercise",
        "Jumbled sentences game",
        "Interactive chat with AI",
        "Sentence dictation",
        "Basic grammar rules (Subject-verb agreement)"
    ],
    "Level 4 - Conversations": [
        "Everyday dialogues practice",
        "Role-playing with AI chatbot",
        "Speaking challenges with pronunciation check",
        "Listening comprehension with native speaker audio",
        "Storytelling practice",
        "Common phrases & idioms"
    ]
}

if "letter_input_key" not in st.session_state:
    st.session_state.letter_input_key = 0

# Utility Functions
def text_to_speech(text, lang='en'):
    """Convert text to speech and return a temporary audio file."""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None
    
# Assume text_to_speech is defined elsewhere
def text_to_speech(text, lang='en'):
    """Convert text to speech and return a temporary audio file."""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

def recognize_handwriting(image_data):
    """Recognize handwritten text from canvas image data with improved accuracy."""
    if not tesseract_available:
        st.error("Handwriting recognition is disabled due to missing Tesseract.")
        return ""
    try:
        # Convert to PIL Image and grayscale
        pil_image = Image.fromarray(image_data.astype(np.uint8))
        grayscale = pil_image.convert("L")
        
        # Display raw input for debugging
        st.image(pil_image, caption="Raw Canvas Input", use_container_width=True)
        
        # Convert to OpenCV format
        img_array = np.array(grayscale)
        
        # Preprocessing: Resize and denoise
        scale_factor = 4  # Higher scale for better resolution
        resized = cv2.resize(img_array, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        denoised = cv2.fastNlMeansDenoising(resized, h=15)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 6
        )
        
        # Morphological operations to enhance strokes
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=3)
        eroded = cv2.erode(dilated, kernel, iterations=1)
        
        # Find contours to isolate the letter
        contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Get bounding box of the largest contour (assumed to be the letter)
            x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
            # Add padding to avoid cutting off edges
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(eroded.shape[1] - x, w + 2 * padding)
            h = min(eroded.shape[0] - y, h + 2 * padding)
            # Crop to the letter
            cropped = eroded[y:y+h, x:x+w]
            
            # Resize cropped image to a standard size for Tesseract
            standard_size = (100, 100)
            cropped_resized = cv2.resize(cropped, standard_size, interpolation=cv2.INTER_CUBIC)
            
            # Display preprocessed cropped image
            st.image(cropped_resized, caption="Cropped and Preprocessed Image for OCR", use_container_width=True)
            
            # OCR with optimized config for single letter
            config = '--psm 10 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            result = pytesseract.image_to_data(cropped_resized, config=config, output_type=pytesseract.Output.DICT)
            
            # Extract text and confidence
            recognized_text = ""
            max_confidence = 0
            for i, text in enumerate(result['text']):
                if text.strip():
                    confidence = float(result['conf'][i])
                    if confidence > max_confidence:
                        recognized_text = text.strip().lower()
                        max_confidence = confidence
            
            if recognized_text:
                st.write(f"Recognized: '{recognized_text}' (Confidence: {max_confidence:.2f}%)")
                if max_confidence < 60:
                    st.warning("Low confidence. Try drawing the letter larger and more distinctly.")
                return recognized_text
            else:
                st.warning("No text recognized. Ensure the letter is large, bold, centered, and without extra marks.")
                return ""
        else:
            st.warning("No letter detected. Draw the letter larger and bolder within the canvas.")
            return ""
    except Exception as e:
        st.error(f"Error recognizing handwriting: {e}")
        return ""

# Level 1: Alphabets Practice
def level_1_alphabets():
    st.subheader("Level 1 - Alphabets")
    st.write("Practice English alphabets below:")
    
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    selected_letter = st.selectbox("Choose a letter to learn:", alphabet, key="letter_select")
    
    # Pronunciation
    if selected_letter:
        st.write(f"Pronunciation for '{selected_letter}':")
        audio_file = text_to_speech(selected_letter)
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            os.unlink(audio_file)  # Clean up
    
    # Handwriting or text input
    if tesseract_available:
        st.write(f"Try writing the letter '{selected_letter}' below:")
        st.info("Tip: Draw the letter large (fill the canvas), bold, and centered. Avoid extra marks.")
        canvas_result = st_canvas(
            stroke_width=6,  # Even thicker strokes
            stroke_color="black",
            background_color="white",
            width=800,  # Larger canvas
            height=400,
            drawing_mode="freedraw",
            key=f"canvas_{st.session_state.canvas_key}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Canvas"):
                st.session_state.canvas_key += 1
        with col2:
            if canvas_result.image_data is not None and st.button("Check Writing"):
                recognized_text = recognize_handwriting(canvas_result.image_data)
                if recognized_text:
                    if recognized_text == selected_letter.lower():
                        st.success("Correct! 🎉")
                        st.session_state.user.earn_xp(2)
                        st.session_state.user.maintain_streak(True)
                        st.session_state.canvas_key += 1  # Clear canvas on success
                        st.session_state.user.maintain_streak(False)
                else:
                    st.error(f"No letter recognized. Try drawing '{selected_letter}' larger, bolder, and centered.")
                    st.session_state.user.maintain_streak(False)
    else:
        st.write(f"Type the letter '{selected_letter}' below (handwriting recognition is disabled):")
        user_input = st.text_input(
            "Enter the letter:",
            key=f"letter_input_{st.session_state.letter_input_key}",
            placeholder=f"Type {selected_letter}"
        )
        if st.button("Check Input"):
            if not user_input:
                st.error("Please enter a letter.")
                st.session_state.user.maintain_streak(False)
            elif user_input.strip().lower() == selected_letter.lower():
                st.success("Correct! 🎉")
                st.session_state.user.earn_xp(2)
                st.session_state.user.maintain_streak(True)
                st.session_state.letter_input_key += 1  # Reset input field
            else:
                st.error(f"Oops! You entered '{user_input}'. Try typing '{selected_letter}'.")
                st.session_state.user.maintain_streak(False)

# Level 2: Basic Words
def level_2_activities():
    st.subheader("Level 2 - Basic Words")
    
    words = {
        "apple": "A fruit that is usually red or green.",
        "dog": "A domesticated carnivorous mammal.",
        "school": "A place where children go to learn.",
        "book": "A set of written or printed pages.",
        "table": "A flat surface with four legs."
    }
    
    if "current_word" not in st.session_state:
        st.session_state.current_word = random.choice(list(words.keys()))
    
    word = st.session_state.current_word
    st.write(f"Word: **{word}**")
    st.write(f"Meaning: {words[word]}")
    
    # Pronunciation
    audio_file = text_to_speech(word)
    if audio_file:
        st.audio(audio_file, format="audio/mp3")
        os.unlink(audio_file)
    
    # Canvas or text input fallback
    if tesseract_available:
        st.write(f"Practice writing the word '{word}' (write clearly and large):")
        canvas_result = st_canvas(
            stroke_width=3,
            stroke_color="black",
            background_color="white",
            width=400,
            height=200,
            drawing_mode="freedraw",
            key=f"canvas_{st.session_state.canvas_key}_word"
        )
        
        if st.button("Clear Canvas"):
            st.session_state.canvas_key += 1
        
        if canvas_result.image_data is not None and st.button("Check Word"):
            recognized_text = recognize_handwriting(canvas_result.image_data)
            st.write(f"Recognized: '{recognized_text}'")
            if recognized_text == word.lower():
                st.success("Correct! 🎉")
                st.session_state.user.earn_xp(3)
                st.session_state.user.maintain_streak(True)
                st.session_state.current_word = random.choice(list(words.keys()))  # New word
            else:
               
                st.session_state.user.maintain_streak(False)
    else:
        st.write(f"Type the word '{word}' below (handwriting recognition is disabled):")
        user_input = st.text_input("Enter the word:", key="word_input")
        if st.button("Check Input"):
            if user_input.strip().lower() == word.lower():
                st.success("Correct! 🎉")
                st.session_state.user.earn_xp(3)
                st.session_state.user.maintain_streak(True)
                st.session_state.current_word = random.choice(list(words.keys()))
            elif user_input:
                
                st.session_state.user.maintain_streak(False)

# Level 3: Sentence Formation with Grammar Lessons
def level_3_activities():
    st.subheader("Level 3 - Grammar and Sentences")
    st.write("Learn different grammar rules by completing sentences!")
    
    # Expanded sentence bank with grammar categories
    sentences = [
        # Verb Tenses
        {"sentence": "I ____ to school every day.", "answer": "go", "category": "Present Tense", 
         "explanation": "Use the present tense 'go' for habits or routines (e.g., 'I go,' 'She goes')."},
        {"sentence": "Yesterday, she ____ a cake.", "answer": "baked", "category": "Past Tense", 
         "explanation": "Use the past tense 'baked' for actions completed in the past."},
        {"sentence": "Tomorrow, we ____ to the park.", "answer": "will go", "category": "Future Tense", 
         "explanation": "Use 'will + verb' (e.g., 'will go') for future actions."},
        
        # Subject-Verb Agreement
        {"sentence": "The dog ____ loudly.", "answer": "barks", "category": "Subject-Verb Agreement", 
         "explanation": "Singular subjects like 'The dog' take singular verbs (e.g., 'barks,' not 'bark')."},
        {"sentence": "The cats ____ in the yard.", "answer": "play", "category": "Subject-Verb Agreement", 
         "explanation": "Plural subjects like 'The cats' take plural verbs (e.g., 'play,' not 'plays')."},
        
        # Articles
        {"sentence": "She has ____ apple.", "answer": "an", "category": "Articles", 
         "explanation": "Use 'an' before words starting with a vowel sound (e.g., 'an apple')."},
        {"sentence": "He rides ____ bike to school.", "answer": "a", "category": "Articles", 
         "explanation": "Use 'a' before words starting with a consonant sound (e.g., 'a bike')."},
        
        # Prepositions
        {"sentence": "The book is ____ the table.", "answer": "on", "category": "Prepositions", 
         "explanation": "Use 'on' for surfaces (e.g., 'on the table')."},
        {"sentence": "We meet ____ noon.", "answer": "at", "category": "Prepositions", 
         "explanation": "Use 'at' for specific times (e.g., 'at noon')."},
        
        # Pronouns
        {"sentence": "____ is my best friend.", "answer": "She", "category": "Pronouns", 
         "explanation": "Use 'She' as a subject pronoun for a female (e.g., 'She is,' not 'Her is')."},
        {"sentence": "I gave the book to ____.", "answer": "them", "category": "Pronouns", 
         "explanation": "Use 'them' as an object pronoun for plural people (e.g., 'to them')."},
        
        # Adjectives/Adverbs
        {"sentence": "The ____ cat slept all day.", "answer": "soft", "category": "Adjectives", 
         "explanation": "Use adjectives like 'soft' to describe nouns (e.g., 'soft cat')."},
        {"sentence": "He runs very ____.", "answer": "quickly", "category": "Adverbs", 
         "explanation": "Use adverbs like 'quickly' to describe verbs (e.g., 'runs quickly')."}
    ]
    
    # Initialize session state for current sentence and grammar progress
    if "current_sentence" not in st.session_state:
        st.session_state.current_sentence = random.choice(sentences)
    if "grammar_progress" not in st.session_state:
        st.session_state.grammar_progress = {cat: 0 for cat in set(s["category"] for s in sentences)}
    
    sentence_data = st.session_state.current_sentence
    sentence = sentence_data["sentence"]
    correct_answer = sentence_data["answer"]
    category = sentence_data["category"]
    explanation = sentence_data["explanation"]
    
    # Display sentence and grammar hint
    st.write(f"Complete the sentence: **{sentence}**")
    st.write(f"Category: {category}")
    st.write(f"Hint: The word starts with '{correct_answer[0].upper()}'")
    
    # User input
    user_answer = st.text_input("Your answer:", key="sentence_input", placeholder="Type the missing word")
    
    # Buttons for checking and skipping
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Check Answer"):
            if not user_answer:
                st.error("Please enter an answer!")
                st.session_state.user.maintain_streak(False)
            elif user_answer.strip().lower() == correct_answer:
                st.success("Correct! 🎉")
                st.session_state.user.earn_xp(5)
                st.session_state.user.maintain_streak(True)
                st.session_state.grammar_progress[category] += 1
                st.write(f"Explanation: {explanation}")
                full_sentence = sentence.replace("____", correct_answer)
                audio_file = text_to_speech(full_sentence)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    os.unlink(audio_file)
                st.session_state.current_sentence = random.choice(sentences)
            else:
                st.error(f"Incorrect! You entered '{user_answer}'. Try again. The answer starts with '{correct_answer[0].upper()}'.")
                st.write(f"Explanation: {explanation}")
                st.session_state.user.maintain_streak(False)
    
    with col2:
        if st.button("Next Sentence"):
            st.session_state.current_sentence = random.choice(sentences)
    
    # Display grammar progress
    with st.expander("Your Grammar Progress"):
        st.write("Mastered grammar topics:")
        for cat, count in st.session_state.grammar_progress.items():
            st.write(f"- {cat}: {count} correct answers")
            st.progress(min(count / 5.0, 1.0))

# Level 4: Conversations
def level_4_activities():
    st.subheader("Level 4 - Conversations 🎤")
    st.write("Practice real-life conversations and have fun talking with AI!")

    # Expanded dialogues with scenarios and multiple acceptable responses
    dialogues = [
        {
            "scenario": "You meet a new friend at a party.",
            "dialogue": "Hello! How are you today?",
            "responses": ["I'm good!", "I'm great, thanks!", "Doing well, how about you?"],
            "follow_up": "Nice to meet you! What’s your favorite hobby?"
        },
        {
            "scenario": "You’re asking a stranger for their name.",
            "dialogue": "Hi, what’s your name?",
            "responses": ["My name is John.", "I’m John!", "John’s my name."],
            "follow_up": "Cool name! Where are you from?"
        },
        {
            "scenario": "You’re a tourist asking about someone’s hometown.",
            "dialogue": "Where are you from?",
            "responses": ["I’m from India.", "I come from India!", "India’s my home."],
            "follow_up": "That’s awesome! What’s it like there?"
        },
        {
            "scenario": "You’re ordering food at a café.",
            "dialogue": "What would you like to eat?",
            "responses": ["I’d like a sandwich.", "A sandwich, please!", "Can I have a sandwich?"],
            "follow_up": "Great choice! Anything to drink?"
        }
    ]

    # Initialize session state
    if "current_dialogue" not in st.session_state:
        st.session_state.current_dialogue = random.choice(dialogues)
    if "conversation_step" not in st.session_state:
        st.session_state.conversation_step = 0  # 0 = initial, 1 = follow-up
    if "conversation_streak" not in st.session_state:
        st.session_state.conversation_streak = 0

    # Current dialogue data
    dialogue_data = st.session_state.current_dialogue
    scenario = dialogue_data["scenario"]
    dialogue = dialogue_data["dialogue"]
    correct_responses = dialogue_data["responses"]
    follow_up = dialogue_data["follow_up"]

    # Display scenario and dialogue
    st.write(f"**Scenario**: {scenario} 🌟")
    if st.session_state.conversation_step == 0:
        st.write(f"Respond to: **{dialogue}**")
        hint = f"Hint: Start with '{correct_responses[0].split()[0]}' or get creative!"
    else:
        st.write(f"Continue the chat: **{follow_up}**")
        hint = "Hint: Keep it friendly and natural!"

    st.write(hint)

    # User input with a fun placeholder
    user_response = st.text_input(
        "Your response:", 
        key="dialogue_input", 
        placeholder="Type your reply here... 😊"
    )

    # Buttons for interaction
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Check Response"):
            if not user_response:
                st.error("Oops! Type something to chat! 🙈")
                st.session_state.user.maintain_streak(False)
            elif any(user_response.strip().lower() == resp.lower() for resp in correct_responses):
                st.success("Awesome reply! 🎉")
                st.session_state.user.earn_xp(5)
                st.session_state.user.maintain_streak(True)
                st.session_state.conversation_streak += 1
                audio_file = text_to_speech(user_response)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    os.unlink(audio_file)
                # Move to follow-up or new dialogue
                if st.session_state.conversation_step == 0:
                    st.session_state.conversation_step = 1
                else:
                    st.session_state.conversation_step = 0
                    st.session_state.current_dialogue = random.choice(dialogues)
            else:
                st.error(f"Not quite! Try something like: '{random.choice(correct_responses)}' 😄")
                st.session_state.user.maintain_streak(False)
                # Bonus XP for creativity if close enough
                if any(word in user_response.lower() for word in correct_responses[0].lower().split()):
                    st.session_state.user.earn_xp(2)
                    st.write("Bonus 2 XP for a creative try! 🌟")

    with col2:
        if st.button("Next Dialogue"):
            st.session_state.current_dialogue = random.choice(dialogues)
            st.session_state.conversation_step = 0
            st.session_state.dialogue_input = ""  # Attempt to clear input (note: may need key reset)

    # Fun feedback and progress
    st.write(f"Conversation Streak: {st.session_state.conversation_streak} 🔥")
    if st.session_state.conversation_streak > 0:
        st.progress(min(st.session_state.conversation_streak / 5.0, 1.0))  # Caps at 5
        if st.session_state.conversation_streak % 3 == 0:
            st.balloons()  # Fun celebration every 3 correct responses

    # Tips section
    with st.expander("Conversation Tips"):
        st.write("- Keep it short and friendly! 😊")
        st.write("- Use words like 'Hi,' 'Thanks,' or 'Cool' to sound natural.")
        st.write("- Don’t worry about small mistakes—have fun chatting!")

# Example integration (assuming larger app context)
if __name__ == "__main__":
    if "user" not in st.session_state:
        class User:
            def __init__(self):
                self.xp = 0
                self.level = 1
                self.streak = 0
            
            def earn_xp(self, amount):
                self.xp += amount
                if self.xp >= self.level * 10:
                    self.level += 1
                    self.xp = 0
            
            def maintain_streak(self, correct):
                self.streak = self.streak + 1 if correct else 0

# Main Function
import streamlit as st

# Placeholder levels dictionary (replace with your actual levels if defined elsewhere)
levels = {
    "Level 1 - Alphabets": ["Learn the alphabet", "Practice writing"],
    "Level 2 - Basic Words": ["Learn basic words", "Spelling practice"],
    "Level 3 - Sentences": ["Form sentences", "Grammar practice"],
    "Level 4 - Conversations": ["Practice dialogues", "Speaking exercises"]
}

# Main Function
def main():
    # Display user progress
    st.sidebar.header("Your Progress")
    st.sidebar.write(f"Level: {st.session_state.user.level}")
    st.sidebar.write(f"XP: {st.session_state.user.xp}/{st.session_state.user.level * 10}")
    st.sidebar.write(f"Streak: {st.session_state.user.streak} days")
    st.sidebar.progress(st.session_state.user.xp / (st.session_state.user.level * 10))
    
    # Level selection with unique key
    level = st.selectbox("Choose a Level:", list(levels.keys()), key="main_level_select")
    
    # Display activities
    st.markdown(f"### {level}")
    for activity in levels[level]:
        st.write(f"- {activity}")
    
    # Run level-specific activities (assuming these functions are defined elsewhere)
    if level == "Level 1 - Alphabets":
        level_1_alphabets()
    elif level == "Level 2 - Basic Words":
        level_2_activities()
    elif level == "Level 3 - Sentences":
        level_3_activities()
    elif level == "Level 4 - Conversations":
        level_4_activities()

if __name__ == "__main__":
    # Initialize user before running main
    if "user" not in st.session_state:
        class User:
            def __init__(self):
                self.xp = 0
                self.level = 1
                self.streak = 0
            
            def earn_xp(self, amount):
                self.xp += amount
                if self.xp >= self.level * 10:
                    self.level += 1
                    self.xp = 0
            
            def maintain_streak(self, correct):
                self.streak = self.streak + 1 if correct else 0
        
        st.session_state.user = User()
    
    main()  # Single call to main after initialization