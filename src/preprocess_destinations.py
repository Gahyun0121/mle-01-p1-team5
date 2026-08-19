import pandas as pd
import re

dst = pd.read_csv('./data/raw/travel_destinations.csv')
master = pd.read_csv('./data/country_master.csv', encoding='utf-8-sig')

print(dst.shape)  # (111, 4)
print(dst.info())

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def get_months(s):
    found = re.findall('|'.join(MONTHS), str(s))
    return '|'.join(sorted(set(found), key=MONTHS.index))

THEME_MAP = {
    '역사문화': ['history','culture','temple','shrine','ruins','heritage','palace','mythology','religion','colonial','traditional','monument'],
    '예술': ['art','museum','music','architecture','design','theatre','literature','film','pop culture','bollywood'],
    '자연': ['nature','mountain','lake','glacier','desert','waterfall','forest','aurora','northern lights','garden','rice paddies','canal','viewpoint'],
    '해변': ['beach','island','coast','surf','diving','snorkel','archipelago','reef'],
    '액티비티': ['hiking','adventure','ski','cycling','trek','sports','safari','rafting','elephant'],
    '미식': ['food','cuisine','wine','beer','coffee','dim sum','pub'],
    '쇼핑': ['shopping','market','bazaar'],
    '휴양': ['spa','wellness','yoga','relax','hygge','romance','nightlife'],
}

def get_themes(cat):
    c = str(cat).lower()
    hit = [t for t, kws in THEME_MAP.items() if any(k in c for k in kws)]
    return '|'.join(hit) if hit else '기타'

dst['months'] = dst['Best_Time_to_Travel'].apply(get_months)
dst['themes'] = dst['Category'].apply(get_themes)

# 붙이기
dst = dst.merge(
    master[['kaggle_country', 'country_kr', 'iso3']],
    left_on='Country',
    right_on='kaggle_country',
    how='left'
)
dst = dst.drop(columns=['kaggle_country'])

dst = dst.rename(columns={'City': 'city', 'Country': 'country_en', 'Category': 'category_raw'})
dst = dst[['city', 'country_en', 'country_kr', 'iso3', 'themes', 'months', 'category_raw']]

print('전체 국가 수:', dst['country_en'].nunique())
print('iso3 없는 국가:', dst[dst['iso3'].isna()]['country_en'].unique())
print('테마 미분류:', dst[dst['themes'] == '기타'][['city', 'category_raw']].to_string())
print('월 비어있음:', dst[dst['months'] == '']['city'].tolist())

dst.to_csv('./data/destinations_clean.csv', index=False, encoding='utf-8-sig')
print('저장 완료')