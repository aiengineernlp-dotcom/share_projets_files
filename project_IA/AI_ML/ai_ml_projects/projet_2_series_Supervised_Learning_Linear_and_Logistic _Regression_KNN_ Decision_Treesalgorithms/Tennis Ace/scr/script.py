# import codecademylib3_seaborn
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from textblob.en.inflect import plural_rules

# load and investigate the data here:
data_tennis = pd.read_csv("../data/tennis_stats.csv")
df = pd.DataFrame(data_tennis)
# afficher les infos generales

# print("Les infos generales de tennis_stats \n",df.info())
# print("\n\n\cn")
# # afficher les collones du dataframe
# print("Les collonnes du DataFrame: \n: ",df.columns)
# print("\n\n\n")
# #Afficher les types de variable du DataFrame
# print("Les types variables du DataFrame:\n",df.dtypes) # est ce que on peut dire que ce sont les types des variables des series??
# #print pour explorer les etiquettes/valeurs uniques/variables categorielles
# print(df['Player'].value_counts().head(30))



# print("""Service Game Columns (Offensive)""")

# """CAS DE LA VARIABLE DEPENDANTE: Wins"""

# # perform exploratory analysis here:
# print("# plotting of feature: ", df['Aces'].name,"on",df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['Aces'], df['Wins'],color = 'orange',label = 'Donnees reelles', alpha = 0.4)
# plt.xlabel("Variable Ind: (Aces)")
# plt.ylabel("Variable Dep: (Wins)")
# plt.title("Relation entre Aces et Wins")
# plt.grid(True)
# plt.legend()
# plt.show()
# #
# #
# print("ploting of features: ", df['DoubleFaults'].name, "on", df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['DoubleFaults'],df['Wins'],color = 'orange',label= "donnees reelles", alpha=0.4)
# plt.xlabel("Variable Ind: (DoubleFaults)")
# plt.ylabel("Variable Dep: (Wins)")
# plt.title("relation entre DoubleFaults, 'et',Wins")
# plt.grid(True)
# plt.legend()
# plt.show()
# #
# #
# print("ploting of feature: ",df['FirstServe'].name, "on",df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['FirstServe'],df['Wins'],color= "orange",label ="valeur reelles",alpha= 0.4)
# plt.xlabel("Variable Ind: (FirstServe)")
# plt.ylabel("Variable DePendante:(Wins)")
# plt.title("Relation entre FirstServe et Wins")
# plt.legend()
# plt.grid(True)
# plt.show()
# # #
# # #
# print(("ploting of features : ",df['FirstServePointsWon'].name, "on",df['Wins'].name))
# plt.figure(figsize=(8,5))
# plt.scatter(df['FirstServePointsWon'],df['Wins'],color='orange',label='valeurs reelles',alpha=0.4)
# plt.title("Relation entre FirstServePointsWon et Wins")
# plt.xlabel("Variable inde: (FirstServePointsWon)")
# plt.ylabel("Variable depend: (Wins)")
# plt.legend()
# plt.grid(True)
# plt.show()
# print("\n\n")
# # #
# # #
# # #
# print('ploting of feature :', df['SecondServePointsWon'].name, "on", df['Wins'].name)
# plt.figure(figsize = (8,5))
# plt.scatter(df['SecondServePointsWon'],df['Wins'],label = 'Valeur Reells', alpha =0.4,color = 'orange')
# plt.xlabel('Variable ind (SecondServePointsWon)')
# plt.ylabel("Variable dependante (Wins)")
# plt.title('Relation entre SecondServePointsWon et Wins')
# plt.legend()
# plt.grid(True)
# plt.show()
# #
# print('ploting of feature: ', df['BreakPointsFaced'].name , df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['BreakPointsFaced'],df['Wins'],color='orange',label='valeur reelles', alpha= 0.4)
# plt.title("Relation entre BreakPointsFaced et  Wins")
# plt.xlabel("Variable independante : (BreakPointsFaced)")
# plt.ylabel("varible dependante: (Wins)")
# plt.legend()
# plt.grid(True)
# plt.show()


