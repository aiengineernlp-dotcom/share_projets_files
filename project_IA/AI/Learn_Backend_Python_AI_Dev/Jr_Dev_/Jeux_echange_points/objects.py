import classes
# Creation des objects (instantiation)

player1 = classes.Player("Omar",40)
player2 = classes.Player("Ali",10)

"""INTERACTIONS"""
print('AFFICHAGE DES POINTS AVANT LE JEUX')
player1.display_life()
player2.display_life()
print('=================================================================================================================\n')
print('DONNATION DES POINTS')
player1.donner_points(player2,100)
print('=================================================================================================================\n')
print('AFFICHAGE DES POINTS APRES LE JEUX')
player1.display_life()
player2.display_life()
print('=================================================================================================================\n')
