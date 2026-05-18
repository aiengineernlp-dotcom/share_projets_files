import datetime

import cls
'''CREATION DES OBJECTS'''

# instanciation de Livre

livre1 = cls.Livre('livre_titre_1','livre_auteur_1','isbn_1')
livre2 = cls.Livre('livre_titre_2','livre_auteur_2','isbn_2',)
livre3 = cls.Livre('livre_titre_3','livre_auteur_3','isbn_3',False)
livre4 = cls.Livre('livre_titre_4','livre_auteur_4','isbn_4')
livre5 = cls.Livre('livre_titre_5','livre_auteur_5','isbn_5')

liste_livres = [livre2,livre3,livre4]

# instanciation de Document

document1 = cls.Document('Titre_document_1','Auteur_Document_1','Isbn_Doc_1')
document2 = cls.Document('Titre_document_2','Auteur_Document_2','Isbn_Doc_2')
document3 = cls.Document('Titre_document_3','Auteur_Document_3','Isbn_Doc_3')

# instanciation de Revue

revue1 = cls.Revue('Revue_Titre_1','Revue_Doocument_1','Isbn_Revue_1')
revue2 = cls.Revue('Revue_Titre_2','Revue_Doocument_2','Isbn_Revue_2')
revue3 = cls.Revue('Revue_Titre_3','Revue_Doocument_3','Isbn_Revue_3')

# instanciation de Membre
membre1 = cls.Membre('Nom_membre_1',1,liste_livres=[])
membre2 = cls.Membre('Nom_membre_2',2,liste_livres=[])
membre3 = cls.Membre('Nom_membre_3',3,liste_livres=[])
membre4 = cls.Membre('Nom_membre_4',4,liste_livres=[])
membre5 = cls.Membre('Nom_membre_5',5,liste_livres=[])
liste_membres = [membre1,membre2,membre3]

# instanciation de Emprunt
emprunter = cls.Emprunter(datetime.UTC)

# instanciation de Bibliotheques
bibliotheque = cls.Bibliotheque('Nom_bibliotheque',liste_livre=[],liste_membre=[])

"""Mes Classes ajoutee"""
# instanciation de Bibliothecaire
bibliothecaire1=cls.Bibliothecaire(1,'Nom_bibliothecaire1')
bibliothecaire2=cls.Bibliothecaire(2,'Nom_bibliothecaire2')
bibliothecaire3=cls.Bibliothecaire(3,'Nom_bibliothecaire3')




'''INTERACTION ENTRE DES OBJECTS AVEC LES METHODES'''

#ajout de un livre:
bibliotheque.ajouter_livre(livre1,bibliothecaire2)
#ajout de plus de un livre:
bibliotheque.ajouter_livre(liste_livres,bibliothecaire1)
print('\n')
#supprission de un livre.
# bibliotheque.supprimer_livre(livre1,bibliothecaire1)
#supprission de + un livre.
# bibliotheque.supprimer_livre(livre1,bibliothecaire1)
print('\n')
#enregister un membre
bibliotheque.enregister_membre(liste_membres,bibliothecaire3)
#enregister plus de un membre
# bibliotheque.enregister_membre()

print('\n')
# EMPRUNTER un livre.
bibliotheque.emprunter_livre()   # emprunt de un seul livre



print('\n')
# Retourner un livre.
bibliotheque.retourner_livre()
# bibliotheque.retourner_livre()



