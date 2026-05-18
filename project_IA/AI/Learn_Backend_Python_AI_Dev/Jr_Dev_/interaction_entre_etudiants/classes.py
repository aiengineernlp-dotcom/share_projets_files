class Student:
    def __init__(self,name):
        self.name = name
        self.notes = []
        self.moy = 0
        self.__bonus = 5  # ne peut etre mofifier ou lu depuis lexterieur de la classe doit etre utiliser avec les getter et les setters

    def __str__(self):
        return f" ETUDIANT INFOS:\n-{self.name}\n-{self.notes}"

    def add_notes(self,new_note,):
        if isinstance(new_note,list):
            self.notes.extend(new_note)
            print(f"Nombre de notes ajoutee pour {self.name}: {len(self.notes)} Notes")
        else:
            self.notes.append(new_note)
            print(f"Nombre Total des notes pour {self.name}: {len(self.notes)} Notes")

    def calcul_moy(self):
        somme = 0
        if len(self.notes) == 0:
            self.moy = 0
        else:
            for note in self.notes:
                somme += note
            self.moy = somme / len(self.notes)
        print(self.moy)


    def display_note(self,student_x,student_y):
        print(f'{self.name} Tes notes sont: {self.notes} et ta moyenne est', self.moy)
        if student_x.moy>student_y.moy:
            print(f'La note de {student_x.name} est plus grand que {student_y.name}')
        else:
            print(f'La note de {student_y.name} est plus petit que {student_x.name}')





# print('La moyenne est : ',moy)

