import pandas as pd
import html
import json
import os

sft = pd.read_json('./data/raw/safety_info.json')
master = pd.read_csv('./data/country_master.csv', encoding='utf-8-sig')

print(sft.shape) # (5957, 7)
print(sft.info())
print(sft.head())

# 버리기
sft = sft.dropna(subset=['내용'])
sft = sft.drop(columns=['첨부파일'])
sft = sft.drop_duplicates(subset=['id'])

# 고치기
sft['내용'] = sft['내용'].apply(html.unescape)
sft['내용'] = sft['내용'].str.replace(r'\s+', ' ', regex=True).str.strip()
sft['제목'] = sft['제목'].astype(str).apply(html.unescape).str.strip()
sft['id'] = sft['id'].astype(str).str.strip()

# 붙이기
sft = sft.merge(
    master[['country_kr', 'iso3']], 
    left_on='국가명', 
    right_on='country_kr', 
    how='left'
            )
sft = sft.drop(columns=['country_kr'])


print(sft.shape)
print(sft.info())
print(sft.head())
print('전체 국가 수:', sft['국가명'].nunique())
print('iso3 붙은 국가:', sft['iso3'].notna().sum(), '건')
print('iso3 없는 국가:', sft[sft['iso3'].isna()]['국가명'].nunique(), '개국')


# 저장 1) 원문 CSV
sft.to_csv('./data/safety_clean.csv', index=False, encoding='utf-8-sig')

# 저장 2) 대시보드 차트용 — 국가·연도별 공지 건수
sft['year'] = pd.to_datetime(sft['작성일'], errors='coerce').dt.year
stats = sft.groupby(['iso3', '국가명', 'year'], dropna=False).size().reset_index(name='count')
stats = stats.rename(columns={'국가명': 'country_kr'})
stats.to_csv('./data/safety_stats.csv', index=False, encoding='utf-8-sig')

# 저장 3) RAG용 — 제목+내용을 한 덩어리로
with open('./data/safety_docs.jsonl', 'w', encoding='utf-8') as f:
    for _, r in sft.iterrows():
        f.write(json.dumps({
            'id': f"safety_{r['id']}",
            'text': f"{r['제목']}\n{r['내용']}",
            'metadata': {
                'source': '외교부 안전공지',
                'iso3': r['iso3'] if pd.notna(r['iso3']) else '',
                'country_kr': r['국가명'],
                'title': r['제목'],
                'written_dt': str(r['작성일'])[:10],
            }
        }, ensure_ascii=False) + '\n')

print(f'저장 완료: {len(sft)}건')