# print('ploting of feature: ', df['BreakPointsSaved'].name, "on", df['Wins'])
# plt.figure(figsize=(8,5))
# plt.scatter(df['BreakPointsSaved'], df["Wins"], color = 'orange', alpha=0.4,label='Valeurs reelles')
# plt.xlabel('Variable independate: BreakPointsSaved')
# plt.ylabel('Vriable dependante: Wins ')
# plt.grid(True)
# plt.legend()
# plt.show()


# print('ploting of feature:',df['ServiceGamesPlayed'].name , 'on',df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['ServiceGamesPlayed'],df['Wins'],color='orange',label='Valeurs reelles',alpha = 0.4)
# plt.xlabel('valeur independante : ServiceGamesPlayed ')
# plt.ylabel('valeur dependante:  Wins')
# plt.title("Relation entre ServiceGamesPlayed et Wins")
# plt.grid(True)
# plt.legend()
# plt.show()

# print('ploting of feature:',df['ServiceGamesWon'].name , 'on',df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['ServiceGamesWon'],df['Wins'],color='orange',label='Valeurs reelles',alpha = 0.4)
# plt.xlabel('valeur independante : ServiceGamesWon ')
# plt.ylabel('valeur dependante:  Wins')
# plt.title("Relation entre ServiceGamesWon et Wins")
# plt.grid(True)
# plt.legend()
# plt.show()


# print("ploting of fetures :",df['ServiceGamesWon'].name , "on", df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['ServiceGamesWon'], df['Wins'],color = 'orange',alpha = 0.4, label = "valeurs reelles")
# plt.xlabel("Variable indep:ServiceGamesWon")
# plt.ylabel("Variable dependante: Wins ")
# plt.title('Relation entre ServiceGamesWon et Wins')
# plt.legend()
# plt.grid(True)
# plt.show()

# #
# print("ploting of feature:", df['TotalServicePointsWon'].name, 'on',df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['TotalServicePointsWon'],df['Wins'], color= 'orange',label = 'Valeurs reelles', alpha = 0.4)
# plt.xlabel("Variable  ind: TotalServicePointsWon")
# plt.ylabel("Variable dep: Wins")
# plt.title("Relation entre TotalServicePointsWon er Wins")
# plt.legend()
# plt.grid(True)
# plt.show()

# print('ploting of feature ',df['SecondServeReturnPointsWon'].name ,'on',df['Wins'])
# plt.scatter(df['SecondServeReturnPointsWon'],df['Wins'],color = 'orange',label = 'Valeur reelle',alpha = 0.4)
# plt.xlabel("Variable indep: ")
# plt.ylabel("Variable dependante:")
# plt.title('Relation entre SecondServeReturnPointsWon et Wins')
# plt.grid(True)
# plt.legend()
# plt.show()


# print("ploting of feature:  ",df['BreakPointsOpportunities'].name, 'on' ,df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['BreakPointsOpportunities'],df['Wins'],color = 'orange',label = 'Valeurs reelles',alpha=0.4)
# plt.xlabel('Variable independante: BreakPointsOpportunities ')
# plt.ylabel('Variable dependante: Wins')
# plt.title('Relation entre BreakPointsOpportunities et Wins')
# plt.legend()
# plt.grid(True)
# plt.show()

# print('ploting of feature ',df['BreakPointsConverted'].name, 'on', df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['BreakPointsConverted'],df['Wins'],color = 'orange',label = 'Valeur reellees')
# plt.xlabel("Variable independante: BreakPointsConverted")
# plt.ylabel("Variable dependante: `WIns'")
# plt.legend()
# plt.grid(True)
# plt.show()


# print("ploting of feature,",df['ReturnGamesPlayed'].name, 'on', df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['ReturnGamesPlayed'],df['Wins'],color = 'orange',label='Valeur reelle',alpha = 0.4)
# plt.xlabel('Variable indep: ReturnGamesPlayed')
# plt.ylabel('Variable dependante: Wins')
# plt.legend()
# plt.grid(True)
# plt.show()

# print("Ploting of feature,",df['ReturnGamesWon'].name, 'on',df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['ReturnGamesWon'],df['Wins'],color = 'orange',alpha=0.4,label = 'Valeurs reelles')
# plt.title("relation entre ReturnGamesWon et Wins")
# plt.xlabel("Variable independante: ReturnGamesWon ")
# plt.ylabel("variable dependante: Wins ")
# plt.legend()
# plt.grid(True)
# plt.show()


