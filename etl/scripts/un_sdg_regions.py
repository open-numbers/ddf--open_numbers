# coding: utf-8

import os.path as osp
import pandas as pd
import json
import requests
from ddf_utils.str import to_concept_id

UN_SDG_URL = 'https://unstats.un.org/SDGAPI/v1/sdg/GeoArea/Tree'

# Most SDG Regions are not official UN regions (M49) and should be divided into Subregions so we can read what countries belong to it. 
# This subdivision is not given in the API/Data, so we manually do it here.
region_composition = {
    202: [],           # Sub-Saharan Africa
    747: [15, 145],    # Northern Africa and Western Asia. 15 northern africa, 145 western asia
    62:  [143, 34],    # Central and Southern Asia. 143 central asia, 34 southern asia
    753: [35, 30],     # Eastern and South-Eastern Asia. 35 south-eastern asia, 30 eastern asia
    543: [54, 57, 61], # Oceania excluding Australia and New Zealand. 54 Melanesia, 57 Micronesia, 61 Polynesia
                        # assumption: Christmas Island, Cocos Islands, Heard & McDonald Islands and Norfolk Islands are part of Australia & New Zealand
    419: [],           # Latin America and the Caribbean
    53:  [],           # Australia and New Zealand
    513: [150, 21]     # Europe and Northern America. 150 Europe, 21 Northern America
}

# Colors picked from https://unstats.un.org/sdgs/indicators/regional-groups/
region_color = {
    202: 'e11484', # Sub-Saharan Africa
    747: 'f99d26', # Northern Africa and Western Asia
    62:  'f36d25', # Central and Southern Asia 
    753: '279b48', # Eastern and South-Eastern Asia
    543: '8f1838', # Oceania excluding Australia and New Zealand
    419: '00aed9', # Latin America and the Caribbean
    53:  'eb1c2d', # Australia and New Zealand
    513: '02558b'  # Europe and Northern America
}

def flatten(node): 
    node_id = node['geoAreaCode']
    new_children = []
    flattened = {
        node_id: node
    }
    if node['children'] is not None:
        for childNode in node['children']:
            if childNode['type'] == 'Country':
                new_children.append(childNode)
            else: 
                flatChild = flatten(childNode)
                flattened.update(flatChild)
                child_id = childNode['geoAreaCode']
                new_children += flatChild[child_id]['children']
    flattened[node_id]['children'] = new_children
    return flattened

def csv_to_dict(csv, keyCol, valCol):
    import csv

    data={}
    with open(csv) as fin:
        reader=csv.reader(fin, skipinitialspace=True, quotechar="'")
        for row in reader:
            data[row[0]]=row[1:]
    return data

def main():
    country_df = pd.read_csv('../../ddf--entities--geo--country.csv', dtype=str)
    synonyms_dict = pd.read_csv('../../ddf--synonyms--geo.csv', dtype=str).set_index('synonym').geo.to_dict()
    
    r = requests.get(UN_SDG_URL)
    regions_tree = r.json()
    regions_flat = flatten(regions_tree[0]) # 0 = world

    # Least Developed Countries
    ldc_entities = [ {
        'un_sdg_ldc': 'un_least_developed',
        'name': regions_tree[1]['geoAreaName'],
        'is--un_sdg_ldc': 'TRUE'
    },{
        'un_sdg_ldc': 'un_not_least_developed',
        'name': 'Other UN Countries',
        'is--un_sdg_ldc': 'TRUE'
    }]
    ldc_countries = []
    ldc_set = set()
    for country in regions_tree[1]['children']:
        code = str(country['geoAreaCode'])
        if code in synonyms_dict:
            ldc_countries.append({
                'country': synonyms_dict[code],
                'un_sdg_ldc': 'un_least_developed'
            })
            ldc_set.add(code)
        else:
            print('Could not find synonym for ', country)
    for country in regions_flat[1]['children']:
        code = str(country['geoAreaCode'])
        if code in synonyms_dict and code not in ldc_set:
            ldc_countries.append({
                'country': synonyms_dict[code],
                'un_sdg_ldc': 'un_not_least_developed'
            })

    # SDG Regions
    regions = []
    region_countries = []
    for region_id, subregions in region_composition.items():
        region_name = regions_flat[region_id]['geoAreaName']
        region_entity_id = 'un_' + to_concept_id(region_name)
        region = {
            'un_sdg_region': region_entity_id,
            'name': region_name,
            'color': '#' + region_color[region_id],
            'is--un_sdg_region': 'TRUE'
        }
        regions.append(region)

        subregions.append(region_id)
        for subregion in subregions:
            for country in regions_flat[subregion]['children']:
                code = str(country['geoAreaCode'])
                if code in synonyms_dict:
                    region_countries.append({
                        'country': synonyms_dict[code],
                        'un_sdg_region': region_entity_id
                    })
                else:
                    print('Could not find synonym for ', country)
    
    

    # un sdg region entity set
    regions_df = pd.DataFrame.from_records(regions)
    regions_df.to_csv('../../ddf--entities--geo--un_sdg_region.csv', index=False)
    
    # un sdg ldc entity set
    ldc_df = pd.DataFrame.from_records(ldc_entities)
    ldc_df.to_csv('../../ddf--entities--geo--un_sdg_ldc.csv', index=False)

    # update country properties
    country_df = country_df.set_index('country')
    region_countries = pd.DataFrame.from_records(region_countries).set_index('country')
    ldc_countries = pd.DataFrame.from_records(ldc_countries).set_index('country')

    country_df['un_sdg_region'] = region_countries.reindex(country_df.index)['un_sdg_region']
    country_df['un_sdg_ldc'] = ldc_countries.reindex(country_df.index)['un_sdg_ldc']
    country_df.to_csv('../../ddf--entities--geo--country.csv')


if __name__ == '__main__':
    main()
    print('Concept file was not manipulated. Please update concepts and their properties (e.g. colors) manually if needed.')
    print('Done.')
