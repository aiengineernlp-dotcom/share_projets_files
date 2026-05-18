print("REMUNeRATION")

def computepay(temps_travail_journalier, salaire_par_heure):
    try:
        # temps_travail_journalier = int(input("Entrer le volume horaire de travail:")) # 43
        # salaire_par_heure = float(input("entrer le montant a recevoir/payer par heure:")) # 12
        if temps_travail_journalier > 40:
            heure_supplementaire = temps_travail_journalier-40  # peut etre 3
            salaire_heure_supp = heure_supplementaire * (salaire_par_heure+0.5)
            salaire = (temps_travail_journalier * salaire_par_heure)+salaire_heure_supp
            print("Le salaire est de :", salaire)
        else :
            salaire = temps_travail_journalier * salaire_par_heure
        return salaire
    except Exception as e:
        print("Error, Please enter a numeric input.",e)
        return None


salaire = computepay(4,3)

print(salaire)

'''
si le travailleur fait plus de 40 heures alors la diffrence sera utiliser pourcalculer son salaire supp 

'''


'''
donc c'est le salaire plus (taux+50%)


ChatGPT said:
Pas tout à fait — clarifions cela étape par étape. Ce n’est pas :

Salaire + (taux + 50%) ❌

C’est plutôt :

Salaire = salaire normal + (heures majorées × [taux horaire + 50%]) ✅

🔹 Exemple clair :
Tu gagnes 2 000 € par mois pour 160 heures → ton taux horaire est :

2000 € ÷ 160 h = 12,50 €/h

Tu fais 10 heures supplémentaires à taux majoré de 50 %.

Alors :

Ton taux majoré est :

12,50 € + (12,50 € × 0.5) = 18,75 €

Tes heures sup te rapportent :

10 h × 18,75 € = 187,50 €

Ton salaire total ce mois-là sera :

2 000 € + 187,50 € = 2 187,50 €

🔸 Résumé :
On ne rajoute pas 50 % à tout le salaire, mais seulement à la part du salaire liée aux heures ou situations concernées (heures sup, nuit, etc.).
'''