# print("Ploting of features,", df['ReturnPointsWon'].name, 'on', df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['ReturnPointsWon'],df['Wins'],color = 'orange',label = 'Variable reellee',alpha = 0.5)
# plt.title('Relation entre ReturnPointsWon et Wins')
# plt.xlabel('variable independante: ReturnPointsWon ')
# plt.ylabel('variable dependante:  Wins')
# plt.legend()
# plt.grid(True)
# plt.show()



# print('ploting of ',df['TotalPointsWon'].name, 'on',df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['TotalPointsWon'],df['Wins'],color = 'orange', alpha = 0.4, label= "Valeure reelles")
# plt.title('Relatiion entre  TotalPointsWon et  Wins')
# plt.xlabel("Variable independante  TotalPointsWon ")
# plt.ylabel("Variable dependante: Wins ")
# plt.legend()
# plt.grid(True)
# plt.show()



















print("""Return Game Columns (Defensive)""")

# print('ploting of the feature:', df['FirstServeReturnPointsWon'].name, 'on', df['Wins'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['FirstServeReturnPointsWon'],df['Wins'],color = 'orange',alpha = 0.4)
# plt.xlabel('variable independante :FirstServeReturnPointsWon ')
# plt.ylabel('variable dependante : Wins')
# plt.title('Relation entre  FirstServeReturnPointsWon et Wins')
# plt.legend()
# plt.grid(True)
# plt.show()
#
















"""CAS DE LA VARIABLE DEPENDANTE  Losses """

# print("Ploting of features ",df['Aces'].name , "on", df['Losses'].name)
# plt.figure(figsize=(8,5))
# plt.scatter(df['Aces'],df['Losses'],color = 'orange', label = 'valeurs reellees', alpha= 0.4)
# plt.xlabel('Variable inde: (Aces)')
# plt.ylabel('Variable dependante: (Losses)')
# plt.title('Relation entre Aces and Losses')
# plt.legend()
# plt.grid(True)
# plt.show()

























## perform single feature linear regressions here:

# print("\n\n\n Les collonnes : ",df.columns)
# print("\n\n\n Les collonnes : ",df.dtypes)


'''======================================================================'''

# # # Feature: FirstServePointsWon

# X= df[['FirstServePointsWon']]
# Y= df[['Wins']]

# # split data into training set and test set
# X_train, X_test,Y_train,Y_test = train_test_split(
#   X,
#   Y,
#   train_size = 0.8,
#   test_size = 0.2
#   #random_state = 6
# )


# #creation du model
# slr_1 = LinearRegression()

# #entrainement du model

# slr_1.fit(X_train,Y_train)

# #Prediction sur les donnees de test
# y_predict = slr_1.predict(X_test)

# print("La prediction de .....vs .... est  : ",y_predict)


# # la performance du modèle: Affichacher le graphique de comparaison entre valeurs reelles (Y_test) et valeurs predites(y_predicted)
# plt.figure(figsize=(8,5))
# plt.scatter(Y_test,y_predict,alpha = 0.4,label = 'valeur reelle',color = 'orange' )
# plt.xlabel('Valeur reelle de Wins par rapport a  : FirstServePointsWon')
# plt.ylabel('Valeur predite de Wins de Wins par rapport a  : FirstServePointsWon')
# plt.legend()
# plt.grid(True)
# plt.show()


'''======================================================================'''

#Feature: Aces

# # variable independante: X = Aces
# # Variable dependante: Y = Wins
# X = df [['Aces']]
# Y = df[['Wins']]

# #Split data into training set and test set

# X_train, X_test, Y_train, Y_test = train_test_split(
#   X,
#   Y,
#   train_size = 0.8,
#   test_size = 0.2
# )

# #Creation du model
# slr_2 = LinearRegression()

# #Entrainement du model
# slr_2.fit(X_train, Y_train) # entrainement du modele
# #print les coefficients
# print("le coefficient/la pente (m) de la variable independante Aces",slr_2.coef_)
# print("l'ordonee a l'origine (b)",slr_2.intercept_)

