liste_notes = []

while True:
    user_input = input('Enter un chiffre: ')
    if user_input =='done':
        print('DONE!')
        somme = sum(liste_notes)
        print("La somme est : ",somme)
        avarage = somme/len(liste_notes)
        print("La moyenne est : ",avarage)
        print(liste_notes)
        break
    try:
        if isinstance(int(user_input),int):
            liste_notes.append(int(user_input))
            print(liste_notes)
        else:
            print('Vous devez entrer un chiffrre')   # pour
    except ValueError as e:
        print('Error')



