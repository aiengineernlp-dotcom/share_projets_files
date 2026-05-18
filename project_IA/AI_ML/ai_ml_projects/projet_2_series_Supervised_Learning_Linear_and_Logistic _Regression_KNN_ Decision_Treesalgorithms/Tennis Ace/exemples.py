import pandas as pd


def addition(a,b,c):
    return a +b+c
sol =addition(1,2,3)
print(sol)



def modulo(a,c):
    return a%c

mod = modulo(5,3)

print(mod)



data = {'colonne': [1,2,3,4,5,6,7,8,10]}

df = pd.DataFrame(data)

# creation de la fonction lambda pour savoir si la fonction est paire ou nom

est_pair = lambda x : x%2==0

# application de la fonctions lambda grace a apply sur la collonne en creant une nnouvelle collone

df['est_pair'] = df['colonne'].apply(est_pair)

print(df['est_pair'])