# #prediction sur les donnees de test
# y_predict_2 = slr_2.predict(X_test)
# print("La prediction de .....vs .... est  : ",y_predict_2)

# # la performance du modèle: Affichacher le graphique de comparaison entre valeurs reelles (Y_test) et valeurs predites(y_predicted)
# print('Visualisation des predictions de ',df['Aces'].name ,"sur",df['Wins'].name)
# plt.scatter(Y_test, y_predict_2, alpha=0.4, label='Prédictions')
# plt.xlabel('Valeurs réelles (Wins) par rapport a Aces')
# plt.ylabel('Valeurs prédites (Wins) par rapport a Aces')
# plt.legend()
# plt.grid(True)
# plt.show()

'''======================================================================'''
#Features  DoubleFaults
# # Variables: X = DoubleFaults; Y = Wins

# X= df[['DoubleFaults']]
# Y= df[['Wins']]

# #plot data into training set and test set

# X_train, X_test, Y_train, Y_test = train_test_split(
#   X,
#   Y,
#   train_size = 0.8,
#   test_size = 0.2
# )

# #creation du model
# slr_3 = LinearRegression()
# # entrainement du model
# slr_3.fit(X_train,Y_train)
# # afficher les coefficients
# slr_3.coef_
# slr_3.intercept_

# #prediction

# y_predicted = slr_3.predict(X_test)

# # Afficher le graphique
# # la relation brute :   # Afficher la relation brute entre DoubleFaults et Wins
# print("Visualisation des predictions de ",df['DoubleFaults'].name ,"`sur",df['Wins'])
# plt.scatter(df['DoubleFaults'],df['Wins'],alpha=0.4,label = 'Valeurs reelle')
# plt.xlabel('Variable independante de Wins par rapport a DoubleFaults')
# plt.ylabel('Valeurs dependante de Wins par rapport a  DoubleFaults')
# plt.grid(True)
# plt.legend()
# plt.show()


# # la performance du modèle: Affichacher le graphique de comparaison entre valeurs reelles (Y_test) et valeurs predites(y_predicted)
# plt.scatter(Y_test,y_predicted,alpha = 0.4,label='predictions')
# plt.xlabel('Valeurs reelles(Wins) par rapport a  DoubleFaults')
# plt.ylabel('Valeurs predites (Wins) par rapport a  DoubleFaults')
# plt.legend()
# plt.grid(True)
# plt.show()

'''======================================================================'''
#Feature: FirstServe:
#
# X= df[['FirstServe']]
# Y= df[['Wins']]
#
# #splot data into training set and test set
# X_train, X_test, Y_train, Y_test = train_test_split(
#   X,
#   Y,
#   train_size = 0.8,
#   test_size = 0.2
# )
#
# #creation du model de regression lineaire
# slr_4 = LinearRegression()
#
# #entrainement du model
# slr_4.fit(X_train,Y_train)
# #print les coefficients sont
# m = slr_4.coef_
# b= slr_4.intercept_
# #prediction
# y_predicted = slr_4.predict(X_test)
#
# print('La prediction est ',y_predicted)
#
# # Afficher la comparaison entre valeurs réelles (Y_test) et valeurs prédites (y_predicted)
# plt.scatter(Y_test,y_predicted, color = 'orange',alpha = 0.4, label = "valeurs reelles", )
# plt.xlabel('Valeur reelle de wins par rappor a FirstServe')
# plt.ylabel('Valeur reelle de Wins par rapport a FirstServe')
# plt.grid(True)
# plt.legend()
# plt.show()


'''
Exactement je vois du bas vers le haut en abscice  0 jusqua ordonne 10 , les points formants une droite et de ces points il ya d'autres points qui emergents horizontalement comme si on s'etait placer sur la droite et verser de les points vers lavant

AI Assistant
Ce que tu décris est typique d’un scatter plot de valeurs réelles (Y_test) contre valeurs prédites (y_predicted) pour une régression linéaire :

Les points devraient idéalement être alignés sur la diagonale (la droite y = x), ce qui voudrait dire que la prédiction est parfaite.
En réalité, beaucoup de points sont proches de cette diagonale, mais certains s’en éloignent : ils “s’écartent” horizontalement ou verticalement, montrant l’erreur de prédiction.
Plus les points sont proches de la diagonale, plus le modèle est précis.
Ce que tu observes

Les points “qui émergent horizontalement” montrent que, pour une même valeur réelle, le modèle prédit parfois des valeurs différentes.
Cela arrive souvent quand la relation n’est pas parfaitement linéaire ou qu’il y a du bruit dans les données.
C’est normal
Ce genre de dispersion est attendu, surtout avec un seul feature.
L’important est d’observer la tendance générale : si la majorité des points suivent la diagonale, le modèle a capté une partie de la relation.
Si les points sont très dispersés, le modèle n’explique pas bien la variable cible.

'''

