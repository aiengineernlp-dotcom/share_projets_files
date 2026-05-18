import pandas as pd
import nltk

from src.preprocessing.cleaner import CleanDataset

nltk.download("punk_tab")
nltk.download("stopwords")
from src.preprocessing import tokenizer


from tqdm import tqdm
tqdm.pandas()

df = pd.read_csv("data/raw/Reviews.csv")

df = df.dropna(subset=["Text"])

cleandataset_1 = CleanDataset('english')


