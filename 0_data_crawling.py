import time     
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import warnings
import os 
warnings.filterwarnings('ignore')


start = time.time() 

# 키워드 파일 읽어옴
df_f = pd.read_excel("./keyword.xlsx")

chrome_options = Options()
# chrome_options.add_argument('--headless')  # 헤드리스 모드
chrome_options.add_argument('--disable-gpu')  # GPU 비활성화 (윈도우용)
chrome_options.add_argument('--no-sandbox')  # 리눅스 환경에서 필요
chrome_options.add_argument('--disable-dev-shm-usage')  # 메모리 문제 해결
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window() #전체 화면 시행 

# 프레임 변경 
def switch_frame(frame_name):
    driver.switch_to.default_content()
    WebDriverWait(driver, 2).until(EC.frame_to_be_available_and_switch_to_it((By.ID, frame_name)))

# 스크롤 시행 
def page_down(num):
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    body.click()
    for _ in range(num):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)


# def load_all_reviews():
#     while True:
#         try:
#             # 적절한 선택자를 사용하여 "더보기" 버튼 찾기 (a 태그가 아니라 span 태그를 사용)
#             xpath4 = "//span[@class='TeItc' and contains(text(),'더보기')]"
#             load_more_button = driver.find_element(By.XPATH, xpath4)
            
#             # "더보기" 버튼으로 스크롤 및 클릭
#             driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
#             load_more_button.click()
            
#             # 새로운 리뷰가 로드될 시간을 기다림
#             time.sleep(2)
        
#         except NoSuchElementException:
#             # "더보기" 버튼이 없으면 루프를 빠져나옴
#             break
        
def load_reviews_with_limit(limit=5):
    count = 0  # 클릭 횟수 초기화
    while count < limit:
        try:
            # "더보기" 버튼 찾기
            xpath4 = "//span[@class='TeItc' and contains(text(),'더보기')]"
            load_more_button = driver.find_element(By.XPATH, xpath4)
            
            # "더보기" 버튼으로 스크롤 및 클릭
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            load_more_button.click()
            
            # 새로운 리뷰가 로드될 시간을 기다림
            time.sleep(2)
            
            count += 1  # 클릭 횟수 증가
        except NoSuchElementException:
            # "더보기" 버튼이 없으면 루프를 빠져나옴
            break

def save_to_excel(data, filename='key1.xlsx'):
    # 열 이름 정의 (data의 요소 개수와 일치해야 함)
    columns = ['Category', 'Keyword', 'Title', 'Address', 'number', 'service', 'wk', 'info1', 'info2', 'reviews_text']
    
    # 데이터 개수를 확인하여 누락된 값을 기본값으로 채우기
    for entry in data:
        while len(entry) < len(columns):
            entry.append("정보 없음")  # 누락된 값을 기본값으로 채움

    # 데이터프레임 생성
    df = pd.DataFrame(data, columns=columns)
    
    # 파일이 이미 존재하면 기존 데이터와 합치기
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
        # 중복 제거
        df['식별자'] = df['Title'] + df['Address']
        df = df.drop_duplicates(subset='식별자').drop(columns='식별자')

    # 파일 저장
    df.to_excel(filename, index=False, engine='openpyxl')

    
count = 1
total_t = []

