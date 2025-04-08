# Clip-Scholar : Leveraging LLMs for AI-Driven Educational Content Generation


## Group Members

| Name                    | Email                       |
|-------------------------|-----------------------------|
| Bharath L               | 22bds013@iiitdwd.ac.in      |
| Gnanesh A R             | 22bds023@iiitdwd.ac.in      |
| Gopal                   | 22bds025@iiitdwd.ac.in      |
| Madhan S                | 22bds036@iiitdwd.ac.in      |
| Nachiket Ganesh Apte    | 22bds041@iiitdwd.ac.in      |

## About the Project
Clipscholar is an application designed to automate the extraction of transcripts from 
YouTube videos, generating structured notes and customizable quizzes.
Developed using Flask, the YouTube Transcript API, and the 
Mistral-Large-Instruct-2411 model, Clipscholar was evaluated 
on 10 educational videos, demonstrating effective summarization 
and quiz generation capabilities. Key features include 
Markdown-formatted note exports and support for multiple 
quiz formats, such as multiple-choice questions (MCQs), 
fill-in-the-blanks, and question-answer pairsHf.


## Prerequisites
- Flask
- Pytohn 3.12
- HTML, CSS, Javascript

## Running the project

### Setting Up the Environment
Run the following commands to install the required Python libraries:
```bash
sudo apt-get install python3.12-venv -y
python3 -m venv env1
source env1/bin/activate
pip install -r requirements.txt
 ```
### Creating and adding API Key for Mistral LLM

- Insert the key at line 15. You may add "Bearer API_KEY" instead of just key if it is not working

- Finally, run the app using the following command from the root folder
flask --app app run --debug or using sudo ./env1/bin/gunicorn -w 2 -b 0.0.0.0:80 app:app


---
## Acknowledgment
We acknowledge the authors for providing the API Key and Open Source Access:
- 