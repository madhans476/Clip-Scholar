from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import json
import io
import re
from youtube_transcript_api import YouTubeTranscriptApi
from mistralai import Mistral
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

api_key = "BHOYy25hmsTZ5hZrAObwW9UQRDjldiLI"
def run_mistral(user_message, model="mistral-large-latest"):
    client = Mistral(api_key=api_key)
    messages = [
        {"role":"user", "content":user_message}
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )
    return (chat_response.choices[0].message.content)

# Cache for generated notes
notes_cache = {}
# Cache for fact checks
fact_check_cache = {}

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript from YouTube video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        return str(e)

def get_transcript(video_id):
    """Get transcript from YouTube video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        return str(e)

def generate_notes(transcript_text):
    """Generate notes from transcript using Hugging Face API."""
    
    prompt = f"""I have a YouTube video transcript of an education related video. Please create comprehensive, structured notes that:
    1. Identify and organize the main topics and subtopics with clear headings
    2. Incorporate relevant notes, context, or text from external sources to enrich the educational content
    3. Include key points, definitions, examples, and detailed explanations of the content
    4. Format the notes in proper markdown with headings, bullet points, and emphasis where appropriate
    5. Add relevant citations to academic papers, books, or authoritative sources where appropriate using APA format [Author, Year]
    6. Include a "References" section at the end with the full citations
    
    Transcript:
    {transcript_text}
    """
    
    return run_mistral(prompt)


def generate_quiz(notes, quiz_type, num_questions):
    """Generate quiz based on notes content."""
    
    prompt_templates = {
        "mcq": f"""Based on only the main topic of the following notes, generate {num_questions} multiple-choice questions (MCQs).
        For each question:
        1. Create a clear question about an important concept
        2. Provide 4 options (A, B, C, D)
        3. Indicate the correct answer
        4. Format as a JSON array of objects with keys: "question", "options" (array), "correctAnswer" (index)
        
        Notes:
        {notes}""",
        
        "fill_blanks": f"""Based on only the main topic of the following notes, generate {num_questions} fill-in-the-blank questions.
        For each question:
        1. Create a sentence with an important term or concept replaced by a blank
        2. Provide the correct answer
        3. Format as a JSON array of objects with keys: "question", "answer"
        
        Notes:
        {notes}""",
        
        "qa": f"""Based on only the main topic of the following notes, generate {num_questions} question and answer pairs.
        For each pair:
        1. Create a detailed question about an important concept
        2. Provide a comprehensive answer
        3. Format as a JSON array of objects with keys: "question", "answer"
        
        Notes:
        {notes}"""
    }
    
    prompt = prompt_templates.get(quiz_type.lower())
    
    response = run_mistral(prompt)
    try:
        # Find JSON-like content between square brackets
        json_match = re.search(r'\[\s*{.+}\s*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return {"error": "Could not extract quiz data from generated response"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in generated quiz", "raw": response}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

recently_processed = []

@app.route('/api/extract', methods=['POST'])
def extract_notes():
    data = request.json
    youtube_url = data.get('youtube_url')
    
    if not youtube_url:
        return jsonify({"error": "No YouTube URL provided"}), 400
    
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    # Create cache key that includes style and citations preference
    cache_key = f"{video_id}"

    video_title = get_video_title(video_id)
    
    # Check cache
    if cache_key in notes_cache:
        update_recently_processed(video_id, video_title)
        return jsonify({
            "notes": notes_cache[cache_key]["content"],
            "video_id": video_id,
            "video_title": video_title,
            "recently_processed": recently_processed[:3]
        })
    
    transcript = get_transcript(video_id)
    
    notes = generate_notes(transcript)
    

    
    # Store in cache
    notes_cache[cache_key] = {
        "content": notes,
    }

    update_recently_processed(video_id, video_title)
    
    return jsonify({
        "notes": notes,
        "video_id": video_id,
        "video_title": video_title,
        "recently_processed": recently_processed[:3]
    })

def get_video_title(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text.replace(' - YouTube', '')
        return title
    except Exception:
        return f"Video {video_id}"

# Function to update recently processed list
def update_recently_processed(video_id, title):
    # Check if video already in list
    for video in recently_processed:
        if video['id'] == video_id:
            # Move to top of list (most recent)
            recently_processed.remove(video)
            recently_processed.insert(0, {
                'id': video_id, 
                'title': title,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return

    # Add new video to the top of the list
    recently_processed.insert(0, {
        'id': video_id, 
        'title': title,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Keep only the most recent 10 videos
    if len(recently_processed) > 10:
        recently_processed.pop()

# Add a new API endpoint to get recently processed videos
@app.route('/api/recent-videos', methods=['GET'])
def get_recent_videos():
    return jsonify(recently_processed[:5])  # Return top 5 recent videos


@app.route('/api/notes/<video_id>', methods=['GET'])
def get_video_notes(video_id):
    cache_key = f"{video_id}"
    if cache_key in notes_cache:
        video_title = get_video_title(video_id)
        return jsonify({
            "notes": notes_cache[cache_key]["content"],
            "video_id": video_id,
            "video_title": video_title
        })
    else:
        return jsonify({"error": "Notes not found for this video"}), 404

@app.route('/api/generate-quiz', methods=['POST'])
def create_quiz():
    data = request.json
    video_id = data.get('video_id')
    quiz_type = data.get('quiz_type')
    num_questions = data.get('num_questions', 5)
    
    if not video_id or not quiz_type:
        return jsonify({"error": "Missing parameters"}), 400
    
    # Create cache key that includes style and citations preference
    cache_key = f"{video_id}"
    
    if cache_key not in notes_cache:
        return jsonify({"error": "Notes not found. Please generate notes first."}), 404
    
    quiz_data = generate_quiz(notes_cache[cache_key]["content"], quiz_type, num_questions)

    return jsonify(quiz_data)

@app.route('/api/download/<video_id>')
def download_notes(video_id):
    
    cache_key = f"{video_id}"
    
    if cache_key not in notes_cache:
        return jsonify({"error": "Notes not found"}), 404
    
    notes_content = notes_cache[cache_key]["content"]
    buffer = io.BytesIO()
    buffer.write(notes_content.encode('utf-8'))
    buffer.seek(0)
    
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"youtube_notes_{video_id}.md",
        mimetype="text/markdown"
    )

if __name__ == '__main__':
    app.run(debug=True)