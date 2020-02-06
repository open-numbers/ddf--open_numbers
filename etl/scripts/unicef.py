# coding: utf-8

import os.path as osp
import pandas as pd

from ddf_utils.io import open_google_spreadsheet


DOCID = '1POAjAhMgUjv6Mt_FSVSgzAr7c6oUvzinpQPvhfmOuuU'
SHEET = 'data-for-countries-etc-by-year'


def main():
    country_df = pd.read_csv('../../ddf--entities--geo--country.csv', dtype=str)
    unicef_df = pd.read_excel(open_google_spreadsheet(DOCID), sheet_name=SHEET)

    # unicef entity set
    unicef_regions = unicef_df[['unicef region', 'unicef region full name']].drop_duplicates(subset='unicef region')
    unicef_regions.columns = ['unicef_region', 'name']
    unicef_regions.to_csv('../../ddf--entities--geo--unicef_region.csv', index=False)

    # update country properties
    country_df = country_df.set_index('country')
    unicef_df = unicef_df.rename(columns={'geo': 'country'}).set_index('country')

    country_df['unicef_region'] = unicef_df.reindex(country_df.index)['unicef region']
    country_df.to_csv('../../ddf--entities--geo--country.csv')


if __name__ == '__main__':
    main()
    print('Done.')
