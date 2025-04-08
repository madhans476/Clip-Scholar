# Clip-Scholar

Clipscholar is an application designed to automate the extraction of transcripts from 
YouTube videos, generating structured notes and customizable quizzes.
Developed using Flask, the YouTube Transcript API, and the 
Mistral-Large-Instruct-2411 model, Clipscholar was evaluated 
on 10 educational videos, demonstrating effective summarization 
and quiz generation capabilities. Key features include 
Markdown-formatted note exports and support for multiple 
quiz formats, such as multiple-choice questions (MCQs), 
fill-in-the-blanks, and question-answer pairsHf.

Steps to Run:
1. Virtual environment creation
    sudo apt-get install python3.12-venv -y
    python3 -m venv env1
    source env1/bin/activate
    pip install -r requirements.txt


2. Create API Key for Mistal LLM

3. Insert the key at line 15. You may add "Bearer API_KEY" instead of just key if it is not working

4. Next, run the app using the following command from the root folder
flask --app app run --debug or using sudo ./env1/bin/gunicorn -w 2 -b 0.0.0.0:80 app:app


Note - Usage of YouTube Transcriptor API may not work as some of the web addresses are blocked by it thinking they are bots. So, kindly use Supadata API in that case.

For that, generate the API Key for Supadata API from the website:
https://supadata.ai/ - First 100 requests are free
You'll just need to change at line 47 and import necessary requirements. For more details, visit the website.