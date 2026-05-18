import csv
from functools import reduce


def count(predicate, iterable):
    count_filter = filter(lambda x: predicate(x), iterable)
    reduce_filter = reduce(lambda x, y: x + 1, count_filter, 0)
    return reduce_filter


# def average(itr):
#   iterable = iter(itr)
#   def avg_helper(curr_count,itr,curr_sum):
#     next_num = next(itr,"null")
#     curr_sum = curr_sum + next_num
#     curr_count = curr_count + 1
#     if next_num=="null":
#       return curr_sum/curr_count

"""Retour sur ton raisonnement :

Tu as bien compris l’utilisation de next() et la condition d’arrêt.
Il faut juste placer la condition avant l’addition et l’incrémentation.
Conseil :

Utilise bien itr dans next(), pas iterable.
Place la condition d’arrêt avant de modifier la somme et le compteur."""


def average(itr):
    iterable = iter(itr)

    def avg_helper(curr_count, itr, curr_sum):
        next_num = next(itr, "null")
        if next_num == "null":
            return curr_sum / curr_count
        curr_sum += next_num
        curr_count += 1
        return avg_helper(curr_count, itr, curr_sum)

    return avg_helper(0, iterable, 0)  # question 6


#     Oui, ce que tu as dit à propos de la fonction next() est correct.

# Résumé de ce que tu as dit :

# next() prend en paramètre un itérable (généralement un itérateur) et une valeur par défaut.
# Si l’itérateur a encore des éléments, next() retourne le prochain élément.
# Si l’itérateur est épuisé, next() retourne la valeur par défaut (par exemple "null").
# Exemple :

# it = iter([1, 2])
# print(next(it, "fin"))  # Affiche 1
# print(next(it, "fin"))  # Affiche 2
# print(next(it, "fin"))  # Affiche "fin"

# Copy code

# Ton explication sur le fonctionnement de next() est donc juste.


with open('1kSalesRec.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    fields = next(reader)
    count_belgium = count(lambda x: x[1] == "Belgium", reader)
    print(count_belgium)
    csvfile.seek(0)
    avg_portugal = avg_portugal = average(
        map(lambda x: float(x[13]), filter(lambda x: x[1] == "Portugal", reader))
    )

    print(avg_portugal)