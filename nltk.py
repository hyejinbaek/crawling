# nltk 키워드 추출

import pandas as pd
import re
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# 데이터 로드
df = pd.read_excel("./keyword_final/combined_keyword_results.xlsx")


# reviews_text 컬럼에서 자주 등장하는 키워드 추출
reviews = df['reviews_text'].dropna().astype(str)  # NaN 값 제거 및 문자열 변환

# 텍스트 전처리 함수 정의
def preprocess_text(text):
    # 소문자로 변환 및 특수 문자 제거
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

# 모든 리뷰를 하나의 문자열로 결합
all_reviews = ' '.join(reviews.map(preprocess_text))

# 텍스트를 토큰화
tokens = word_tokenize(all_reviews)

# 불용어 제거
# 한국어는 불용어 데이터 제공하지 않음
# stop_words = set(stopwords.words('english') + stopwords.words('korean'))  # 필요 시 추가 언어 지원
stop_words = stopwords.words('english')
filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 1]  # 길이 제한

# 키워드 빈도 계산
keyword_counts = Counter(filtered_tokens)

# 상위 20개 키워드 출력
top_keywords = keyword_counts.most_common(100)
print("Top 20 Keywords:")
for keyword, count in top_keywords:
    print(f"{keyword}: {count}")
