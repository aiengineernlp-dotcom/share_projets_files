serie_list_1 = []
while True:
    user_input_1 = input('entrer un chiffre: ')
    if user_input_1 == 'done_1':
        print("Liste 1: ", serie_list_1)
        MAX= max(serie_list_1)
        MIN= min(serie_list_1)
        print('MAX: ',MAX)
        print('MIN: ', MIN)
        break

    try:
        if isinstance(int(user_input_1),int):
            serie_list_1.append(int(user_input_1))
            print("Liste a jour: ",serie_list_1)
    except ValueError as e:
        print('Vous devez entrer un chifrre')
