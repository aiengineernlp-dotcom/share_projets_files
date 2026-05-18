# score= range (0,1)
#
# try:
#     ask_score = float(input("Demander le score: "))
#     if not ask_score in score:
#         print(score)
#         print('BAD ANSWEER')
#     elif ask_score>=0.95:
#         print('A')
#     elif ask_score>=0.8:
#         print('B')
#     elif ask_score >= 0.7:
#         print('C')
#     elif 0.6<ask_score>= 0.6:
#         print('F')
# except Exception as e:
#     print('ValueError, Please enter a numeric input. ')

def computegrade(score):
    try:
        score = float(input('Entrer la valeur du score: '))
        if 0.0<=score<=1.0:
            if score>=0.9:
             return   ('F')
            elif score>=0.8:
                return('0')
            elif score>=0.7:
                return('R')
            else:
                return('Bad value')
        else:
            print('La valeur doit etre entre 0.0 et 1.0')
    except Exception as e:
        print("this is the error: ", e)

computegrade()