## perform two feature linear regressions here:

## perform two feature linear regressions here:
# --------- Modèle avec [Aces,DoubleFaults,] ---------
# Feature: [Aces,DoubleFaults,], Target: Wins
#
# X = df[['Aces','DoubleFaults']]
# Y = df[['Wins']]
#
# #plot data into training set and test set
#
# X_train, X_test,Y_train, Y_test = train_test_split(
#   X,
#   Y,
#   train_size= 0.8,
#   test_size = 0.2
# )
#
# #creation du model
# mlr_1 = LinearRegression()
# #entrainement du model
# mlr_1.fit(X_train,Y_train)
# #Affichage des coefficients
# b = mlr_1.intercept_
# m = mlr_1.coef_
# #prediction
# y_predicted = mlr_1.predict(X_test)
# print ("La prediction est  ceci: ",y_predicted)
#
# #Visualisation
#
# # Afficher la comparaison entre valeurs réelles (Y_test) et valeurs prédites (y_predicted)
# plt.scatter (Y_test,y_predicted, color = 'g',alpha = 0.4)
# plt.xlabel('Valeur reelle (Wins) ')
# plt.ylabel("Valeur predites (Wins)")
# plt.title('Prediction de Wins avec Aces et DoubleFaults')
# plt.grid(True)
# plt.legend()
# plt.show()



'''======================================================================'''

# --------- Modèle avec [FirstServe,FirstServePointsWon,] ---------
# Feature: [FirstServe,FirstServePointsWon,], Target: Wins

X = df [['FirstServe','FirstServePointsWon']]
Y = df [['Wins']]

#plot data into training set and test set

X_train, X_test, Y_train, Y_test = train_test_split(
  X,
  Y,
  train_size=0.8,
  test_size=0.2
)

#creation du model
mlr_100 = LinearRegression()
#entrainement des donnees
mlr_100.fit(X_train,Y_train)
#affichage des coeficients :
m100 = mlr_100.coef_
b100= mlr_100.intercept_
#prediction

y_predicted_100 = mlr_100.predict(X_test)
print('la valeur predite est: ',y_predicted_100)

#Visualisation

print('Affichage des comparaison entre les valeurs reelles et les valeurs preditess')
plt.figure(figsize=(8,5))
plt.scatter(Y_test,y_predicted_100 ,color ='orange',alpha=0.5,label= 'Valaurs reelles')
plt.xlabel('Valeurs reelles de Wins ')
plt.ylabel('Valeur predite de Wins/.')
plt.legend()
plt.grid(True)
plt.show()

'''======================================================================'''


# --------- Modèle avec [FirstServe,FirstServePointsWon,] ---------
# Feature: [FirstServe,FirstServePointsWon,], Target: Wins















## perform multiple feature linear regressions here:

'''======================================================================'''




## perform multiple feature linear regressions here:

# --------- Modèle avec [Aces,DoubleFaults,FirstServe,FirstServePointsWon] ---------
# Feature: [Aces,DoubleFaults,FirstServe,FirstServePointsWon], Target: Wins

