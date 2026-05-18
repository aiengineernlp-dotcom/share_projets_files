# resize_images.py
# Dépendance: Pillow (pip install pillow)

from PIL import Image, ImageOps, ImageFile
import os

ImageFile.LOAD_TRUNCATED_IMAGES = True

# --- Configuration ---
input_paths = [
    "/mnt/data/breast-cancer-awareness-scaled.webp",
    "/mnt/data/ChatGPT Image Oct 8, 2025, 07_07_46 AM.png"
]
output_dir = "/mnt/data/resized"
target_size = (1920, 1080)
preserve_aspect = False   # True pour garder le ratio (avec letterbox), False pour forcer 1920x1080
letterbox_color = (255, 255, 255)  # couleur de fond si preserve_aspect=True

# --- Prépare dossier de sortie ---
os.makedirs(output_dir, exist_ok=True)

def resize_force(img, size):
    # Redimensionne en forçant la nouvelle taille (déformation possible)
    return img.resize(size, Image.Resampling.LANCZOS)

def resize_with_letterbox(img, size, bg_color=(255,255,255)):
    # Redimensionne en conservant le ratio, puis centre sur fond de la taille cible
    img_thumb = ImageOps.contain(img, size, Image.Resampling.LANCZOS)
    background = Image.new("RGBA" if img.mode == "RGBA" else "RGB", size, bg_color)
    offset = ((size[0] - img_thumb.width) // 2, (size[1] - img_thumb.height) // 2)
    background.paste(img_thumb, offset, img_thumb if img_thumb.mode == "RGBA" else None)
    return background

for path in input_paths:
    try:
        if not os.path.isfile(path):
            print(f"[SKIP] Fichier introuvable: {path}")
            continue

        img = Image.open(path)
        # Convertir en mode RGB si nécessaire pour éviter problèmes lors de la sauvegarde en JPEG
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        if preserve_aspect:
            out_img = resize_with_letterbox(img, target_size, bg_color=letterbox_color)
        else:
            out_img = resize_force(img, target_size)

        # Nom du fichier de sortie
        base = os.path.splitext(os.path.basename(path))[0]
        # Choisir extension selon mode (webp si sortie souhaitée webp)
        out_ext = ".webp" if path.lower().endswith(".webp") else os.path.splitext(path)[1]
        out_path = os.path.join(output_dir, f"{base}-{target_size[0]}x{target_size[1]}{out_ext}")

        # Sauvegarde avec qualité élevée si JPEG/WEBP
        save_kwargs = {}
        if out_ext.lower() in (".jpg", ".jpeg"):
            save_kwargs["quality"] = 95
            save_kwargs["subsampling"] = 0
        if out_ext.lower() == ".webp":
            save_kwargs["quality"] = 95

        out_img.save(out_path, **save_kwargs)
        print(f"[OK] {path} -> {out_path}")

    except Exception as e:
        print(f"[ERROR] {path} : {e}")










//Oui — le code que j’ai exécuté est un script complet pour redimensionner deux images déjà présentes dans le conteneur et sauvegarder les versions 1920×1080.
//Mais je peux te donner une version légèrement améliorée, plus robuste (gestion d’erreurs, création de dossier de sortie, usage recommandé de Resampling.LANCZOS, option pour préserver le ratio d’aspect en ajoutant des bordures ou en recadrant). Voici un script prêt à copier-coller et exécuter localement ou dans le même environnement :



Instructions rapides :

Installe Pillow si nécessaire : pip install pillow

Place le script dans le même environnement où sont les images (ou ajuste input_paths).

Lance : python resize_images.py

Les images redimensionnées seront dans /mnt/data/resized/ (ou le dossier que tu choisis).

Remarques :

Le script original que j’ai exécuté force la taille (déformation possible). Si tu veux préserver le ratio, mets preserve_aspect = True — le script ajoutera des bordures (letterbox) pour atteindre 1920×1080.

Si tu préfères recadrer (crop) au lieu de letterbox, je peux fournir cette variante aussi.

Dis-moi si tu veux que les fichiers de sortie soient tous en .jpg ou .webp — je l’adapte.
