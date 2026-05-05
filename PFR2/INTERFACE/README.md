# Robot CTL — Interface Web (Raspberry Pi 3B)

Interface web Flask pour piloter un robot Arduino via Raspberry Pi 3B.

## Structure du projet

```
robot/
├── app.py                  ← Serveur Flask
├── requirements.txt        ← Dépendances Python
├── templates/
│   └── index.html          ← Interface web
└── text_engine/            ← Moteur de requêtes texte (C)
    ├── pfr_text.out        ← Exécutable compilé (make)
    ├── lexique_fr.txt
    ├── lexique_en.txt
    ├── config_lang.txt
    └── commands.txt        ← Généré à l'exécution
```

## Installation sur Raspberry Pi

```bash
# Cloner / copier le projet
cd ~
cp -r robot_ctl/ ~/robot/

# Installer les dépendances Python
pip3 install -r requirements.txt

# Compiler le moteur C
cd ~/robot/text_engine/
make

# Revenir à la racine
cd ~/robot/
```

## ⚠️ Chemin hardcodé dans le source C

Le fichier `text_request.c` exporte les commandes vers `/home/ny_aina/commands.txt`.

**Option A** — Créer un lien symbolique (recommandé, sans recompilation) :
```bash
ln -s ~/robot/text_engine/commands.txt /home/ny_aina/commands.txt
```

**Option B** — Modifier et recompiler :
```c
// Dans text_request.c, ligne export_commands(...) :
export_commands("/home/<VOTRE_USER>/robot/text_engine/commands.txt", cmds, c);
```
Puis `make` dans `text_engine/`.

## Lancement

```bash
cd ~/robot/
python3 app.py
```

Accès depuis n'importe quel appareil du réseau local :
```
http://<IP_du_Pi>:5000
```

Pour trouver l'IP du Pi :
```bash
hostname -I
```

## Lancement automatique au démarrage (optionnel)

```bash
# Créer un service systemd
sudo nano /etc/systemd/system/robot-ctl.service
```

```ini
[Unit]
Description=Robot CTL Flask Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/<USER>/robot/app.py
WorkingDirectory=/home/<USER>/robot
User=<USER>
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable robot-ctl
sudo systemctl start robot-ctl
```

## Modes de pilotage

### Mode Manuel
- **D-pad** : maintenir pour avancer/reculer/tourner, relâcher pour stopper
- **Raccourcis clavier** : `Z/↑` avancer · `S/↓` reculer · `Q/←` gauche · `D/→` droite · `Espace/Échap` stop
- **Commande précise** : saisir une valeur en mètres ou degrés puis valider

### Mode Texte
- Saisir une phrase en français ou anglais
- Le moteur C (`pfr_text.out`) analyse la phrase et génère des commandes
- Cocher "Envoyer à l'Arduino" pour exécuter automatiquement
- Utiliser `Ctrl+Entrée` pour soumettre rapidement

## Protocole série Arduino

| Commande           | Action                    |
|--------------------|---------------------------|
| `forward <m>\n`    | Avancer de X mètres       |
| `backward <m>\n`   | Reculer de X mètres       |
| `left <deg>\n`     | Tourner à gauche de X°    |
| `right <deg>\n`    | Tourner à droite de X°    |
| `stop 0\n`         | Arrêt immédiat            |

## Variables d'environnement

| Variable     | Défaut        | Description             |
|--------------|---------------|-------------------------|
| `ROBOT_PORT` | `/dev/ttyUSB0`| Port série de l'Arduino |

```bash
ROBOT_PORT=/dev/ttyACM0 python3 app.py
```
