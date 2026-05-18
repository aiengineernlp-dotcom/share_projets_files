# je veux un code qui convertie une image en webp
#
# Parfait 👌
# Voici **3 façons simples** de convertir une image en WebP selon ton environnement.
#
# ---
#
# # ✅ 1️⃣ En ligne de commande (macOS / Linux / serveur)
#
# Si `cwebp` est installé :
#
# ```bash
# cwebp input.jpg -o output.webp
# ```
#
# ### 🔹 Avec qualité personnalisée (ex: 80)
#
# ```bash
# cwebp -q 80 input.png -o output.webp
# ```
#
# ### 🔹 Convertir toutes les images d’un dossier
#
# ```bash
# for file in *.jpg; do
#   cwebp -q 80 "$file" -o "${file%.jpg}.webp"
# done
# ```
#
# 👉 Installer cwebp si nécessaire :
#
# **Mac :**
#
# ```bash
# brew install webp
# ```
#
# **Ubuntu :**
#
# ```bash
# sudo apt install webp
# ```
#
# ---
#
# # ✅ 2️⃣ En PHP (utile pour WordPress / backend)
#
# ```php
# <?php
# $source = 'image.jpg';
# $destination = 'image.webp';
# $quality = 80;
#
# $image = imagecreatefromjpeg($source);
# imagewebp($image, $destination, $quality);
# imagedestroy($image);
#
# echo "Conversion réussie !";
# ?>
# ```
#
# ⚠️ Assure-toi que GD est activé :
#
# ```bash
# php -m | grep gd
# ```
#
# ---
#
# # ✅ 3️⃣ En Python (automatisation locale)
#
# ```python
# from PIL import Image
#
# img = Image.open("input.jpg")
# img.save("output.webp", "webp", quality=80)
#
# print("Conversion réussie !")
# ```
#
# Installer Pillow :
#
# ```bash
# pip install pillow
# ```
#
# ---
#
# # 🎯 Recommandation pour toi (Erman 💻)
#
# Vu que tu veux automatiser :
#
# 👉 La meilleure solution pour ton workflow (compression + webp + logo) serait :
#
# * CLI avec `imagemagick`
# * ou script Python automatisé
# * ou un script bash qui fait tout en une commande
#
# Si tu veux, je peux te créer un script complet :
# compression + conversion WebP + ajout automatique du logo 🔥
#
#
# ===============================================================================================
#
# en python
#
# Parfait Erman 👌🔥
# On va faire ça proprement en **Python**, version simple puis version pro (automatisée).
#
# ---
#
# # ✅ 1️⃣ Version simple – Convertir UNE image en WebP
#
# Installe Pillow si ce n’est pas déjà fait :
#
# ```bash
# pip install pillow
# ```
#
# ### Script basique :
#
# ```python
# from PIL import Image
#
# input_path = "input.jpg"
# output_path = "output.webp"
#
# img = Image.open(input_path)
# img.save(output_path, "WEBP", quality=80)
#
# print("Conversion réussie ✅")
# ```
#
# ---
#
# # ✅ 2️⃣ Version pro – Convertir TOUT un dossier en WebP
#
# Ce script :
#
# * Convertit .jpg / .jpeg / .png
# * Garde le même nom
# * Met qualité 80
# * Ignore les erreurs
#
# ```python
# import os
# from PIL import Image
#
# input_folder = "images"
# quality = 80
#
# for filename in os.listdir(input_folder):
#     if filename.lower().endswith((".jpg", ".jpeg", ".png")):
#         input_path = os.path.join(input_folder, filename)
#         output_path = os.path.join(
#             input_folder,
#             os.path.splitext(filename)[0] + ".webp"
#         )
#
#         try:
#             img = Image.open(input_path)
#             img.save(output_path, "WEBP", quality=quality)
#             print(f"Converti : {filename} ✅")
#         except Exception as e:
#             print(f"Erreur avec {filename} ❌ : {e}")
#
# print("Terminé 🚀")
# ```
#
# ---
#
# # ✅ 3️⃣ Version avancée – Optimisée + conversion RGBA propre
#
# Gère transparence PNG correctement :
#
# ```python
# import os
# from PIL import Image
#
# input_folder = "images"
# quality = 80
#
# for filename in os.listdir(input_folder):
#     if filename.lower().endswith((".jpg", ".jpeg", ".png")):
#         input_path = os.path.join(input_folder, filename)
#         output_path = os.path.join(
#             input_folder,
#             os.path.splitext(filename)[0] + ".webp"
#         )
#
#         try:
#             img = Image.open(input_path).convert("RGBA")
#             img.save(output_path, "WEBP", quality=quality, method=6)
#             print(f"Converti : {filename} ✅")
#         except Exception as e:
#             print(f"Erreur : {e}")
#
# print("Toutes les images sont converties 🚀")
# ```
#
# `method=6` = meilleure compression (plus lente mais meilleure qualité).
#
# ---
#
# # 🔥 Si tu veux aller encore plus loin
#
# Je peux te faire un script qui :
#
# * ✔️ Compresse
# * ✔️ Convertit en WebP
# * ✔️ Ajoute ton logo automatiquement
# * ✔️ Supprime les fichiers originaux
# * ✔️ Met tout dans un dossier ready-for-upload WordPress
#
# Vu ton workflow compression → webp → logo, ça te ferait gagner énormément de temps 😉
#
#
# ===============================================================================================
#
# ok
#
# Parfait Erman 🔥💻
# Voici ton **script automatique complet** :
#
# ✅ Compression
# ✅ Conversion WebP
# ✅ Ajout automatique du logo
# ✅ Dossier prêt pour upload WordPress
#
# ---
#
# # 📦 Installation
#
# ```bash
# pip install pillow
# ```
#
# ---
#
# # 📂 Structure recommandée
#
# ```
# project/
# │
# ├── images/          # tes images originales
# ├── logo.png         # ton logo (fond transparent recommandé)
# └── script.py
# ```
#
# ---
#
# # 🚀 SCRIPT COMPLET
#
# ```python
# import os
# from PIL import Image
#
# # ===== CONFIG =====
# input_folder = "images"
# output_folder = "output"
# logo_path = "logo.png"
#
# quality = 80          # qualité WebP
# logo_scale = 0.15     # taille du logo (15% largeur image)
# margin = 30           # marge du logo
#
# # ==================
#
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)
#
# logo = Image.open(logo_path).convert("RGBA")
#
# for filename in os.listdir(input_folder):
#     if filename.lower().endswith((".jpg", ".jpeg", ".png")):
#         try:
#             input_path = os.path.join(input_folder, filename)
#             base_name = os.path.splitext(filename)[0]
#             output_path = os.path.join(output_folder, base_name + ".webp")
#
#             # Ouvre image principale
#             img = Image.open(input_path).convert("RGBA")
#
#             # ===== Redimension logo proportionnel =====
#             logo_width = int(img.width * logo_scale)
#             logo_ratio = logo_width / logo.width
#             logo_height = int(logo.height * logo_ratio)
#
#             resized_logo = logo.resize((logo_width, logo_height))
#
#             # ===== Position bas droite =====
#             position = (
#                 img.width - logo_width - margin,
#                 img.height - logo_height - margin
#             )
#
#             # ===== Fusion =====
#             img.paste(resized_logo, position, resized_logo)
#
#             # ===== Sauvegarde en WebP =====
#             img.save(output_path, "WEBP", quality=quality, method=6)
#
#             print(f"✔ {filename} converti avec logo")
#
#         except Exception as e:
#             print(f"❌ Erreur avec {filename} : {e}")
#
# print("🚀 Toutes les images sont prêtes dans le dossier OUTPUT")
# ```
#
# ---
#
# # 🎯 Ce que fait ce script
#
# * Redimensionne le logo automatiquement
# * Le place en bas à droite
# * Compresse en WebP
# * Garde qualité 80
# * Utilise compression optimisée (`method=6`)
# * Crée un dossier `/output` prêt pour WordPress
#
# ---
#
# # 🔥 Si tu veux encore plus pro
#
# Je peux ajouter :
#
# * 🔄 Suppression automatique des originaux
# * 📏 Redimensionnement max largeur (ex: 1920px)
# * 📦 Script CLI que tu lances avec `python optimize.py`
# * ⚡ Version ultra rapide avec multiprocessing
# * 🧠 Script intelligent qui détecte déjà les WebP
#
# Tu veux la version **production level pour TheKnowHow** ?
#
#  😉
#
#
# ===============================================================================================
#
#commennt je lance le script
#
# Parfait 👌 on va faire ça étape par étape (macOS puisque tu es sur Mac).
#
# ---
#
# # ✅ 1️⃣ Vérifier que Python est installé
#
# Dans le Terminal :
#
# ```bash
# python3 --version
# ```
#
# Si tu vois une version (ex: Python 3.11.x) → c’est bon ✅
# Sinon dis-moi et je t’aide.
#
# ---
#
# # ✅ 2️⃣ Installer Pillow (si pas encore fait)
#
# ```bash
# pip3 install pillow
# ```
#
# ---
#
# # ✅ 3️⃣ Mettre les fichiers au bon endroit
#
# Structure :
#
# ```
# project/
# │
# ├── images/
# │   ├── image1.jpg
# │   ├── image2.png
# │
# ├── logo.png
# └── script.py
# ```
#
# 👉 Mets ton script dans un fichier appelé :
#
# ```
# script.py
# ```
#
# ---
#
# # ✅ 4️⃣ Aller dans le dossier du projet
#
# Dans le Terminal :
#
# ```bash
# cd /chemin/vers/ton/project
# ```
#
# Exemple si c’est sur le bureau :
#
# ```bash
# cd ~/Desktop/project
# ```
#
# ---
#
# # ✅ 5️⃣ Lancer le script
#
# ```bash
# python3 script.py
# ```
#
# 🎉 Si tout va bien tu verras :
#
# ```
# ✔ image1.jpg converti avec logo
# ✔ image2.png converti avec logo
# 🚀 Toutes les images sont prêtes dans le dossier OUTPUT
# ```
#
# ---
#
# # 📂 Résultat
#
# Un nouveau dossier sera créé :
#
# ```
# project/output/
# ```
#
# Avec tes images en `.webp` prêtes pour WordPress.
#
# ---
#
# # 🔥 Astuce pro (gain de temps)
#
# Tu peux créer un alias pour lancer plus vite :
#
# Dans ton `.zshrc` :
#
# ```bash
# alias optimize='python3 script.py'
# ```
#
# Ensuite tu tapes juste :
#
# ```bash
# optimize
# ```
#
# ---
#
# Si tu veux, je peux te faire une version encore plus propre :
#
# 👉 tu drag & drop les images dans le dossier
# 👉 tu tapes une seule commande
# 👉 tout se fait automatiquement
#
# Tu veux qu’on le transforme en outil permanent pour ton workflow ? 💻🔥


