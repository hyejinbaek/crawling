import pandas as pd
import re
import numpy as np

# 엑셀 파일 읽기
df1 = pd.read_excel("./keyword_final/combined_keyword_results.xlsx")
df2 = pd.read_excel("final.xlsx")


# 데이터 변환을 위한 새 데이터프레임 생성
new_data = pd.DataFrame()

# '구분' 컬럼 처리 함수 정의
def determine_category(row):
    file_part = row['source_file'].split('_')[1].split('.')[0]  # 'crawling_광택.xlsx'에서 '광택' 추출
    if file_part in ['광택', '디테일링', '손세차', '세차']:
        return '손세차장'
    elif file_part in ['주유소', '컴인워시', '노터치', '노브러시']:
        return '자동세차장'
    else:
        return None

new_data['구분'] = df1.apply(determine_category, axis=1)

# 나머지 컬럼 복사
new_data['키워드'] = df1['Keyword']
new_data['상호명'] = df1['Title']
new_data['주소'] = df1['Address']
new_data['전화번호'] = df1['number']
new_data['편의시설'] = df1['service']
new_data['영업일'] = df1['wk']
new_data['방문자리뷰(집계)'] = df1['keywords']
new_data['대표키워드'] = df1['info2']
new_data['홈'] = df1['info1']

# 'reviews_text'에 따라 '베이', '드라잉존', '디테일링', 'PPF'에 O, X 추가
new_data['베이'] = df1['reviews_text'].apply(lambda x: 'O' if '베이' in str(x) else 'X')
new_data['드라잉존'] = df1['reviews_text'].apply(lambda x: 'O' if '드라잉존' in str(x) else 'X')
new_data['디테일링'] = df1['reviews_text'].apply(lambda x: 'O' if '디테일링' in str(x) else 'X')
new_data['PPF'] = df1['reviews_text'].apply(lambda x: 'O' if 'PPF' in str(x) else 'X')

# info1 컬럼에서 URL을 찾고 '홈페이지' 컬럼에 추가
def extract_website(info):
    # URL 패턴 정의 (http, https, www URL 검출)
    url_pattern = re.compile(r'(https?://[^\s]+)|(www\.[^\s]+)')
    urls = url_pattern.findall(str(info))
    # 중첩된 튜플로 반환되므로 URL을 직접 추출
    urls = [url[0] or url[1] for url in urls if url[0] or url[1]]
    if urls:
        return ', '.join(urls)
    return None

new_data['홈페이지'] = df1['info1'].apply(extract_website)

# 변환된 데이터를 2번 파일에 덮어쓰기
new_data.to_excel('final.xlsx', index=False)
print("데이터가 변환되어 'final.xlsx'에 저장되었습니다.")