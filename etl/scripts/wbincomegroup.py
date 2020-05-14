"""
Load income groups from WDI, add income_3groups entity_set and update
income_groups/income_3groups country properties.
Make sure you have the correct source WDI dataset checked out in your datasets folder
"""

import os
import pandas as pd

from ddf_utils.model.package import DDFcsv
from ddf_utils.transformer import translate_column

datasets_dir = os.environ.get('DATASETS_DIR') or '../../../../'

if __name__ == '__main__':
    wb_ddf = DDFcsv.from_path(
        os.path.join(
            datasets_dir,
            'open-numbers/ddf--world_bank--world_development_indicators/')
    ).load_ddf()
    country = wb_ddf.get_entities('economy', 'country')
    income_3level = wb_ddf.get_entities('economy', 'income_3level')

    wdi_country_df = pd.DataFrame.from_records([v.to_dict() for v in country])
    income_3lvl_df = pd.DataFrame.from_records(
        [v.to_dict() for v in income_3level])

    # translate entity id
    income_3level_map = dict(hic='high_income',
                             lic='low_income',
                             mic='middle_income')
    income_4level_map = dict(hic='high_income',
                             lic='low_income',
                             lmc='lower_middle_income',
                             umc='upper_middle_income')

    wdi_country_df['income_3level'] = wdi_country_df['income_3level'].map(
        income_3level_map)
    wdi_country_df['income_4level'] = wdi_country_df['income_4level'].map(
        income_4level_map)

    income_3lvl_df['economy'] = income_3lvl_df['economy'].map(income_3level_map)

    # export entity sets
    income_3lvl_df = income_3lvl_df.rename(columns={
        'economy': 'income_3groups',
        'is--income_3level': 'is--income_3groups'
    })
    rank_map = {'high_income': 3, 'middle_income': 2, 'low_income': 1 }
    income_3lvl_df['rank'] = income_3lvl_df['income_3groups'].map(rank_map)
    income_3lvl_df.dropna(axis=1, how='any').to_csv(
        '../../ddf--entities--geo--income_3groups.csv', index=False)

    # modify countries
    on_country_df = pd.read_csv('../../ddf--entities--geo--country.csv',
                                dtype=str)

    on_synonyms = pd.read_csv('../../ddf--synonyms--geo.csv')

    wdi_country_df_translated = translate_column(df=wdi_country_df,
                                                 column='name',
                                                 target_column='geo',
                                                 dictionary_type='dataframe',
                                                 dictionary=dict(key='synonym',
                                                                 value='geo'),
                                                 base_df=on_synonyms,
                                                 not_found='drop')

    on_country_df = translate_column(df=on_country_df,
                                     column='country',
                                     target_column='income_3groups',
                                     dictionary_type='dataframe',
                                     dictionary=dict(key='geo',
                                                     value='income_3level'),
                                     base_df=wdi_country_df_translated,
                                     not_found='include')
    on_country_df = translate_column(df=on_country_df,
                                     column='country',
                                     target_column='income_groups',
                                     dictionary_type='dataframe',
                                     dictionary=dict(key='geo',
                                                     value='income_4level'),
                                     base_df=wdi_country_df_translated,
                                     not_found='include')
    on_country_df.to_csv('../../ddf--entities--geo--country.csv', index=False)

    # modify concepts
    concept_df = pd.read_csv('../../ddf--concepts.csv', dtype=str)

    if 'income_3groups' not in concept_df['concept'].values:
        income_3group_concept = pd.DataFrame.from_records(data=[
            dict(concept='income_3groups',
                 concept_type='entity_set',
                 domain='geo',
                 name='Income Groups (3 levels)',
                 tags='categorizations')
        ])
        concept_df = concept_df.append(income_3group_concept, sort=False)
        concept_df.to_csv('../../ddf--concepts.csv', index=False)

    print('Done')
