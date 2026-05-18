def count (word):
    count=0
    for letter in word:
        if letter =='a':
            count = count+1
            print(count)
        else:
            print('pas de a touver  ')
count('trontaa')

#===================================voici une version corrigée et améliorée du code :=======================================================================
# def count(word):
#     count = 0
#     for letter in word:
#         if letter == 'a':
#             count += 1
#     if count > 0:
#         print(f"Nombre de lettres 'a' trouvées : {count}")
#     else:
#         print("Pas de 'a' trouvé.")
#
#
# count('trontaa')
