# 세차장 중복 제거
import pandas as pd

# 엑셀 파일 읽기
file_path = "final.xlsx"  # 파일 경로를 입력하세요
df = pd.read_excel(file_path)

# 중복된 '상호명'과 '주소'를 기준으로 첫 번째 행만 유지
df_deduplicated = df.drop_duplicates(subset=['상호명', '주소'], keep='first')

# 중복 제거된 데이터 저장
output_path = "final_deduplicated.xlsx"  # 결과를 저장할 경로
df_deduplicated.to_excel(output_path, index=False)

print("중복 제거 완료. 결과가 저장되었습니다:", output_path)
