class Employee:
    def __init__(self,name,salary):
        self.name = name
        self.salary = salary

    def __str__(self):
        return f'Name: {self.name} - Salaire: {self.salary}'


    def increase_salary(self,amount):
        self.salary+=amount


class Company:
    def __init__(self, name,list_employee=None):
        self.name = name
        if list_employee is None:
            self.list_employee = []
        else:
            self.list_employee = list_employee

    def __str__(self):
        return f'Name: {self.name} - Liste Employee: {self.list_employee}'


    def add_employee(self,new_employee):
        if isinstance(new_employee , list):
            self.list_employee.extend(new_employee)
            print(f'Employe ajoutee:, {len(self.list_employee)},''employes')
        else:
            self.list_employee.append(new_employee)
            print(f'Nombre total des employee:',len(self.list_employee), 'employes')


    def increase_all_employee_salary(self,amount):
        for employee in self.list_employee:
            employee.salary+=amount
            print(f' Dear {employee.name}, {amount}','AED a ete ajouter a votre salaire.','Votre nouveau salaire passe de ',employee.salary-amount ,'AED', 'a',employee.salary,'AED' )


    def display_employee_list(self):
        for employee in self.list_employee:
            print(f'Employee',employee.name, f'Salaire {employee.salary}'' AED')

