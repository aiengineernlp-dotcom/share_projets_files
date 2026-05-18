import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#chargement du dataset
coffee = pd.read_csv("../data/coffee_data.csv")
print(coffee.info())

#definir la variable/ caracteristique  : nearest_starbucks
nearest_starbucks = coffee["nearest_starbucks"]

log_nearest_starbucks = np.log(nearest_starbucks)

# Tracer de l'histogramme

plt.xticks(rotation = 9)
plt.hist(log_nearest_starbucks, bins=80, color = 'g', edgecolor = 'black')
plt.title('TRansformation logarithmique')
plt.xlabel('')
plt.ylabel('')
plt.show()








