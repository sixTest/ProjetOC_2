# Script contenue

Un script permettant de récupérer les informations ci-dessous des livres du site [http://books.toscrape.com](http://books.toscrape.com/), de les formater au format csv et de télécharger les images associées aux livres.

* Url de la page produit du livre
* UPC
* Titre du livre
* Prix avec taxe
* Prix hors taxe
* Nombre de livres en stock
* La description du livre
* La catéogie du livre
* Nombre d'avis
* Url de l'image associée au livre

## Lancement du script

* Ouvrez un invite de commande
* Placez vous dans le dossier contenant le fichier dev.py
* Tapez : python -m venv env
* Tapez : env\Scripts\activate.bat
* Tapez : pip install -r requirements.txt
* Tapez : python dev.py < path pour les fichiers csv > < path pour les images >
