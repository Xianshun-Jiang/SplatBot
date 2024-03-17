import pandas as pd
import json
df = pd.read_csv("./all.csv")

subs = df['Sub'].unique()
sub_dict = {key.replace(" ","",1): [] for key in subs}

range = df['ran'].unique()
range_dict = {key.replace(" ","",1): [] for key in range}

for idx,i in df.iterrows():
    sub_dict[i['Sub'].replace(" ","",1) ].append(i['Name'])
    range_dict[i['ran'].replace(" ","",1) ].append(i['Name'])
    print(type(i))

filename = 'sub-weapon.json'
filename2 = 'range-weapon.json'
with open(filename, 'w') as f:
    json.dump(sub_dict, f, indent=4)
with open(filename2, 'w') as f:
    json.dump(range_dict, f, indent=4)
print(range_dict)