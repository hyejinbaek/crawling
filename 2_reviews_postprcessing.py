# 방문자 리뷰 데이터 키워드 분석 후처리

import pandas as pd
import re
import numpy as np


df = pd.read_excel("./keyword_final/combined_keyword_results.xlsx")
df.loc[df['info1'] == "정보 없음", 'keywords'] = "없음"

# '[' 및 ']'를 제거하고자 하는 컬럼 이름을 설정합니다.
column_name = 'wk'

# 해당 열의 각 값에서 '[' 및 ']'를 제거합니다.
df[column_name] = df[column_name].str.replace('[', '').str.replace(']', '')
df[column_name] = df[column_name].str.replace('\'', '')

df['info1'] = df['info1'].str.replace('[', '').str.replace(']', '')

# 수정된 데이터를 확인하고 싶으면 다음과 같이 출력할 수 있습니다.
print(df[column_name])

print(df['reviews_text'])

# 필터링할 키워드 리스트
target_keywords = ['세차', '세차스폰지', '세차글러브', '세차버킷', '워시버킷', '고압분사기', '호스노즐', '세차샴푸', '폼건샴푸', '드라잉타월', '세차타월', 
                '워터블레이드', '물기제거도구', '왁스', '퀵디테일러', '클레이바', '타이어광택제', '휠클리너', '휠브러시', '코팅제', '발수코팅제', '대시보드클리너', 
                '실내청소기', '차량용청소기', '가죽클리너', '가죽코팅제', '카펫클리너', '섬유클리너', '악취제거제', '방향제', '폴리셔', '연마제', '증기세척기', '차량커버', 
                '워시미트거치대', '세차브러시세트', '프리미엄세차', '디테일링샵', '손세차', '썬팅', '틴팅', '신차패키지','랩핑', '필름', '컴인워시', 'ppf', '프리미엄', '디테일링', '손세차']

# 각 행의 키워드를 필터링하는 함수
def filter_keywords(keywords):
    if isinstance(keywords, str):  # 문자열 확인
        # 개별 키워드를 분리하고, target_keywords에 존재하는 키워드만 남깁니다.
        filtered_keywords = [word.strip() for word in keywords.replace("\n", ",").split(",") if word.strip() in target_keywords]
        return ', '.join(filtered_keywords)
    return ''

# keywords 열을 필터링된 키워드로 갱신
df['filtered_keywords'] = df['keywords'].apply(filter_keywords)

# 변환된 데이터를 2번 파일에 덮어쓰기
df.to_excel('./keyword_final/result.xlsx', index=False)
print("데이터가 변환되어 'result.xlsx'에 저장되었습니다.")
