import customtkinter as ctk

# Configuration globale
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def envoyer_commande(cmd):
    print(f"Commande envoyée : {cmd}")

# Fenêtre principale
app = ctk.CTk()
app.title("🎮 Robot Controller")
app.geometry("350x420")

# Titre
title = ctk.CTkLabel(app, text="Robot Controller", font=("Arial", 20, "bold"))
title.pack(pady=15)

# Frame principale
frame = ctk.CTkFrame(app)
frame.pack(pady=10)

# Fonctions
def avancer(): envoyer_commande("F")
def reculer(): envoyer_commande("B")
def gauche(): envoyer_commande("L")
def droite(): envoyer_commande("R")
def stop(): envoyer_commande("S")

# Boutons directionnels
btn_up = ctk.CTkButton(frame, text="↑", width=70, height=70, corner_radius=20, command=avancer)
btn_left = ctk.CTkButton(frame, text="←", width=70, height=70, corner_radius=20, command=gauche)
btn_stop = ctk.CTkButton(frame, text="STOP", width=70, height=70, corner_radius=20,
                         fg_color="#e63946", hover_color="#c1121f", command=stop)
btn_right = ctk.CTkButton(frame, text="→", width=70, height=70, corner_radius=20, command=droite)
btn_down = ctk.CTkButton(frame, text="↓", width=70, height=70, corner_radius=20, command=reculer)

# Placement
btn_up.grid(row=0, column=1, padx=10, pady=10)
btn_left.grid(row=1, column=0, padx=10, pady=10)
btn_stop.grid(row=1, column=1, padx=10, pady=10)
btn_right.grid(row=1, column=2, padx=10, pady=10)
btn_down.grid(row=2, column=1, padx=10, pady=10)

# Slider vitesse
def changer_vitesse(val):
    print(f"Vitesse : {int(val)}")

slider = ctk.CTkSlider(app, from_=0, to=100, command=changer_vitesse)
slider.pack(pady=15)

label_vitesse = ctk.CTkLabel(app, text="Vitesse")
label_vitesse.pack()

# Mode info
status = ctk.CTkLabel(app, text="Mode TEST", text_color="gray")
status.pack(pady=10)

app.mainloop()