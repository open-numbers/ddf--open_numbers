import pandas as pd
import re

df = pd.read_csv('../../ddf--synonyms--geo.csv')

cp = df.copy()
regex = re.compile(r"^[A-Za-z0-9\s\(\)]*$", re.IGNORECASE)
cp['synonym'] = cp['synonym'].apply(lambda str: str.replace(' ','_') if regex.search(str) else str)

df = pd.concat([df,cp])
df = df.drop_duplicates()
df.to_csv('snake_case_synonyms.csv', index=False)

test_synonyms = [] # list of synonyms to test against
for syn in test_synonyms:
    if syn not in list(df['synonym']):
        print('Not found', syn)