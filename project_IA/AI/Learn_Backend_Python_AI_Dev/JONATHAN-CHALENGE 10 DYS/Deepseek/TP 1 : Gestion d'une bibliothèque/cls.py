'''TP 1 : Gestion d'une bibliothèque 📚
Objectif :
Créer un système de gestion de bibliothèque en utilisant les concepts de POO.

Contenu :
Classes à créer :

Livre : Attributs (titre, auteur, ISBN, statut (disponible/emprunté)).

Membre : Attributs (nom, ID, liste des livres empruntés).

Bibliotheque : Attributs (liste des livres, liste des membres). Méthodes (ajouter un livre, supprimer un livre, enregistrer un membre, emprunter un livre, retourner un livre).

Concepts à appliquer :

Héritage : Créez une classe Document parente pour Livre et Revue (optionnel).

Association : Un Membre peut emprunter plusieurs Livres.

Agrégation : La Bibliotheque contient une liste de Livres et de Membres.

Composition : Un Livre ne peut pas exister sans une Bibliotheque.

Délégation : La méthode emprunter_livre de Bibliotheque délègue la mise à jour du statut du livre à la classe Livre.

Fonctionnalités :

Ajouter/supprimer un livre.

Enregistrer un membre.

Emprunter/retourner un livre.

Afficher la liste des livres disponibles.

Bonus :

Ajouter une classe Emprunt pour gérer l'historique des emprunts.

Utiliser des exceptions pour gérer les cas où un livre est déjà emprunté.'''

# creation des classes et methods

class Livre:
    def __init__(self, titre,auteur,isbn,statut = True):
        self.titre = titre
        self.auteur = auteur
        self.isbn = isbn
        self.statut = statut

    def __str__(self):
        return f"{self.titre}"


class Document(Livre):
   def __init__(self, titre, auteur, isbn):
       super().__init__(titre, auteur, isbn)

   def __str__(self):
       return f"{self.titre}"

class Revue(Livre):
    def __init__(self, titre, auteur, isbn):
        super().__init__(titre, auteur, isbn)

    def __str__(self):
        return f"{self.titre}"


class Bibliotheque:
    def __init__(self,nom, liste_livre=None,liste_membre=None):
        '''je verifie au moment de la creation de la liste si ya pas liste des livres. alors j'en cree sinon je la laisse vide'''
        self.nom = nom
        if liste_livre is None:
            self.liste_livres = []
        else:
            self.liste_livres =liste_livre

        '''je verifie au moment de la creation de la liste si ya pas liste des membres. alors j'en cree sinon je la laisse vide'''
        if liste_membre is None:
            self.liste_membre = []
        else:
            self.liste_membre =liste_membre

    def ajouter_livre(self,new_livre,bibliothecaire):
        if isinstance(new_livre,list):
            try:
                self.liste_livres.extend(new_livre)
                print(len(self.liste_livres), f"ajoutes par {bibliothecaire.nom}")
                for l in self.liste_livres:
                    if l.statut:
                        print(l.titre,'Disponible:',l.statut)
                    else:
                        print(l.titre,'InDisponible:',l.statut)
                    print(f'Total du nombre des livres ajouter : {len(self.liste_livres)}.')
                return new_livre   # ici je retourne la liste des livres
            except Exception as e :
                print('This is the error: ', e)
        else:
            try:
                self.liste_livres.append(new_livre)
                print(len(self.liste_livres), f"ajoutes par {bibliothecaire.nom}")

                for l in self.liste_livres:
                    if l.statut:
                        print(l.titre, 'Disponible:', l.statut)
                    else:
                        print(l.titre, 'InDisponible:', l.statut)

                    return l.statut # ici je retourne statut du livre
                return new_livre #ici je retourne un seul livre
            except Exception as e :
                print('This is thr error: ',e)



    def enregister_membre(self,new_membre,bibliotecaire):
        if isinstance(new_membre,list):
            try:
                self.liste_membre.extend(new_membre)
                # new_membre.saved()
                print("Nombre total des membres : ",len(self.liste_membre),'membres')
                print("deburging......:",self.liste_membre)
                for m in self.liste_membre:
                    print("Enregistrement du membre .... ", )
                    # m.save()
                    return m  # ici c'est l'etat du membre qui est retourner c'est a dire l'etat enregister
                return new_membre # retourne la liste des membres
            except Exception as e :
                print("This is the error:", e )
        else:
            try:
                self.liste_membre.append(new_membre)
                # new_membre.save()
                print(f"nouveau membre ajouter:",len(self.liste_membre),f"membre\npar {bibliotecaire.nom}", )
                for m in self.liste_membre:
                    print("Enregistrement du membre .... ", )
                    # m.save()
                    return m # ici c'est l'etat du membre qui est retourner c'est a dire l'etat enregister
                return new_membre  # retourne  un seul  membre
            except Exception as e:
                print("This is the error:", e)

    def supprimer_livre(self, livre, bibliothecaire):
        del_livre = input(print(bibliothecaire.nom, 'Entrer le titre du livre a supprimer: '))
        if livre.statut and del_livre == livre.titre:
            self.liste_livres.remove(livre)
            livre.statut=False
            print(livre, 'Supprimer avec succes')
            print(self.liste_livres)
        else:
            print('livre non trouveer')

#

    def retourner_livre(self,):
        ret_livre_titre= input('Enter le titre du livre a retourner: ')

        for l in self.liste_livres:
            if l.emprunter_livre():
                print(l.titre,'trouver!!')
                return True
            elif ret_livre_titre==l.titre and l.statut==False:
                print('Non trouver!')
                return False
            else:
                print('Acune correspondance')
                return True




    def emprunter_livre(self):
        empr = input('Entrer le nom du livre a emprunter: ')
        try:
            for l in self.liste_livres: # je parcours la liste entiere
                print("dddd---1----",self.liste_livres)
                if not empr==l.titre:  # ici je did que si le livre n'est pas disponible dans toute la bibliotheque
                    print("dddd---2----",)
                    print('non-disponible')
                    return False

                elif  empr == l.titre and l.statut:
                    print('disponible')
                    l.statut = False
                    print(l.titre,"n'est plus  disponible donc son etat est false:----->",l.statut)
                    return True
                else:
                    print('Aucune donnee trouvee')
        except Exception as e:
            print("This is the error: ", e)






    def afficher_livre(self):
        pass


class Emprunter:
    def __init__(self,date):
        self.date = date
    def __str__(self):
        pass
        

class Membre:
    def __init__(self,nom,id,liste_livres = None):
        self.nom = nom
        self.id = id
        if liste_livres is None:
            self.liste_livres = []
        else:
            self.liste_livres = liste_livres

    def __str__(self):
        return f"{self.nom}: {self.id}"

"""Mes Classes ajoutee"""
class Bibliothecaire:
    def __init__(self,id,nom,):
        self.id = id
        self.nom = nom
    def __str__(self):
        return f"{self.nom}:{self.id}"








