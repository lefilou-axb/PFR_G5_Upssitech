# --- Iportation de toutes les bibliotheques ---
import subprocess
import speech_recognition as sr
import os
from gtts import gTTS
import time
from playsound import playsound

# --- Fonction de synthese ---
def text_to_speech(text):
    print(f"Robot dit : {text}")
    try:
        speech = gTTS(text=text, lang="fr", slow=False)
        speech_file = "speech.mp3"
        speech.save(speech_file)
        # Commande Windows pour lire le fichier
        #os.system(f"start {speech_file}") 
        # Commande python pour lire le fichier
        playsound(speech_file)
    except Exception as e:
        print(f"Erreur audio : {e}")

# --- Fonction de tokenisation ---
def normaliser_transcription(transcription):
    if not transcription: return []
    # On découpe la phrase en mots
    chaine_tokenisee = transcription.split()
    return chaine_tokenisee

# --- Boucle prinicpale ---
if __name__ == "__main__":
    r = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            # Réglage du bruit ambiant
            print("Réglage du bruit ambiant... (ne parlez pas 1 sec)")
            r.adjust_for_ambient_noise(source)
            
            # Ecoute de la source micro par défaut
            print("Je vous écoute (Speak!)...")
            audio_data = r.listen(source)
            print("Fin de l'écoute (End!)")
            
            try:
                # Reconnaissance de la voix par Google
                transcription = r.recognize_google(audio_data, language="fr-FR")
                print(f"Vous avez dit : {transcription}")
                
                # Tokenisation
                tokens = normaliser_transcription(transcription)
                print(f"Mots clés : {tokens}")
                #subprocess.run(["../text_engine/main", transcription]) #modifier le .exe par celui de ny aina
                
                # Réponse vocale
                text_to_speech("Commande reçu: " + transcription)
                
            except sr.UnknownValueError:
                print("Je n'ai pas compris la phrase.")
            except sr.RequestError:
                print("Pas de connexion internet pour la reconnaissance.")
                
    except OSError:
        print("Erreur : Aucun microphone trouvé. Vérifiez vos paramètres Windows.")
