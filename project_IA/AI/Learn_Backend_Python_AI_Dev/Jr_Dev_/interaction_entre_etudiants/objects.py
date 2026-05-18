import classes
#instanciation
student_1 = classes.Student('OMAR')
student_2 = classes.Student('ALI')
print('=================================================================================================================\n')
"""INTERACTIONS"""

print('AJOUTER NOTES')
list_notes_E1 = [10,12,13,14,15]
list_notes_E2 = [100,2,12,3,7,3,9]
student_1.add_notes(12,)
student_1.add_notes(list_notes_E1,)
student_2.add_notes(list_notes_E2,)
print('=================================================================================================================\n')

print('Calculer moyenns:')
print(F"MOYENNE DE {student_1.name}")
student_1.calcul_moy()
print('=================================================================================================================\n')
print(F"MOYENNE DE {student_2.name}")
student_2.calcul_moy()
print('===================================================================================================================')
print('Afficher moyenns:')
student_1.display_note(student_2,student_1)
student_2.display_note(student_2,student_1)



print('AFFICHAGE DES POINTS AVANT LE JEUX')