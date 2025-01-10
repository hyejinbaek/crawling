# 방문자 리뷰 데이터 키워드 분석 후처리

import pandas as pd
import re
import numpy as np


df = pd.read_excel("./keyword_final/combined_keyword_results.xlsx")
df.loc[df['info1'] == "정보 없음", 'keywords'] = "없음"


# 필터링할 키워드 리스트
target_keywords = ['세차', '프리미엄세차', '디테일링샵', '손세차', '썬팅', '틴팅', '신차패키지','랩핑']


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
