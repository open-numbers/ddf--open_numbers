# %%
import pandas as pd
import shapefile
# %%
sf = shapefile.Reader("../source/GDL Shapefiles V6.zip")
# %%
sf.shapeTypeName
# %%
len(sf)
# %%
shapes = sf.shapes()
# %%
len(shapes)
# %%
shapes[0]
# %%
s = shapes[0]
# %%
s
# %%
s.oid
# %%
s.parts
# %%
s[0]
# %%
s.bbox
# %%
fields = sf.fields
# %%
fields
# %%
rec = sf.record(0)
# %%
rec
# %%
len(sf.records())
# %%
rec['gdlcode']
# %%
rec.as_dict()
# %%
records = sf.records()
# %%
df1 = pd.DataFrame.from_records([x.as_dict() for x in records])
# %%
df1
# %%
df2 = pd.read_csv('../../../ddf--gdl--shdi/ddf--entities--level--subnat.csv')
# %%
df3 = pd.read_csv('../../../ddf--gdl--area_db/ddf--entities--level--subnat.csv')
# %%
df2
# %%
df3
# %%
df4 = pd.concat([df2[['gdlcode', 'name']], df3[['gdlcode', 'name']]], ignore_index=True)
# %%
df4
# %%
df4 = df4.drop_duplicates(subset=['gdlcode'])
# %%
df4
# %%
df5 = pd.read_excel('../source/GDL-Codes Global Data Lab V5.xlsx')
# %%
df5
# %%
df5[df5['Region'].str.contains('Total')]
# %%
df5 = df5[~df5['Region'].str.contains('Total')]
# %%
df5
# %%
for code in df4['gdlcode'].values:
    if code not in df5['GDLCODE'].values:
        print(code)
# %%
df4.dropna()
# %%
for code in df5['GDLCODE'].values:
    if code not in df4['gdlcode'].values:
        print(code)
# %%
df5[df5['GDLCODE'] == 'CHNr133']
# %%
df4[df4['gdlcode'] == 'CHNr201']
# %%
df6 = df4.copy()
# %%
df6['subnational_region'] = df6['gdlcode'].str.lower()
df6['is--subnational_region'] = 'TRUE'
# %%
df6
# %%
df6[['subnational_region', 'name', 'is--subnational_region']].to_csv('../../ddf--entities--geo--subnational_region.csv', index=False)
# %%
