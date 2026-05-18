class Enseignant:
    def __init__(self, nom,matiere,classe_assignee, liste_eleve=None,liste_devoirs=None,liste_devoirs_donnees=None):
        self.nom = nom
        self.matiere  = matiere
        self.classe_assignee = classe_assignee
        self.liste_eleve = [] if liste_eleve is None else liste_eleve
        self.liste_devoirs = [] if liste_devoirs is None else liste_devoirs
        self.liste_devoirs_donnees = [] if liste_devoirs_donnees is None else liste_devoirs_donnees

    def __str__(self):
        return f"Nom: {self.nom}  - Matiere: {self.matiere} - Classe Assignee: {self.classe_assignee}"

    def ajouter_eleve(self,new_eleve):
        if isinstance(new_eleve, list):
            self.liste_eleve.extend(new_eleve)
            print(f'{self.nom} Vous avez',len(self.liste_eleve),'eleves ajouter avec success.')
        else:
            self.liste_eleve.append(new_eleve)
            print('Nombre totals de vos eleves: ', len(self.liste_eleve))

    def donner_devoir(self,new_devoir):
        if not self.liste_eleve:
            print('Votre liste des eleves est vide.')
        else:
            if isinstance(new_devoir,list):
                self.liste_devoirs.extend(new_devoir)
                print(self.nom,'Vous avez donner',len(self.liste_devoirs), 'nouveaux devoir a',self.liste_eleve)
                self.liste_devoirs_donnees.extend(new_devoir)
                if self.liste_devoirs!=0:#
                    for eleve in self.liste_eleve:
                        if isinstance(new_devoir, list):
                            eleve.devoirs_recus.extend(new_devoir)
                        else:
                            eleve.devoirs_recus.append(new_devoir)
            else:
                self.liste_devoirs.append(new_devoir)
                print(self.nom, 'Vos devoirs totaux donner: ', len(self.liste_devoirs), 'devoir a',self.liste_eleve)
                self.liste_devoirs_donnees.append(new_devoir)




class Devoir:
    def __init__(self, nom,description):
        self.nom = nom
        self.description = description

    def __str__(self):
        return f'{self.nom} - {self.description}'




class Eleve:
    def __init__(self, nom, classe,devoirs_recus=None):
        self.nom = nom
        self.classe = classe
        self.devoirs_recus = [] if devoirs_recus is None else devoirs_recus



    def __str__(self):
        return f" Nom: {self.nom} - Classe: {self.classe} - Devoirs: {self.devoirs_recus}"

    def recevoir_devoir(self):
        print(self.devoirs_recus)
        for devoir in self.devoirs_recus:
            if devoir:
                print("Devoir recus:\nNom:",devoir.nom,"Description:\n",devoir.description)

    def soumettre_devoir(self):
        if self.recevoir_devoir():
            print()

    def afficher_devoirs(self):
        pass
        # for devoir in self.devoirs_recus:
        #     print("Devoir recus:\nNom:", devoir.nom, "Description:\n", devoir.description)
        # # if len(self.devoirs)==0:
        # #     print("Aucun devoir recu")

