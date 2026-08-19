import pandas as pd
import html

alm = pd.read_json('./data/raw/alarm.json')
master = pd.read_csv('./data/country_master.csv', encoding='utf-8-sig')

print(alm.shape) # (208, 9)
print(alm.columns.tolist())
print(alm.info())

# 버리기
alm = alm.drop(columns=['작성일'])

# 고치기
alm['경보내용'] = alm['경보내용'].apply(html.unescape)
alm['경보내용'] = alm['경보내용'].str.replace(r'\s+', ' ', regex=True).str.strip()

# 붙이기
alm = alm.merge(
    master[['country_kr', 'iso3']],
    left_on='국가명',
    right_on='country_kr',
    how='left'
)
alm = alm.drop(columns=['country_kr'])


print(alm.shape)
print('전체 국가 수:', alm['국가명'].nunique())
print('iso3 없는 국가:', alm[alm['iso3'].isna()]['국가명'].nunique(), '개국')
print(alm[alm['국가명'] == '러시아'][['국가명', '경보단계', '경보내용']])


alm.to_csv('./data/alarm_clean.csv', index=False, encoding='utf-8-sig')
print('저장 완료')