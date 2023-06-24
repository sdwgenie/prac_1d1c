#!/usr/bin/env python
# coding: utf-8
import os
from pyvirtualdisplay import Display
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
import urllib.request
import requests
import time
import os
import pymysql
import datetime
import undetected_chromedriver as uc

days = ['https://opensea.io/rankings?sortBy=one_day_volume', 'https://opensea.io/rankings?sortBy=seven_day_volume', 'https://opensea.io/rankings?sortBy=thirty_day_volume', 'https://opensea.io/rankings?sortBy=total_volume']
chain = ['', '&chain=ethereum', '&chain=klaytn', '&chain=matic', '&chain=solana', '&chain=arbitrum', '&chain=avalanche', '&chain=optimism', '?chain=bsc']
nft = ['nft_24h', 'nft_7d', 'nft_30d', 'nft_at']
side = ['a_', 'e_', 'k_', 'p_', 's_', 'ar_', 'av_', 'o_', 'b_']
now_time = ['24H', '7D', '30D', 'AT']
poly = 'POLY'
arbit = 'ARBIT'
opt = 'OPT'

### 크롬 옵션 설정
#options = uc.ChromeOptions()
#options.add_argument('--no-sandbox')
#options.add_argument('--headless')
#options.add_argument('--window-size=1920,1080')
#options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36')
#options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/507.06 Safari/507.06")

### Pyvirtualdisplay
#Image.MAX_IMAGE_PIXELS = None
display = Display(visible = 0, size=(1920,1080))
display.start()

### Undetected Chrome
driver = uc.Chrome(version_main=104)
driver.maximize_window()
#driver.set_window_size(1900, 1200)

