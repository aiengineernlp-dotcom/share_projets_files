import os
from datetime import datetime

class Book:
    def __init__(self, titre,auteur,id,disponible=True):
        self.titre = titre
        self.auteur = auteur
        self.id = id
        self.disponible = disponible # disponble

    def __str__(self):
        return f"Titre: {self.titre} - Auteur: {self.auteur} - ID: {self.id} - disponible: {self.disponible}"

class Library:

    def __init__(self,list_book=None):

        self.list_book = [] if list_book is None else list_book

    def __str__(self):
        return f" Liste des Livres: {self.list_book}"

    def add_books(self,new_book):

        if isinstance(new_book, list):
            self.list_book.extend(new_book)
            print(f"{len(self.list_book)} livres ajoutes avec success.")
        else:
            self.list_book.append(new_book)
            print(f"Nombre total des livres : {len(self.list_book)}")

    def gere_emp(self):

        '''

        Objectif : signaler si un livre est emprunter

        Conditions :
        - si le livre n'est pas dans la librairie alors c'est pas disponible

        Effets :
        -on va voir directemet afficher "Non disponible sur l'ecran"
        -

        '''




    def gere_reto(self):
        pass

    def display_books_status(self):
        print("Listes des livres disponibles dans la liste list_book ")
        for livre in self.list_book:
            print(f"Status du livre:,{livre.titre} : {livre.disponible}")



class User :
    def __init__(self,id,name,email_user,mot_de_passe,history_pret=None):
        self.id = id
        self.name = name
        self.email_user = email_user
        self.mot_de_passe = mot_de_passe
        self.history_pret = [] if history_pret is None else history_pret

    def __str__(self):
        return f" ID: {self.id} - Name: {self.name} - Email: {self.email_user} - Mot de passe {self.mot_de_passe}"

    def emprunter_livr(self,new_emprun,):

        '''
        Objectif : permettre à l'utilisateur d'emprunter un livre ou plusieurs livres

        Conditions :
        - Le livre doit être disponible.

        Effets :
        - Le livre est ajouté à la liste des emprunts.
        - Le livre devient indisponible.
        '''

        if new_emprun.disponible:
            if isinstance(new_emprun, list):
                self.history_pret.extend(new_emprun)
                print(f"{self.name},Vous avez emprunter {len(self.history_pret)} nouveaux livres")

            else:
                self.history_pret.append(new_emprun)
                print(f"{self.name}, Votre Nombre total de livres empruntes: {len(self.history_pret)} livre(s)")

            new_emprun.disponible=False   # le livre devient non dispo donc change de statut
        else:
            print(f'livre {new_emprun.titre} est non disponible. a la date de  {datetime.day}')

    def rendre_livr(self,library):

        '''

        Objectif :  permettre l'utilisateur de remettre le livre a la bibliotheque

        Conditions : le livre doit avoir ete emprunter c'est a dire doit etre  a False dans la disponibilite
        -

        Effets :
        - le livre est rajouter a la bibliotheque
        - lhistorique de l'utilisateur redevien sans ce livre la

        '''

        for livre in self.history_pret:
            if not livre.disponible:  #je cherche les livres qui ont un statut False
                if isinstance(livre, list):
                    library.list_book.extend(livre) # rendre plusieurs livres
                else:
                    library.list_book.append(livre) # rendre un seul livre

                livre.disponible = True   # livre est a nouveau disponible

                print(f'vous avez rendu le livre: {livre.titre}. a la date de : {datetime.day}')
            else:
                print('........')

