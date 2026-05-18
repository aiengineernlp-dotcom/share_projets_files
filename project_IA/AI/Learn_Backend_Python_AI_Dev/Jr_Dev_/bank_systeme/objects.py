import classes
# Creation des objects (instantiation)
'CREATION BANQUES'
bank_1 = classes.Bank('Al Hilal')
'CREATION COMPTES'
account_1 = classes.Account(1,'Omar',40000)
account_2 = classes.Account(2,'Ali',4000)
account_3 = classes.Account(3,'Tony',5000)

"""INTERACTIONS"""
print('AJOUT DES COMPTES')
list_accounts = [account_1,account_3]
bank_1.add_account(list_accounts)
bank_1.add_account(account_2)
print('=================================================================================================================\n')
print('DISPLAY ACCOUNTS')
account_1.display_account()
account_2.display_account()
account_3.display_account()
print('=================================================================================================================\n')
print('crediter COMPTES')
account_1.deposit(1000)
account_2.deposit(1000)
account_3.deposit(1000)
print('=================================================================================================================\n')
print('debiter COMPTES')
account_1.whitdrawal(100)
account_2.whitdrawal(100)
account_3.whitdrawal(100)
print('=================================================================================================================\n')
print('TRANSFERER ARGENT')
bank_1.transfer(account_1,account_3,3000)
print('=================================================================================================================\n')
print('DISPLAY ACCOUNTS')
account_1.display_account()
account_2.display_account()
account_3.display_account()















print('=================================================================================================================\n')
"""INTERACTIONS"""
print('AFFICHAGE DES POINTS AVANT LE JEUX')