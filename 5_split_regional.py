# 주소명 기반으로 지역명 분리
import pandas as pd

# 주소 데이터를 포함한 엑셀 파일 읽기
file_path = 'final_deduplicated.xlsx'  # 업로드한 엑셀 파일 경로
df = pd.read_excel(file_path)

# 주소를 지역1, 지역2, 지역3으로 나누는 함수
def split_address(address):
    parts = address.split()  # 공백 기준으로 분리
    region1 = parts[0] if len(parts) > 0 else None  # 예: 강원
    region2 = parts[1] if len(parts) > 1 else None  # 예: 강릉시
    region3 = " ".join(parts[2:]) if len(parts) > 2 else None  # 나머지 (예: 강변로 294 1층)
    return pd.Series([region1, region2, region3])

# 새로운 컬럼 추가
df[['지역1', '지역2', '지역3']] = df['주소'].apply(split_address)

# 결과를 새로운 엑셀 파일로 저장
output_file_path = 'test.xlsx'  # 저장할 파일 경로
df.to_excel(output_file_path, index=False)

print(f"분리된 결과가 '{output_file_path}'에 저장되었습니다.")
