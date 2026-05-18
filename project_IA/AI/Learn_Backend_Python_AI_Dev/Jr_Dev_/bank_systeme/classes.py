class Account:
    def __init__(self, number,owner, sold):
        self .number = number
        self.owner = owner
        self.sold = sold

    def __str__(self):
        return f"{self.number} - {self.owner} - {self.sold}"

    def deposit(self,amount):
        self.sold+=amount
        print(f"Votre compte a ete crediter de {amount}\nNouveau solde est de {self.sold}")
        # return amount

    def whitdrawal(self,amount):
        if amount<=self.sold:
            self.sold-=amount
            print(f"Votre compte a ete depiter de {amount}\nNouveau solde est de {self.sold}")
            #return amount

    def display_account(self):
        print(self.owner, f"Your account is {self.sold} AED")


class Bank:
    def __init__(self,name,):
        self.name = name
        self.accounts = []

    def __str__(self):
        return f"Name: {self.name}, {self.accounts}"

    def add_account(self,new_account):
        if isinstance(new_account,list):
            self.accounts.extend(new_account)
            print(f"Comptes ajoutés: {len(self.accounts)}")
        else:
            self.accounts.append(new_account)
            print(f"Tous les comptes: {len(self.accounts)}")

    def transfer(self,sender,receiver,amount):
        if sender.sold>=amount:
            sender.sold -= amount
            receiver.sold+=amount
            print(f"{sender.owner} a fait un transfer de {amount}  AED a {receiver.owner}")
        else:
            print('Fonds inssuiffisant pour cette operation')







