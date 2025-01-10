import os
import openai
import pandas as pd
from dotenv import load_dotenv

# .env 파일을 불러와 환경 변수로 설정
load_dotenv()

# 환경 변수에서 API 키를 가져와 설정
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# 입력 텍스트 길이 제한
MAX_INPUT_LENGTH = 1000  # 텍스트 길이를 제한 (문자 수 기준)

# 텍스트를 자르는 함수
def truncate_text(text, max_length=MAX_INPUT_LENGTH):
    return text[:max_length] if len(text) > max_length else text

# OpenAI API를 통한 키워드 추출 요청
def extract_keywords(text):
    try:
        truncated_text = truncate_text(text)  # 텍스트 길이 제한
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 방문자 리뷰에서 세차, 청소와 같은 핵심 키워드를 추출해주는 역할을 한다."},
                {"role": "user", "content": f"다음 내용을 키워드로 추출해줘:\n\n{truncated_text}"}
            ],
            max_tokens=60,
            temperature=0.5
        )
        keywords = response.choices[0]['message']['content'].strip()
        return keywords
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# 데이터 프레임을 청크로 나누어 처리
def process_dataframe_in_chunks(df, chunk_size=100):
    chunks = [df.iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]
    processed_chunks = []
    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx + 1}/{len(chunks)}...")
        chunk['keywords'] = chunk['reviews_text'].apply(lambda x: extract_keywords(x) if pd.notna(x) else x)
        processed_chunks.append(chunk)
    return pd.concat(processed_chunks)

# 특정 폴더에 있는 모든 .xlsx 파일을 처리하고 결과를 하나의 파일로 저장하는 함수
def process_and_save_to_single_excel(folder_path, output_file, chunk_size=100):
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    all_dataframes = []

    for file in all_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_excel(file_path)
            
            # 리뷰 텍스트에서 키워드 추출
            if 'reviews_text' in df.columns:
                df_processed = process_dataframe_in_chunks(df, chunk_size=chunk_size)
                df_processed['source_file'] = file  # 원본 파일 이름 추가
                all_dataframes.append(df_processed)
            else:
                print(f"Error: 'reviews_text' column not found in {file}")
                continue

        except Exception as e:
            print(f"Error processing {file}: {e}")

    # 모든 데이터를 하나의 데이터프레임으로 합치기
    final_df = pd.concat(all_dataframes, ignore_index=True)
    final_df.to_excel(output_file, index=False)
    print(f"All data processed and saved to: {output_file}")

# 입력 폴더와 출력 파일 경로 설정
input_folder = 'crawling_final'
output_file = 'keyword_final/combined_keyword_results.xlsx'

# 파일 처리 및 저장 실행
process_and_save_to_single_excel(input_folder, output_file, chunk_size=100)