# ===============================================================================================

import os
from PIL import Image

# ===== CONFIG =====
input_folder = "images"
output_folder = "output"
logo_path = "logo.png"

quality = 80          # qualité WebP
logo_scale = 0.15     # taille du logo (15% largeur image)
margin = 30           # marge du logo

# ==================

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

logo = Image.open("/Users/ermanw/Bot_robot_scripts/ConvertirUNE_imageenWebP/images/logo.png").convert("RGBA")

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            input_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, base_name + ".webp")

            # Ouvre image principale
            img = Image.open(input_path).convert("RGBA")

            # ===== Redimension logo proportionnel =====
            logo_width = int(img.width * logo_scale)
            logo_ratio = logo_width / logo.width
            logo_height = int(logo.height * logo_ratio)

            resized_logo = logo.resize((logo_width, logo_height))

            # ===== Position bas droite =====
            position = (
                img.width - logo_width - margin,
                img.height - logo_height - margin
            )

            # ===== Fusion =====
            img.paste(resized_logo, position, resized_logo)

            # ===== Sauvegarde en WebP =====
            img.save(output_path, "WEBP", quality=quality, method=6)

            print(f"✔ {filename} converti avec logo")

        except Exception as e:
            print(f"❌ Erreur avec {filename} : {e}")

print("🚀 Toutes les images sont prêtes dans le dossier OUTPUT")



""" CE CODE AU DESSUS EST A OPTIMISER"""
