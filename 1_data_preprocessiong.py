import os
import openai
import pandas as pd
from dotenv import load_dotenv

# .env 파일을 불러와 환경 변수로 설정
load_dotenv()

# 환경 변수에서 API 키를 가져와 설정
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# 엑셀 파일 불러오기
original_file_path = 'crawling_result.xlsx'  # 원본 엑셀 파일 경로 설정
df = pd.read_excel(original_file_path)

# OpenAI API를 통한 키워드 추출 요청
def extract_keywords(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Extract key keywords from the following text:\n\n{text}"}
            ],
            max_tokens=60,
            temperature=0.5
        )
        keywords = response.choices[0]['message']['content'].strip()
        return keywords
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# 각 리뷰에 대해 키워드 추출하기
df['keywords'] = df['reviews_text'].apply(lambda x: extract_keywords(x) if pd.notna(x) else x)

# 새로운 파일 경로 지정
new_file_path = 'preprocessing.xlsx'  # 새로운 엑셀 파일 이름 설정

# 수정된 데이터프레임을 새로운 엑셀 파일로 저장
df.to_excel(new_file_path, index=False)