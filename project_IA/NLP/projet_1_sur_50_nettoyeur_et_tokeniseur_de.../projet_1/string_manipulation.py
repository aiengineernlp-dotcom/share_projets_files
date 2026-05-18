text = "Le client veut acheter une maison a yaounde"
decomposition = text.split()
mots_courts = []
mots_long  = []
for index_mot in decomposition:
     if len(index_mot)>=4:
         mots_long.append(index_mot)
     elif len(index_mot)<=4:
         mots_courts.append(index_mot)



print("les mots court<=4:", len(mots_courts))
print('les mots longs >=4',len(mots_long))
print('le reste de mots',mots_long )