for tot in range(36):

    now = tot // 9
    no_w = tot % 9
        
    driver.implicitly_wait(2)
    time.sleep(3)
    
    n_time = datetime.datetime.now()
    date = n_time.strftime('%y%m%d%H')
    img_folder = './static/img/' + date + '_' + side[no_w] + now_time[now]
    #img_folder = './static/img/' + '220818' + str(tot) + '_' + side[no_w] + now_time[now]
    
    driver.get(days[now] + chain[no_w])
    driver.implicitly_wait(2)

    for re in range(5):
        
        try :
            end = 0
            temp = []
            info_list = []
            coin_list = []
            link_list = []
            img_list = []

            for i in range(11):

                ### 스크롤 조정
                start = end
                end = 850 * (i)
                driver.execute_script("window.scrollTo(%d, %d)" % (start, end))

                driver.implicitly_wait(2)
                time.sleep(5)

                #driver.save_screenshot('./test/%s%s_%s.png' % (side[no_w], re, i))

                cnt = 1

                ### 반응형 웹 필요 정보 스캔
                while True:
                    try:
                        #coin = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div[2]/a/div[2]/div/div/button' % (cnt))[0]
                        num = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[1]/div[1]/span/div' % (cnt))[0]
                        col = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[1]/div[3]/div/span/div/div' % (cnt))[0]
                        link = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a' % (cnt))[0]
                        vol = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[2]' % (cnt))[0].text
                        cha = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[3]' % (cnt))[0]
                        flo = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[4]' % (cnt))[0].text
                        sales = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[5]' % (cnt))[0]
                        owners = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[6]' % (cnt))[0].text.split('\n')
                        item = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[7]' % (cnt))[0].text.split('\n')
                        coin_list.append([int(num.text), vol.split()[1]])
                        link_list.append([int(num.text), link.get_attribute('href')])
                        
                        if len(flo.split()) == 3:
                            if owners[0][-1] != '%' and item[0][-1] != '%':
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[1], sales.text, '—', '—', '—', '—'])
        
                            elif owners[0][-1] != '%':
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[1], sales.text, '—', '—', item[0], item[1]])
        
                            elif item[0][-1] != '%':
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[1], sales.text, owners[0], owners[0], '—', '—'])
        
                            else:
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[1], sales.text, owners[0], owners[1], item[0], item[1]])
                        
                        else:
                            if owners[0][-1] != '%' and item[0][-1] != '%':
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[0], sales.text, '—', '—', '—', '—'])
        
                            elif owners[0][-1] != '%':
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[0], sales.text, '—', '—', item[0], item[1]])
        
                            elif item[0][-1] != '%':
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[0], sales.text, owners[0], owners[0], '—', '—'])
        
                            else:
                                info_list.append([int(num.text), col.text, vol.split()[0], cha.text, flo.split()[0], sales.text, owners[0], owners[1], item[0], item[1]])

                        cnt += 1

                    except:
                        break
              
                while cnt:
                    try :
                        num = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[1]/div[1]/span/div' % (cnt))[0]
                        img = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[1]/div[3]/div/div[6]/div[%s]/div/a/div[1]/div[2]/span/img' % (cnt))[0]
                        #print(img.get_attribute('srcset'))
                        #print(img.get_attribute('srcset').split(','))
                        if img.get_attribute('src')[0] == 'h':
                            img_list.append([int(num.text), img.get_attribute('src').split('?auto')[0] + '?auto=format&w=100'])
                            
                        cnt -= 1

                    except :
                        cnt -= 1
                        pass

            ### 중복 제거
            set_coin = set([tuple(i) for i in coin_list])
            coins = [list(i) for i in set_coin]

            set_info = set([tuple(i) for i in info_list])
            infos = [list(i) for i in set_info]

            set_link = set([tuple(i) for i in link_list])
            links = [list(i) for i in set_link]

            set_img = set([tuple(i) for i in img_list])
            imgs = [list(i) for i in set_img]

            ### 오류 제거
            err = []
            er = 0

            for i in range(len(infos)):
                if infos[i][0] == '':
                    err.append(i)
                    
                else:
                    infos[i][0] = int(infos[i][0])
                    
            for i in err:
                del infos[i-er]
                er +=1

            err = []
            err2 = []
            err3 = []
            er = 0
            cnt = 0
        
            for i, j in enumerate(imgs):
                err3.append(imgs[i][0])
                
                if j[1] == '':
                    err.append(i)
                    err2.append(j[0])

            for i in err2:
                if err3.count(i) == 2:
                    del imgs[err[cnt]-er]
                    cnt += 1
                    er += 1

            ### 순서 정렬
            info_sort = sorted(infos, key = lambda x : x[0])
            coin_sort = sorted(coins, key = lambda x : x[0])
            link_sort = sorted(links, key = lambda x : x[0])
            img_sort = sorted(imgs, key = lambda x : x[0])
            
            ### 이미지 저장
            if not os.path.isdir(img_folder):
                os.mkdir(img_folder)

            for i in range(len(info_sort)):
                try:
                    info_sort[i].append(coin_sort[i][1])
                    response = requests.get(img_sort[i][1])
                    image = Image.open(BytesIO(response.content)).convert('RGB')
                    image.info.pop('background', None)
                    image = image.resize((100,100))
                    image.save(img_folder + '/%s.gif' % (img_sort[i][0]), 'gif')
                except:
                    pass

            ### 정보 DB 저장
            conn = pymysql.connect(host = 'localhost', user = 'bizmeta', password = 'bmeta2044!!', db = 'bizmeta', charset = 'utf8mb4')
            cursor = conn.cursor()

            ### 당일 데이터 초기화
            sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
            sql2 = '''SET COLLECTION = NULL,
                        VOLUME = NULL,
                        CHANGE_ = NULL,
                        FLOOR_PRICE = NULL,
                        SALES = NULL,
                        OWNERS_PERCENT = NULL,
                        OWNERS = NULL,
                        ITEMS_PERCENT = NULL,
                        ITEMS = NULL,
                        COIN = NULL,
                        IMAGE = NULL,
                        LINK = NULL
                    WHERE RANKING = %s'''

            for i in range(100*re, 100*(re + 1) + 1):
                cursor.execute(sql + sql2, (i+1))
                if i >= 500:
                    break
            
            conn.commit()
            
            if (side[no_w] == 'p_'):
                sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                sql2 = '''SET COLLECTION = %s,
                            VOLUME = %s,
                            CHANGE_ = %s,
                            FLOOR_PRICE = %s,
                            SALES = %s,
                            OWNERS_PERCENT = %s,
                            OWNERS = %s,
                            ITEMS_PERCENT = %s,
                            ITEMS = %s,
                            COIN = %s,
                            IMAGE = %s,
                            LINK = %s
                        WHERE RANKING = %s'''

                for i in range(len(link_sort)):
                    cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], poly, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                conn.commit()

            elif (side[no_w] == 'ar_'):
                sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                sql2 = '''SET COLLECTION = %s,
                            VOLUME = %s,
                            CHANGE_ = %s,
                            FLOOR_PRICE = %s,
                            SALES = %s,
                            OWNERS_PERCENT = %s,
                            OWNERS = %s,
                            ITEMS_PERCENT = %s,
                            ITEMS = %s,
                            COIN = %s,
                            IMAGE = %s,
                            LINK = %s
                        WHERE RANKING = %s'''

                for i in range(len(link_sort)):
                    cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], arbit, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                conn.commit()

            elif (side[no_w] == 'o_'):
                sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                sql2 = '''SET COLLECTION = %s,
                            VOLUME = %s,
                            CHANGE_ = %s,
                            FLOOR_PRICE = %s,
                            SALES = %s,
                            OWNERS_PERCENT = %s,
                            OWNERS = %s,
                            ITEMS_PERCENT = %s,
                            ITEMS = %s,
                            COIN = %s,
                            IMAGE = %s,
                            LINK = %s
                        WHERE RANKING = %s'''

                for i in range(len(link_sort)):
                    cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], opt, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                conn.commit()

            else:
                sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                sql2 = '''SET COLLECTION = %s,
                            VOLUME = %s,
                            CHANGE_ = %s,
                            FLOOR_PRICE = %s,
                            SALES = %s,
                            OWNERS_PERCENT = %s,
                            OWNERS = %s,
                            ITEMS_PERCENT = %s,
                            ITEMS = %s,
                            COIN = %s,
                            IMAGE = %s,
                            LINK = %s
                        WHERE RANKING = %s'''

                for i in range(len(link_sort)):
                    cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], info_sort[i][10], (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                conn.commit()
            conn.close()

        ### 오류 발생시 리셋 후 데이터 입력
        except:
            conn = pymysql.connect(host = 'localhost', user = 'bizmeta', password = 'bmeta2044!!', db = 'bizmeta', charset = 'utf8mb4')
            cursor = conn.cursor()
            
            sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
            sql2 = '''SET COLLECTION = NULL,
                        VOLUME = NULL,
                        CHANGE_ = NULL,
                        FLOOR_PRICE = NULL,
                        SALES = NULL,
                        OWNERS_PERCENT = NULL,
                        OWNERS = NULL,
                        ITEMS_PERCENT = NULL,
                        ITEMS = NULL,
                        COIN = NULL,
                        IMAGE = NULL,
                        LINK = NULL
                    WHERE RANKING = %s'''

            for i in range(100*re, 100*(re + 1) + 1):
                cursor.execute(sql + sql2, (i+1))
                if i >= 500:
                    break
            
            conn.commit()
            
            if len(coin_list) :
                if (side[no_w] == 'p_'):
                    sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                    sql2 = '''SET COLLECTION = %s,
                                VOLUME = %s,
                                CHANGE_ = %s,
                                FLOOR_PRICE = %s,
                                SALES = %s,
                                OWNERS_PERCENT = %s,
                                OWNERS = %s,
                                ITEMS_PERCENT = %s,
                                ITEMS = %s,
                                COIN = %s,
                                IMAGE = %s,
                                LINK = %s
                            WHERE RANKING = %s'''

                    for i in range(len(link_sort)):
                        cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], poly, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                    conn.commit()

                elif (side[no_w] == 'ar_'):
                    sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                    sql2 = '''SET COLLECTION = %s,
                                VOLUME = %s,
                                CHANGE_ = %s,
                                FLOOR_PRICE = %s,
                                SALES = %s,
                                OWNERS_PERCENT = %s,
                                OWNERS = %s,
                                ITEMS_PERCENT = %s,
                                ITEMS = %s,
                                COIN = %s,
                                IMAGE = %s,
                                LINK = %s
                            WHERE RANKING = %s'''

                    for i in range(len(link_sort)):
                        cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], arbit, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                    conn.commit()

                elif (side[no_w] == 'o_'):
                    sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                    sql2 = '''SET COLLECTION = %s,
                                VOLUME = %s,
                                CHANGE_ = %s,
                                FLOOR_PRICE = %s,
                                SALES = %s,
                                OWNERS_PERCENT = %s,
                                OWNERS = %s,
                                ITEMS_PERCENT = %s,
                                ITEMS = %s,
                                COIN = %s,
                                IMAGE = %s,
                                LINK = %s
                            WHERE RANKING = %s'''

                    for i in range(len(link_sort)):
                        cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], opt, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                    conn.commit()
                
                else:
                    sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                    sql2 = '''SET COLLECTION = %s,
                                VOLUME = %s,
                                CHANGE_ = %s,
                                FLOOR_PRICE = %s,
                                SALES = %s,
                                OWNERS_PERCENT = %s,
                                OWNERS = %s,
                                ITEMS_PERCENT = %s,
                                ITEMS = %s,
                                COIN = %s,
                                IMAGE = %s,
                                LINK = %s
                            WHERE RANKING = %s'''

                    for i in range(len(link_sort)):
                        cursor.execute(sql + sql2, (info_sort[i][1], info_sort[i][2], info_sort[i][3], info_sort[i][4], info_sort[i][5], info_sort[i][6], info_sort[i][7], info_sort[i][8], info_sort[i][9], info_sort[i][10], (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], info_sort[i][0]))
                    conn.commit()
                conn.close()
            else :
                pass

        os.system('sh updating.sh')
        
        ### 페이지 이동
        try:
            driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[2]/button[2]/i')[0].click()
                                                         
        except:
            break

driver.close()
display.stop()




