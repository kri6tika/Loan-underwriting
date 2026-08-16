import pandas as pd

df = pd.read_csv("data/raw/loan_data.csv")

df = df.drop_duplicates()

df = df.fillna(0)

print(df.isnull().sum())
