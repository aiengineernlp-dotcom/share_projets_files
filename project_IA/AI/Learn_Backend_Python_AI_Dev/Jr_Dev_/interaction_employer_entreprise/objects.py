import classes
# instanciation

company = classes.Company('Beyond_inc',)

employee_1 = classes.Employee('OMAR',90000)
employee_2 = classes.Employee('Ali',9000)
employee_3 = classes.Employee('Tony',5000)

list_employee = [employee_1,employee_2]


#interactions

print('==========Add_employee=======================================================================================================\n')
company.add_employee(list_employee)
company.add_employee(employee_3)
print('===Increase_all_employee_salary==============================================================================================================\n')
company.increase_all_employee_salary(1000)
employee_1.increase_salary(5000)

print('=========Display_employee_list========================================================================================================\n')
company.display_employee_list()











print('=================================================================================================================\n')
