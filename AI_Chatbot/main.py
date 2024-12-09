import random
import json
import pickle

import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow import keras
from keras.models import Sequential,load_model

import numpy as np
import speech_recognition as sr
import pyttsx3
import time

lemmatizer = WordNetLemmatizer()
intents = json.loads(open("E:\mental health support platform\AI_Chatbot\intents.json").read())

words = pickle.load(open('E:\mental health support platform\AI_Chatbot\words.pkl', 'rb'))
classes = pickle.load(open('E:\mental health support platform\AI_Chatbot\classes.pkl', 'rb'))
model = load_model('E:\mental health support platform\AI_Chatbot\chatbot_model.h5')

symptom_database = {
   "headache": {
        "guidance": "Stay hydrated, rest in a quiet room, and consider over-the-counter pain relief.",
        "medication": ["Ibuprofen", "Paracetamol"],
    },
    "fever": {
        "guidance": "Stay hydrated, rest, and use a cold compress. Consider taking fever reducers.",
        "medication": ["Acetaminophen", "Ibuprofen"],
    },
    "anxiety": {
        "guidance": "Practice deep breathing, mindfulness, or talk to a friend. Consider seeing a therapist for ongoing issues.",
        "medication": ["Consult a healthcare provider for medication recommendations."],
    },
    "cold": {
        "guidance": "Stay warm, drink hot fluids, and rest. Over-the-counter decongestants may help.",
        "medication": ["Decongestants", "Antihistamines"],
    },
    "insomnia": {
        "guidance": "Avoid caffeine before bed, maintain a sleep schedule, and try relaxation techniques.",
        "medication": ["Melatonin supplements", "Consult a doctor for prescription options."],
    },
    "depression": {
        "guidance": "Reach out to a mental health professional or trusted individual. Practice self-care, and stay active.",
        "medication": ["Antidepressants (prescription only)", "Consider therapy."],
    },
    # Add more symptoms and corresponding solutions here...
}
def clean_up_sentence(sentence):
	sentence_words = nltk.word_tokenize(sentence)
	sentence_words = [lemmatizer.lemmatize(word)
					for word in sentence_words]

	return sentence_words


def bag_of_words(sentence):
	sentence_words = clean_up_sentence(sentence)
	bag = [0] * len(words)

	for w in sentence_words:
		for i, word in enumerate(words):
			if word == w:
				bag[i] = 1
	return np.array(bag)


def predict_class(sentence):
	bow = bag_of_words(sentence)
	res = model.predict(np.array([bow]))[0]

	ERROR_THRESHOLD = 0.25

	results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

	results.sort(key=lambda x: x[1], reverse=True)

	return_list = []

	for r in results:
		return_list.append({'intent': classes[r[0]],
							'probability': str(r[1])})
	return return_list


def get_response(intents_list, intents_json):
	tag = intents_list[0]['intent']
	list_of_intents = intents_json['intents']

	result = ''

	for i in list_of_intents:
		if i['tag'] == tag:
			result = random.choice(i['responses'])
			break
	return result

def check_symptoms(symptoms):
    symptoms_lower = symptoms.lower()
    for symptom, data in symptom_database.items():
        if symptom in symptoms_lower:
            return data
    return None
# This function will take the voice input converted
# into string as input and predict and return the result in both
# text as well as voice format.
def calling_the_bot(symptoms):
    result = check_symptoms(symptoms)
    if result:
        print(f"Guidance: {result['guidance']}")
        print(f"Suggested Medications: {', '.join(result['medication'])}")
        time.sleep(1) 
        return result
    else:
        print("Sorry, I couldn't find any specific guidance for your symptoms.")
        return None

def handle_voice_input():
    if __name__ == '__main__':
       print("Bot is Running")

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    engine = pyttsx3.init()
    rate = engine.getProperty('rate')

    # Adjust speech rate
    engine.setProperty('rate', 175)

    # Adjust volume
    volume = engine.getProperty('volume')
    engine.setProperty('volume', 1.0)

    # Get voices for male/female selection
    voices = engine.getProperty('voices')

    # Welcome message
    engine.say("Hello, I am Bagley, your personal Mental Talking Healthcare Chatbot. How Can I assist you today?")
    engine.runAndWait()
    engine.say("If you want to continue with a male voice, please say 'Male.' Otherwise, say 'Female.'")
    engine.runAndWait()

    # Asking for the MALE or FEMALE voice
    with mic as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for voice preference...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            text = "male"  # Default to male if no clear input
        except sr.RequestError as e:
            print(f"API error: {e}")
            text = "male"  # Default to male if an API issue occurs

    # Set the voice based on user input
    if text.lower() == "female":
        engine.setProperty('voice', voices[1].id)
        print("You have chosen to continue with a Female Voice")
    else:
        engine.setProperty('voice', voices[0].id)
        print("You have chosen to continue with a Male Voice")

    while True:
        with mic as symptom:
            print("I'm listening. Please tell me how you're feeling or your symptoms.")
            engine.say("You can talk to me about how you're feeling or your symptoms.")
            engine.runAndWait()
            try:
                recognizer.adjust_for_ambient_noise(symptom, duration=0.5)
                symp = recognizer.listen(symptom)
                text = recognizer.recognize_google(symp)
                engine.say(f"You said: {text}")
                engine.runAndWait()

                engine.say(
                            "Scanning our database for your symptoms. Please wait."
                        )
                engine.runAndWait()
                

                # Call the function with the user's symptoms
                analysis = calling_the_bot(text)
                if analysis:
                    engine.say(f"Here is some guidance: {analysis['guidance']}")
                    engine.say(f"Possible medications include: {', '.join(analysis['medication'])}")
                else:
                    engine.say(engine, "I'm sorry, I couldn't find any guidance for your symptoms.")

                engine.runAndWait()
                
            except sr.UnknownValueError:
                engine.say("Sorry, either your symptom is unclear to me or it is not present in our database. Please try again.")
                engine.runAndWait()
                print("Sorry, either your symptom is unclear to me or it is not present in our database. Please try again.")
                continue
        # Ask if the user wants to continue
        with mic as source:
            engine.say("Would you like to continue? Say 'Yes' to continue or 'No' to exit.")
            engine.runAndWait()
            try:
                recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Listening for user decision...")
                audio = recognizer.listen(source)
                decision = recognizer.recognize_google(audio).lower()
                print(f"You said: {decision}")
                if decision in ["no", "exit", "stop"]:
                    engine.say("Thank you for talking to me. Take care and stay safe.")
                    engine.runAndWait()
                    break
            except sr.UnknownValueError:
                engine.say("Sorry, I didn't catch that. Please try again.")
                engine.runAndWait()
                continue

