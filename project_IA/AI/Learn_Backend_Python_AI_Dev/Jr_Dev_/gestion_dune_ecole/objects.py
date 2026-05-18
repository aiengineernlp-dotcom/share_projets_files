#instanciations
import classes

eleve_1 = classes.Eleve('Omar','C1')
eleve_2 = classes.Eleve('Ali','C2')
eleve_3 = classes.Eleve('Tony','C3')
liste_eleve = [eleve_1,eleve_2]
print('=================================================================================================================')
enseig_1 = classes.Enseignant('enseig_Paul','M1','C1')
enseig_2 = classes.Enseignant('enseig_Marie','M2','C2')
enseig_3 = classes.Enseignant('enseig_Tonton','M3','C3')
print('=================================================================================================================')

devoir_1 = classes.Devoir('Maths','About Maths devoir')
devoir_2 = classes.Devoir('Info','About Info devoir')
devoir_3 = classes.Devoir('Python','About Python devoir')
devoir_4 = classes.Devoir('Englais','About Englais devoir')

liste_devoir = [devoir_1,devoir_2,devoir_3]
print('==================Ajouter_eleve===============================================================================================\n')
enseig_1.ajouter_eleve(liste_eleve)


print('==================donner_devoir===============================================================================================\n')
enseig_1.donner_devoir(liste_devoir)

print('==================recevoir_devoir===============================================================================================\n')
eleve_1.recevoir_devoir()

print('==================soumettre_devoir===============================================================================================\n')
eleve_1.soumettre_devoir()


print('==================afficher_devoirs===============================================================================================\n')
eleve_1.afficher_devoirs()










print('=================================================================================================================\n')
