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
chrome_options.add_argument('--headless')  # 헤드리스 모드
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

# 턴 마다 수집 저장
def save_to_excel(data, filename='key1.xlsx'):
    df = pd.DataFrame(data, columns=['Category', 'Keyword', 'Title', 'Address', 'number','service','wk','info1','info2'])
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
        df['식별자'] = df['Title'] + df['Address']
        df = df.drop_duplicates(subset='식별자').drop(columns='식별자')
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
                        
                        
                        
                #=====================================================================================================================================================          
                        switch_frame('searchIframe')
                        time.sleep(0.5)
                    
                    
                    
                    except (TimeoutException, StaleElementReferenceException, AttributeError, IndexError, NoSuchElementException) as e:
                        print(f"error name: {e}") 
                        break
                    
    
                    total_t.append([ cate_f, keyword, title_f, addr_f, num_f, ser_f, com, inf_f1, inf_f2 ])
                    save_to_excel(total_t)
                
            # 페이지 이동 
            try:
                next_btn = driver.find_elements(By.CSS_SELECTOR, '.zRM9F > a')
                if page[-1]:  
                    count += 1
                    if next_btn_len < count : 
                        count = 1
                        break
                    elif next_btn_len == 1 : 
                        break
                    else : 
                        next_btn[-1].click()
                        time. sleep(2)
          
                
                
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