# X = df[['Aces','DoubleFaults','FirstServe','FirstServePointsWon']]
# Y = df[['Wins']]
#
# #plot data into training set and test set
#
# X_train, X_test,Y_train, Y_test = train_test_split(
#   X,
#   Y,
#   train_size= 0.8,
#   test_size = 0.2
# )
#
# #creation du model
# mlr_1 = LinearRegression()
# #entrainement du model
# mlr_1.fit(X_train,Y_train)
# #Affichage des coefficients
# b = mlr_1.intercept_
# m = mlr_1.coef_
# #prediction
# y_predicted = mlr_1.predict(X_test)
# print ("La prediction est : ",y_predicted)
#
# #Visualisation
#
# # Afficher la comparaison entre valeurs réelles (Y_test) et valeurs prédites (y_predicted)
# plt.scatter (Y_test,y_predicted, color = 'g',alpha = 0.4)
# plt.xlabel('Valeur reelle (Wins) ')
# plt.ylabel("Valeur predites (Wins)")
# plt.title('Prediction de Wins avec Aces,DoubleFaults,FirstServe,FirstServePointsWon')
# plt.grid(True)
# plt.legend()
# plt.show()
# plt.clf()

















#Voici quelques suggestions pour les rendre encore plus précis et cohérents avec ce que fait chaque bloc de code:

## perform single feature linear regressions here:

# Afficher les colonnes et les types de données du DataFrame
# print("\n\n\n Les colonnes : ",df.columns)
# print("\n\n\n Les types : ",df.dtypes)

# --------- Modèle avec FirstServePointsWon ---------
# Feature: FirstServePointsWon, Target: Wins

# Séparer les données en train et test
# X = FirstServePointsWon, Y = Wins
# Entraîner le modèle sur 80% des données, tester sur 20%
# Prédire les valeurs de Wins sur le jeu de test
# Afficher la comparaison entre valeurs réelles et prédites

'''Pour chaque modèle, tu peux utiliser ce schéma:'''

# --------- Modèle avec [Nom de la feature] ---------
# Feature: [Nom de la feature], Target: Wins

# Séparer les données en train et test
# Entraîner le modèle
# Prédire sur le jeu de test
# Afficher la comparaison entre valeurs réelles (Y_test) et prédites (y_predicted)


'''Pour la partie brute (relation simple entre deux variables, sans prédiction'''
# Afficher la relation brute entre DoubleFaults et Wins (toutes les données)
# plt.scatter(df['DoubleFaults'], df['Wins'], ...)

'''Pour la performance du modèle :'''

# Afficher la comparaison entre valeurs réelles (Y_test) et valeurs prédites (y_predicted)
# plt.scatter(Y_test, y_predicted, ...)



'''Suggestions pour aller plus loin :

Ajoute le calcul du score R² pour chaque modèle (model.score(X_test, Y_test))
Teste d’autres combinaisons de features pour voir l’impact sur la performance
Ajoute une conclusion sur les features les plus importantes ou sur la qualité des modèles
En résumé
Ce projet est solide pour un portfolio débutant. Il montre que tu sais manipuler des données, entraîner des modèles, et interpréter les résultats.
Pour un entretien ou une candidature, explique bien ta démarche et ce que tu as appris à chaque étape.'''
#
# Calculer un score
# Tu peux aussi utiliser le score R² pour mesurer la performance :
# print(slr_2.score(X_test, Y_test))

# Copy code
#
# Interprétation
#
# Si les points sont proches d’une droite diagonale, le modèle prédit bien.
# Si les points sont très dispersés, le modèle prédit mal.
# Un score R² proche de 1 indique un bon modèle.



