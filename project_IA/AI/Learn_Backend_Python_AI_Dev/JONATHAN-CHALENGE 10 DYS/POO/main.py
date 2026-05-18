class Personne:
    def __init__(self,nom:str = '', age:int=0,):
        self.nom = nom
        self.age = age

    def __str__(self):
        return f"{self.nom} - {self.age}"

    def SePresenter(self):
        self.demanderNom()
        print('Salut je suis', str(self.nom),"j'ai " ,self.age," ans",'je suis...')
        if self.estMajeur():
            return True
        else:
            return False

    def demanderNom(self):
        nom = input("Demander nom: ")

    def estMajeur(self):

        try:
            if self.age<18:
                print(str(self.nom)+ " est mineur")
                return True
            elif self.age>=18:
                print(str(self.nom)+ " est majeur")
                return False
            elif self.age==0:
                print(str(self.nom))
        except Exception as e :
            print("this is the error: ", e)





personne1 = Personne('jean',23)
personne2 = Personne('omar',17)
personne3 = Personne()

personne1.SePresenter()
print('')
personne2.SePresenter()
print('')
personne3.SePresenter()

