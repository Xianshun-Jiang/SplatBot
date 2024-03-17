import pandas as pd

df = pd.read_csv("./all.csv")

one_third = df['Range'].quantile(0.3333)
two_third = df['Range'].quantile(0.6667)

# Define a function to categorize the range
def categorize_range(x):
    if x < one_third:
        return "Short"
    elif x < two_third:
        return "Median"
    else:
        return "Long"

# Apply the function to the 'Range' column and assign the result to a new column 'ran'
df['ran'] = df['Range'].apply(categorize_range)

# Save the modified DataFrame back to the CSV
df.to_csv("./all.csv", index=False)

print(df.ran.value_counts())