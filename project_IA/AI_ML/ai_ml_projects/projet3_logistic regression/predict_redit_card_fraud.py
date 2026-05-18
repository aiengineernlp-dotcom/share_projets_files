import seaborn as sb
import pandas as pd
import numpy as np
import codecademylib3
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import codecademylib3

# Load the data
transactions = pd.read_csv('transactions_modified.csv')
print("transactions_head: ",transactions.head(),"\n")
print("transactions_info: ",transactions.info(),"\n")

df = pd.DataFrame(transactions)
# How many fraudulent transactions?

print("Fraudulent transactions:",sum(df['isFraud']),'Frauds','\n')


# Summary statistics on amount column
print("La Description statistics est:\n",df['amount'].describe(),'\n')
print("SOmme des statistics amount est:", sum(df['amount']),'\n')



# Create isPayment field
print("Question 3 verifier si les elements sont dans la collonne 'type' grace a la fontion .isin() \n ")
debit_payment=['PAYMENT','DEBIT'] # ma liste de elements

df['isPayment'] = df['type'].isin(debit_payment).astype(int)

print("le resultat est:\n",df)


 
# Create isMovement field
print("Question 4 verifier si les elements sont dans la collonne 'type' grace a la fontion .isin() \n ")
cash_out_transfer = ['CASH_OUT','TRANSFER']      #Ma liste d'elements
df['isMovement']= df['type'].isin(cash_out_transfer).astype(int)
print("Capture si l'argent sort du compte d'origine\n",df)

# Create accountDiff field
print("Calcule des differences entre le compte origine et le compte destination sachant que une differente tres forte de valeurs sera entre les deux comptes sera suspecte.")

df['accountDiff'] = abs(df['oldbalanceOrg'] - df['oldbalanceDest'])

# Create features and label variables
features = df[['amount','isPayment','isMovement','accountDiff']] # #notre X ou encore variables explicatives

label = df['isFraud']# Notre y ou encore variable cible

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
  features,
  label,
  train_size = 0.7,
  test_size = 0.3,
  random_state = 6
)


# Normalize the features variables
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# Fit the model to the training data
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# Score the model on the training data
score_training_data = model.score(X_train_scaled, y_train)
print("Accuracy_training_data:\n",score_training_data )
# Score the model on the test data
score_test_data = model.score(X_test_scaled, y_test)
print("Accuracy_test_data:\n",score_test_data )
# Print the model coefficients
coefficients = model.coef_
ord_origine = model.intercept_
print("coefficients du modele : \n", coefficients)
print("How did your model perform ? : score_training_data est superieur a Accuracy_test_data donc il ya surapprentissage ")

# question 12  Which feature was most important? Least important?
print("feature most important was 'accountDiff' because the coefficient is:7.73531296e-08 ")

print("feature Least important was 'isPayment' because the coefficient is:-3.75447098e-12 ")
# New transaction data
transaction1 = np.array([123456.78, 0.0, 1.0, 54670.1])
transaction2 = np.array([98765.43, 1.0, 0.0, 8524.75])
transaction3 = np.array([543678.31, 1.0, 0.0, 510025.5])

# Create a new transaction
your_transaction = np.array([113551.10,4.5,5.9,12345678.3])


# Combine new transactions into a single array
sample_transactions = np.array([transaction1,transaction2,transaction3,your_transaction])
# sample_transactions = np.array([transaction1, transaction2, transaction3, your_transaction])
print("sample_transactions:::::\n",sample_transactions)

# Normalize the new transactions
sample_transactions_scaled= scaler.transform(sample_transactions)

# Predict fraud on the new transactions
predictions = model.predict (sample_transactions_scaled)
print("predictions:\n",predictions)

probabilities = model.predict_proba(sample_transactions_scaled)
print("probabilities:",probabilities,"\n")


# Show probabilities on the new transactions
