import pandas as pd

df = pd.read_csv("./all.csv")

one_third = df['Range'].quantile(0.3333)
two_third = df['Range'].quantile(0.6667)

for i in df['Range']:
    if i < one_third:
        df['ran'] = "Short"
    elif i < two_third:
        df['ran'] = "Median"
    else:
        df['ran'] = "Long"

df.to_csv("./all.csv", index=False)
print(df)