#
#
# Identifying Data
# Player: name of the tennis player
# Year: year data was recorded
# Service Game Columns (Offensive)
# Aces: number of serves by the player where the receiver does not touch the ball
# DoubleFaults: number of times player missed both first and second serve attempts
# FirstServe: % of first-serve attempts made
# FirstServePointsWon: % of first-serve attempt points won by the player
# SecondServePointsWon: % of second-serve attempt points won by the player
# BreakPointsFaced: number of times where the receiver could have won service game of the player
# BreakPointsSaved: % of the time the player was able to stop the receiver from winning service game when they had the chance
# ServiceGamesPlayed: total number of games where the player served
# ServiceGamesWon: total number of games where the player served and won
# TotalServicePointsWon: % of points in games where the player served that they won
# Return Game Columns (Defensive)
# FirstServeReturnPointsWon: % of opponents first-serve points the player was able to win
# SecondServeReturnPointsWon: % of opponents second-serve points the player was able to win
# BreakPointsOpportunities: number of times where the player could have won the service game of the opponent
# BreakPointsConverted: % of the time the player was able to win their opponent’s service game when they had the chance
# ReturnGamesPlayed: total number of games where the player’s opponent served
# ReturnGamesWon: total number of games where the player’s opponent served and the player won
# ReturnPointsWon: total number of points where the player’s opponent served and the player won
# TotalPointsWon: % of points won by the player
# Outcomes
# Wins: number of matches won in a year
# Losses: number of matches lost in a year
# Winnings: total winnings in USD($) in a year
# Ranking: ranking at the end of year
# 3.
# Perform exploratory analysis on the data by plotting different features against the different outcomes. What relationships do you find between the features and outcomes? Do any of the features seem to predict the outcomes?
#
# We utilized matplotlib’s .scatter() method to plot different features against different outcomes. Check out the documentation here for a refresher on how to utilize it.
#
# We found a strong relationship between the BreakPointsOpportunities feature and the Winnings outcome.
#
# 4.
# Use one feature from the dataset to build a single feature linear regression model on the data. Your model, at this point, should use only one feature and predict one of the outcome columns. Before training the model, split your data into training and test datasets so that you can evaluate your model on the test set. How does your model perform? Plot your model’s predictions on the test set against the actual outcome variable to visualize the performance.
#
# 5.
# Create a few more linear regression models that use one feature to predict one of the outcomes. Which model that you create is the best?
#
# 6.
# Create a few linear regression models that use two features to predict yearly earnings. Which set of two features results in the best model?
#
# 7.
# Create a few linear regression models that use multiple features to predict yearly earnings. Which set of features results in the best model?
#
# Head to the Codecademy forums and share your set of features that resulted in the highest test score for predicting your outcome. What features are most important for being a successful tennis player?
#
# Solution
# 8.
# Great work! Visit our forums to compare your project to our sample solution code. You can also learn how to host your own solution on GitHub so you can share it with other learners! Your solution might look different from ours, and that’s okay! There are multiple ways to solve these projects, and you’ll learn more by seeing others’ code.
#





"""


Pour effectuer une boucle sur une colonne d'un DataFrame Pandas en utilisant isin() ou apply(), vous pouvez utiliser apply() avec une fonction lambda pour itérer sur les éléments de la colonne et appliquer une condition, ou utiliser isin() pour vérifier si les valeurs de la colonne sont dans un ensemble donné, ce qui renvoie un booléen. 
Voici des exemples pour chaque méthode :
Utilisation de apply() avec une fonction lambda : 
Python

import pandas as pd

# Créer un DataFrame exemple
data = {'colonne': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
df = pd.DataFrame(data)

# Définir une fonction lambda pour vérifier si la valeur est paire
est_pair = lambda x: x % 2 == 0

# Appliquer la fonction à la colonne et stocker le résultat dans une nouvelle colonne
df['est_pair'] = df['colonne'].apply(est_pair)

print(df)
Ce code crée un DataFrame exemple, définit une fonction lambda pour vérifier si un nombre est pair, puis utilise apply() pour appliquer cette fonction à chaque élément de la colonne 'colonne'. Le résultat est stocké dans une nouvelle colonne nommée 'est_pair'. 
Utilisation de isin() :
Python

import pandas as pd

# Créer un DataFrame exemple
data = {'colonne': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']}
df = pd.DataFrame(data)

# Définir une liste de valeurs à vérifier
valeurs_a_verifier = ['a', 'c', 'e', 'g', 'i']

# Vérifier si les valeurs de la colonne sont dans la liste
df['est_dans_liste'] = df['colonne'].isin(valeurs_a_verifier)

print(df)
Dans cet exemple, isin() est utilisé pour vérifier si chaque valeur de la colonne 'colonne' existe dans la liste valeurs_a_verifier. Le résultat est un booléen stocké dans la nouvelle colonne 'est_dans_liste'.
Quelle méthode choisir ?
apply() avec une fonction lambda :
Utile pour des opérations plus complexes où vous devez effectuer des calculs ou des transformations sur les valeurs de la colonne.
isin() :
Idéal pour vérifier si des valeurs sont présentes dans un ensemble donné, renvoyant un booléen pour chaque élément. 
En résumé, choisissez apply() pour des opérations plus personnalisées et isin() pour des vérifications de présence dans un ensemble de valeurs.

"""