# 검색키워드
for idx, v in enumerate(df_f['검색리스트'], start=1):
    keyword = f'{v}'
    if keyword == '':
        continue  
    else:
        url = f'https://map.naver.com/v5/search/{keyword}'
    driver.get(url)
    driver.refresh() 


    # 메인 프레임
    switch_frame('searchIframe') 

    # 소스, 파싱
    res = driver.page_source  
    soup = BeautifulSoup(res, 'html.parser')  
    time.sleep(0.5)

    # 페이지 구성
    next_btn = driver.find_elements(By.CSS_SELECTOR, '.zRM9F > a')  # 다음 페이지 버튼
    next_btn_len = len(driver.find_elements(By.CSS_SELECTOR, '.zRM9F > a[class*=mBN2s]')) # 다음페이지 수
    page = driver.find_elements(By.CSS_SELECTOR, '.YwYLL') # 업체수
    
    t_len = len(page)
    
    # 키워드 
    print(f' ===================================================== {v} =====================================================')
    
    # 페이지 반복 
    for case1 in range(len(next_btn)) : 
        try:
            page = driver.find_elements(By.CSS_SELECTOR, '.YwYLL')
            t_len = len(page)
            #==================================================================================================================     
            # 업체 없음
            if t_len == 0:
                break
            #==================================================================================================================        
            # 업체 한곳 
            if t_len == 1:
                switch_frame('entryIframe')
                time.sleep(0.5)
                
                res_s = driver.page_source
                soup_p = BeautifulSoup(res_s, 'html.parser')
                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="_title"]')))
   
    
                #---------------------------------------------------------------------------------------------------------------         
                # 수집 (홈탭)
                cate_f = ''
                title_s = soup_p.find('span', class_='GHAhO')
                title_f = title_s.text if title_s else "업체명 없음"
                print(f'업체명: {title_f}')
                
                addr_s = soup_p.find('span', class_='LDgIH')
                addr_f = addr_s.text if addr_s else "주소 없음"
                print(f'주소: {addr_f}')
                
                num_s = soup_p.find('span', class_='xlx7Q')
                num_f = num_s.text if num_s else "전화번호 없음"
                print(f'전화번호: {num_f}')
                
                site_s = soup_p.find('a', class_='place_bluelink CHmqa')
                site_f = site_s.text if site_s else "홈페이지 없음"
                print(f'홈페이지: {site_f}')
                
                ser_s = soup_p.find('span', class_='place_blind', string='편의')
                ser_f = ser_s.find_parent('div').find('div', class_='vV_z_').text if ser_s else "편의 없음"
                print(f'편의: {ser_f}')
                

                com = []
                try:
                    work_day_element = driver.find_element(By.CSS_SELECTOR, 'div.y6tNq')
                    if work_day_element.is_displayed():
                        work_day_element.click()
                        work_h = driver.find_elements(By.CSS_SELECTOR, 'div.y6tNq span.A_cdD')
                        for w_hh in work_h:
                            day = w_hh.find_element(By.CSS_SELECTOR, 'span.i8cJw').text
                            time_t = w_hh.find_element(By.CSS_SELECTOR, 'div.H3ua4').text
                            h_time = f'{day} {time_t}'
                            com.append(h_time)
                except NoSuchElementException:
                    com = ['정보 없음']
                print(f'영업시간: {com}')
                
            
                # 수집 (정보탭)                   
                try:
                    xpath2 = "//a[@class='tpj9w _tab-menu' and .//span[text()='정보']]"
                    
                    elements = driver.find_elements(By.XPATH, xpath2) # 정보탭이 없는 경우 존재
                    if elements:
                        # 스크롤 
                        driver.execute_script("arguments[0].scrollIntoView(true);", elements[0]) 
                        driver.execute_script("arguments[0].click();", elements[0]) 
                        
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="_title"]')))
                        
                        time.sleep(1)  
                        res_s2 = driver.page_source
                        soup_ppp = BeautifulSoup(res_s2, 'html.parser')

                        # 정보 
                        inf_s_l1 = soup_ppp.find_all('div', class_='T8RFa')
                        inf_t1 = [inf_s.text for inf_s in inf_s_l1 if inf_s]
                        inf_f1 = ' // '.join(inf_t1) if inf_t1 else "정보 없음"
                        print(f'정보: {inf_f1}')

                        # 대표키워드 
                        inf_s_l2 = soup_ppp.find_all('div', class_='FbEj5')
                        inf_t2 = [span.text for div in inf_s_l2 for span in div.find_all('span', class_='RLvZP') if span]
                        inf_f2 = ' // '.join(inf_t2) if inf_t2 else "정보 없음"
                        print(f'대표키워드: {inf_f2}')
                        
                    else:
                        inf_f1 = "정보 없음"
                        inf_f2 = "정보 없음"
                        print(f'정보: {inf_f1}')
                        print(f'대표키워드: {inf_f2}')

                except Exception as e:
                    inf_f1 = "정보 없음"
                    inf_f2 = "정보 없음"
                    print(f'정보: {inf_f1}')
                    print(f'대표키워드: {inf_f2}')
                    print(f"정보탭 클릭 오류: {e}")
                    pass
                
                # 수집 (리뷰)             
                try:
                    xpath3 = "//a[@class='tpj9w _tab-menu' and .//span[text()='리뷰']]"
                    elements = driver.find_elements(By.XPATH, xpath3)
                    print(" === elements === ", elements)
                    if elements:
                        # 스크롤
                        driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])  
                        driver.execute_script("arguments[0].click();", elements[0])  

                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="_title"]')))                  
                        
                        time.sleep(2)  # 추가 대기
                        page_down(3)
                        
                        res_reviews = driver.page_source
                        soup_reviews = BeautifulSoup(res_reviews, 'html.parser')
                        
                        # 리뷰 리스트 찾기
                        review_elements = soup_reviews.find_all('div', class_='pui__vn15t2')
                        reviews = [review.text.strip() for review in review_elements if review]
                        reviews_text = ' // '.join(reviews) if reviews else "리뷰 없음"
                        print(f'리뷰: {reviews_text}')

                except Exception as e:
                    inf_f1 = "정보 없음"
                    inf_f2 = "정보 없음"
                    print(f'정보: {inf_f1}')
                    print(f'대표키워드: {inf_f2}')
                    print(f"정보탭 클릭 오류: {e}")
                    pass
                
                
                switch_frame('searchIframe')
                time.sleep(0.5)
                
                
                total_t.append([ cate_f, keyword, title_f, addr_f, num_f, ser_f, com, inf_f1, inf_f2 ])
                save_to_excel(total_t)
                #---------------------------------------------------------------------------------------------------------------    
                
                
            #==================================================================================================================      
            # 업체 여러곳
            else : 
                # 스크롤 통해 마지막 업체까지 파싱 
                page_down(70) #70
                
                page = driver.find_elements(By.CSS_SELECTOR, '.YwYLL')
                cate = driver.find_elements(By.CLASS_NAME, 'YzBgS')
                t_len = len(page)
                print(f'> 페이지개수 :{t_len}')
                
                # 페이지당 업체수 가져오기 
                for case2 in range(t_len):
                    print(f'  >> {case2+1} 번째')
                    try:
                        element = page[case2]
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        WebDriverWait(driver, 2).until(EC.element_to_be_clickable(element))

                        cate_s = cate[case2]
                        cate_f = cate_s.text.strip() # 태그정보 
                        element_text = element.text.strip()

                        # 업체 클릭
                        element.click()
                        time.sleep(2)
                
                        # 클릭시 프레임 변경
                        switch_frame('entryIframe')
                        time.sleep(0.3)
                        
                        res_s = driver.page_source
                        soup_p = BeautifulSoup(res_s, 'html.parser')
                        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="_title"]')))

                    
                        # 정보 없을 시 다음
                        if not driver.find_element(By.XPATH, '//*[@id="_title"]').is_displayed():
                            continue
                    
        
                        #---------------------------------------------------------------------------------------------------------------                    
                        # 수집 (홈탭)

                        title_s = soup_p.find('span', class_='GHAhO')
                        title_f = title_s.text if title_s else "업체명 없음"
                        print(f'업체명: {title_f}')
                        
                        addr_s = soup_p.find('span', class_='LDgIH')
                        addr_f = addr_s.text if addr_s else "주소 없음"
                        print(f'주소: {addr_f}')
                        
                        num_s = soup_p.find('span', class_='xlx7Q')
                        num_f = num_s.text if num_s else "전화번호 없음"
                        print(f'전화번호: {num_f}')
                        
                        site_s = soup_p.find('a', class_='place_bluelink CHmqa')
                        site_f = site_s.text if site_s else "홈페이지 없음"
                        print(f'홈페이지: {site_f}')
                        
                        ser_s = soup_p.find('span', class_='place_blind', string='편의')
                        ser_f = ser_s.find_parent('div').find('div', class_='vV_z_').text if ser_s else "편의 없음"
                        print(f'편의: {ser_f}')
        
        
                        com = []
                        try:
                            work_day_element = driver.find_element(By.CSS_SELECTOR, 'div.y6tNq')
                            if work_day_element.is_displayed():
                                work_day_element.click()
                                work_h = driver.find_elements(By.CSS_SELECTOR, 'div.y6tNq span.A_cdD')
                                for w_hh in work_h:
                                    day = w_hh.find_element(By.CSS_SELECTOR, 'span.i8cJw').text
                                    time_t = w_hh.find_element(By.CSS_SELECTOR, 'div.H3ua4').text
                                    h_time = f'{day} {time_t}'
                                    com.append(h_time)
                        except NoSuchElementException:
                            com = ['정보 없음']
                        print(f'영업시간: {com}')

                        
                        # 수집 (정보탭)             
                        try:
                            xpath2 = "//a[@class='tpj9w _tab-menu' and .//span[text()='정보']]"
                            elements = driver.find_elements(By.XPATH, xpath2) # 정보탭이 없는 경우 존재
                            if elements:
                                # 스크롤
                                driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])  
                                driver.execute_script("arguments[0].click();", elements[0])  

                                WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="_title"]')))                  
                                
                                time.sleep(1)  # 추가 대기
                                res_s2 = driver.page_source
                                soup_ppp = BeautifulSoup(res_s2, 'html.parser')
    
                                # 정보 추출
                                inf_s_l1 = soup_ppp.find_all('div', class_='T8RFa')
                                inf_t1 = [inf_s.text for inf_s in inf_s_l1 if inf_s]
                                inf_f1 = ' // '.join(inf_t1) if inf_t1 else "정보 없음"
                                print(f'정보: {inf_f1}')

                                # 대표키워드 추출
                                inf_s_l2 = soup_ppp.find_all('div', class_='FbEj5')
                                inf_t2 = [span.text for div in inf_s_l2 for span in div.find_all('span', class_='RLvZP') if span]
                                inf_f2 = ' // '.join(inf_t2) if inf_t2 else "정보 없음"
                                print(f'대표키워드: {inf_f2}')
                                
                            else:
                                inf_f1 = "정보 없음"
                                inf_f2 = "정보 없음"
                                print(f'정보: {inf_f1}')
                                print(f'대표키워드: {inf_f2}')

                        except Exception as e:
                            inf_f1 = "정보 없음"
                            inf_f2 = "정보 없음"
                            print(f'정보: {inf_f1}')
                            print(f'대표키워드: {inf_f2}')
                            print(f"정보탭 클릭 오류: {e}")
                            pass
                        
                        # 수집 (리뷰)             
                        try:
                            xpath3 = "//a[@class='tpj9w _tab-menu' and .//span[text()='리뷰']]"
                            elements = driver.find_elements(By.XPATH, xpath3)

                            if elements:
                                # 리뷰 탭으로 스크롤 및 클릭
                                driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])
                                driver.execute_script("arguments[0].click();", elements[0])

                                WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="_title"]')))
                                
                                time.sleep(2)  # 추가 대기 시간
                                load_reviews_with_limit(limit=5)  # 리뷰를 5번 로드하는 함수 호출
                                
                                # 제한된 리뷰를 로드한 후 리뷰 요소 수집
                                res_reviews = driver.page_source
                                soup_reviews = BeautifulSoup(res_reviews, 'html.parser')
                                
                                # 리뷰 요소를 찾아 수집
                                review_elements = soup_reviews.find_all('div', class_='pui__vn15t2')
                                reviews = [review.text.strip() for review in review_elements if review]
                                reviews_text = ' // '.join(reviews) if reviews else "리뷰 없음"
                                print(f'리뷰: {reviews_text}')
                            else:
                                reviews_text = "정보 없음"
                                print(f'방문자 리뷰 2 : {reviews_text}')
                        except Exception as e:
                            reviews_text = "정보 없음"
                            print(f'방문자 리뷰: {reviews_text}')
                            print(f"정보탭 클릭 오류: {e}")
                        
                        
                        
                #=====================================================================================================================================================          
                        switch_frame('searchIframe')
                        time.sleep(0.5)
                    
                    
                    
                    except (TimeoutException, StaleElementReferenceException, AttributeError, IndexError, NoSuchElementException) as e:
                        print(f"error name: {e}") 
                        break
                    
    
                    total_t.append([cate_f, keyword, title_f, addr_f, num_f, ser_f, com, inf_f1, inf_f2, reviews_text])
                    save_to_excel(total_t)
                    
                
            # 페이지 이동
            try:
                next_btn = driver.find_elements(By.CSS_SELECTOR, '.zRM9F > a')
                next_btn_len = len(next_btn)  # next_btn의 길이 계산
                if page[-1]:  
                    count += 1
                    if next_btn_len < count: 
                        count = 1
                        break
                    elif next_btn_len == 1: 
                        break
                    elif next_btn_len > 0:  # 버튼이 존재할 경우에만 클릭
                        next_btn[-1].click()
                        time.sleep(2)
            except IndexError:
                print("더 이상 이동할 페이지가 없습니다.")
          
                
                
            except (TimeoutException, NoSuchElementException) as e:
                print(f'Error during pagination: {e}')
                break
             
        except (TimeoutException, NoSuchElementException) as e:
            print(f'Error during page processing: {e}')
            break
  
    

# 종료
driver.quit()

# 소요시간
e_time = time.time() - start
hours = e_time // 3600
r_seconds = e_time % 3600
minutes = r_seconds // 60
seconds = r_seconds % 60
print('[데이터 수집 완료]\n소요 시간:', (f"{int(hours)}시간 {int(minutes)}분 {int(seconds)}초"))


