import pandas as pd
# dataset  = pd.read_csv('data/Reviews.csv')
mydataset = pd.read_csv('data/Reviews.csv')

if __name__ == "__main__":

    print("\nMes donnees brutes du dataset .....")
    print(mydataset.head(5))
    print("\nMes types de donnees brutes du dataset .....")
    print(mydataset.dtypes)

    print('Affichage des etiquettes')
    print(mydataset['Text'].value_counts())


