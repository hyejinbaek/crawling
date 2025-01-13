파일 정보
1. keyword.xlsx : 크롤링 대상 전체 키워드
2. keywords_1.xlsx, keywords_2.xlsx, keywords_3.xlsx : 크롤링 대상 키워드 1/3씩 쪼갠 키워드(ip차단 이슈로 파일 분리)
3. naver_map_crawler.py : 전임자 코드
4. 0_data_crawling.py : 최종 크롤링 코드
5. 1_data_preprocessiong.py : 방문자 리뷰 컬럼 gpt를 이용하여 키워드 추출 (실패)
6. 2_reviews_postprcessing.py : 방문자 리뷰 컬럼 필터링 키워드 정하여 추출 (성공)
7. 3_final.py : 요청사항에 적합한 형태로 데이터 후처리
8. 4_deduplication.py : 상호/주소 중복 제거
9. 5_split_regional.py : 지역 1,2,3 분리
10. nltk.py : 방문자 리뷰 컬럼 키워드 빈도 분석(세차용품 관련 자주 등장하는 키워드 파악 위함)