import os
import cv2
import pygame
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from gtts import gTTS
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import speech_recognition as sr
import sqlite3
import pandas as pd
import csv
from threading import Thread
from PIL import Image, ImageTk

class AnimeChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Bella ChatBot")
        self.root.geometry("1080x720")
        self.root.configure(bg="#2E3440")
        self.root.resizable(True, True)
        
        # Load the idle image and speaking video
        self.idle_image_path = 'idle_image.png'
        self.speaking_video_path = 'speaking_video.mp4'
        
        # Initialize text-to-speech and speech recognition
        self.recognizer = sr.Recognizer()
        
        # Load the model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
        self.model = AutoModelForCausalLM.from_pretrained("distilgpt2")
        self.text_generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        
        # Load the dataset
        self.dataset_path = 'dataset.csv'
        self.load_dataset()
        
        # Initialize pygame for playing audio
        pygame.init()
        
        # Initialize database connection
        self.db_conn = sqlite3.connect('reviews.db')
        self.db_cursor = self.db_conn.cursor()
        
        # Farewell phrases
        self.farewell_phrases = ["goodbye", "bye", "see you", "farewell", "later", "ciao", "adios"]
        
        # Mode toggle
        self.learning_mode = tk.BooleanVar()
        self.learning_mode.set(False)
        
        # Create GUI elements
        self.create_widgets()
        
    def load_dataset(self):
        self.dataset = pd.read_csv(self.dataset_path)
        self.dataset_dict = {q.lower(): a for q, a in zip(self.dataset['question'], self.dataset['answer'])}
        
    def create_widgets(self):
        # Frame for the image and video
        self.image_frame = tk.Frame(self.root, bg="#4C566A", bd=2, relief=tk.SUNKEN)
        self.image_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="nsew")
        
        self.idle_image = Image.open(self.idle_image_path).resize((320, 480), Image.Resampling.LANCZOS)
        self.idle_image_tk = ImageTk.PhotoImage(self.idle_image)
        self.image_label = tk.Label(self.image_frame, image=self.idle_image_tk, bg="#4C566A")
        self.image_label.pack(expand=True)
        
        # Frame for the chat and controls
        self.control_frame = tk.Frame(self.root, bg="#2E3440")
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.toggle_button = tk.Checkbutton(self.control_frame, text="Learning Mode", variable=self.learning_mode, command=self.toggle_mode, font=("Helvetica", 12), bg="#2E3440", fg="#D8DEE9", selectcolor="#4C566A")
        self.toggle_button.grid(row=0, column=0, sticky="w")
        
        self.chat_display = scrolledtext.ScrolledText(self.control_frame, wrap=tk.WORD, width=60, height=20, font=("Helvetica", 12), bg="#3B4252", fg="#ECEFF4")
        self.chat_display.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.input_box = tk.Entry(self.control_frame, width=50, font=("Helvetica", 12))
        self.input_box.grid(row=2, column=0, pady=10, sticky="ew")
        self.input_box.bind("<Return>", lambda event: self.process_input())
        
        self.send_button = tk.Button(self.control_frame, text="Send", command=self.process_input, font=("Helvetica", 12), bg="#5E81AC", fg="#ECEFF4")
        self.send_button.grid(row=2, column=1, padx=5)
        
        self.speak_button = tk.Button(self.control_frame, text="Speak", command=self.speech_input, font=("Helvetica", 12), bg="#5E81AC", fg="#ECEFF4")
        self.speak_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Configure row and column weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        
    def toggle_mode(self):
        mode = "Learning Mode" if self.learning_mode.get() else "Talking Mode"
        self.chat_display.insert(tk.END, f"Switched to {mode}\n")
        
    def display_image(self):
        self.image_label.configure(image=self.idle_image_tk)
        
    def play_video(self):
        cap = cv2.VideoCapture(self.speaking_video_path)
        while pygame.mixer.music.get_busy():
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (320, 480))
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            self.image_label.configure(image=frame)
            self.image_label.image = frame
            self.root.update_idletasks()
            self.root.update()
        cap.release()
        
    def speak(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
        Thread(target=self.play_video).start()
        while pygame.mixer.music.get_busy():
            self.root.update()
        pygame.mixer.music.unload()
        if os.path.exists("response.mp3"):
            os.remove("response.mp3")
        self.display_image()
        
    def recognize_speech(self):
        with sr.Microphone() as source:
            self.chat_display.insert(tk.END, "Listening...\n")
            audio = self.recognizer.listen(source)
        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        
    def get_response(self, user_input):
        user_input_lower = user_input.lower()
        # Check if the user input contains any keywords from the dataset
        for question in self.dataset_dict:
            if all(keyword in user_input_lower for keyword in question.split()):
                return self.dataset_dict[question]
        # If no keywords match, use the text generation pipeline
        response = self.text_generator(user_input, max_length=30, num_return_sequences=1, truncation=True)
        return response[0]['generated_text'].strip()
        
    def ask_for_review(self, question, answer):
        self.chat_display.insert(tk.END, f"Please rate the response (1-10):\n")
        self.chat_display.see(tk.END)
        
        review = simpledialog.askinteger("Input", "Please rate the response (1-10):", parent=self.root, minvalue=1, maxvalue=10)
        if review is not None:
            if review >= 8:
                self.save_response(question, answer)
            elif review < 5:
                better_answer = simpledialog.askstring("Input", "Please provide a better answer:", parent=self.root)
                if better_answer:
                    self.save_response(question, better_answer)
                
    def save_response(self, question, answer):
        question_lower = question.lower()
        # Check if the question already exists in the dataset
        if question_lower in self.dataset_dict:
            self.chat_display.insert(tk.END, f"Question '{question_lower}' already exists in the dataset. Skipping save.\n")
            self.chat_display.see(tk.END)
            return
        # Update the dataset dictionary
        self.dataset_dict[question_lower] = answer
        # Update the CSV file
        with open(self.dataset_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([question_lower, answer])
            
    def process_input(self):
        user_input = self.input_box.get()
        self.input_box.delete(0, tk.END)
        self.chat_display.insert(tk.END, f"User: {user_input}\n")
        self.chat_display.see(tk.END)
        
        if any(phrase in user_input.lower() for phrase in self.farewell_phrases):
            self.speak("Goodbye! Have a great day!")
            self.root.quit()
        else:
            response = self.get_response(user_input)
            self.chat_display.insert(tk.END, f"Bella: {response}\n")
            self.chat_display.see(tk.END)
            self.speak(response)
            if self.learning_mode.get():
                self.ask_for_review(user_input, response)
                
    def speech_input(self):
        user_input = self.recognize_speech()
        self.chat_display.insert(tk.END, f"User: {user_input}\n")
        self.chat_display.see(tk.END)
        
        if any(phrase in user_input.lower() for phrase in self.farewell_phrases):
            self.speak("Goodbye! Have a great day!")
            self.root.quit()
        else:
            response = self.get_response(user_input)
            self.chat_display.insert(tk.END, f"Bella: {response}\n")
            self.chat_display.see(tk.END)
            self.speak(response)
            if self.learning_mode.get():
                self.ask_for_review(user_input, response)
                
    def run(self):
        self.display_image()
        self.root.mainloop()
        
if __name__ == "__main__":
    root = tk.Tk()
    bot = AnimeChatBot(root)
    bot.run()
