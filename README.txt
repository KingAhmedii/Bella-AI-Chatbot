# Bella AI Chatbot

## Overview
Bella is an AI-powered chatbot capable of engaging in interactive conversations through text and voice. It can learn from user feedback and improve its responses over time.

## Features
- Text and voice interaction
- Learning Mode and Talking Mode
- User-friendly graphical interface

## Directory Structure

Bella-AI-Chatbot/
├── README.md
├── requirements.txt
├── anime_chatbot.py
├── dataset.csv
├── assets/
│   ├── idle_image.png
│   └── speaking_video.mp4
├── env/
│   ├── Include/
│   ├── Lib/
│   ├── Scripts/
│   └── ...

Setup Instructions

1. Clone the Repository

git clone https://github.com/KingAhmedii/Bella-AI-Chatbot.git
cd Bella-AI-Chatbot

2. Set Up the Virtual Environment

python -m venv env
Activate the virtual environment:

On Windows:

.\env\Scripts\activate
On macOS/Linux:


source env/bin/activate

3. Install Required Libraries


pip install -r requirements.txt

4. Prepare the Dataset
Ensure the dataset.csv file is in the project directory. If it's not present, create it with the necessary data structure:

plaintext

question,answer
"Hello","Hi there! How can I help you today?"

5. Run the Application


python anime_chatbot.py

Usage
Enter text in the input box or use the voice input button to interact with Bella.
Switch between Learning Mode and Talking Mode using the toggle button.
Provide feedback to help Bella learn and improve.

Contributing
Feel free to fork this repository and contribute by submitting a pull request.
