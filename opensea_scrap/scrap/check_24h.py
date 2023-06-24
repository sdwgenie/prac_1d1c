#!/usr/bin/env python
# coding: utf-8
import os
from pyvirtualdisplay import Display
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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

days = ['https://opensea.io/rankings?sortBy=one_day_volume']
chain = ['&chain=klaytn', '&chain=ethereum']
nft = ['nft_24h']
side = ['k_', 'e_']
now_time = ['24H']
poly = 'POLY logo'

# options = uc.ChromeOptions()
# options.add_argument('--no-sandbox')
# options.add_argument('--headless')
# options.add_argument('--window-size=1920,1080')
# options.add_argument('--disable-gpu')
# options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36')

for tot in range(2):
    now = tot // 5
    no_w = tot % 5

    conn = pymysql.connect(host = 'localhost', user = 'bizmeta', password = 'bmeta2044!!', db = 'bizmeta', charset = 'utf8')

    cursor = conn.cursor()

    cursor.execute('SELECT * FROM %s WHERE RANKING BETWEEN 1 AND 100' % (side[no_w] + nft[now]))
                
    a = cursor.fetchone()

    if a[1] is None:

        conn.close()

        display = Display(visible = 0, size=(1280,1024))
        display.start()

        driver = uc.Chrome(version_main=104)
        driver.maximize_window()

        driver.implicitly_wait(2)
        time.sleep(3)
        
        n_time = datetime.datetime.now()
        date = n_time.strftime('%y%m%d%H')
        img_folder = './static/img/' + date + '_' + side[no_w] + now_time[now]
        driver.get(days[now] + chain[no_w])
        driver.implicitly_wait(2)

        for re in range(5):
            
            try :
                end = 0
                target_list = []; temp = []
                coin_list = []
                link_list = []
                img_list = []

                for i in range(11):
                    
                    start = end
                    end = 850*(i)
                    driver.execute_script("window.scrollTo(%d, %d)" % (start, end)) 

                    target = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[2]/div/div[3]')[0] 
                    
                    tar = target.text.split('\n')

                    driver.implicitly_wait(2)

                    for j in range(len(tar)):
                        if j % 8 == 0 and j != 0:
                            target_list.append(temp)
                            temp = []

                        if j == len(tar)-1:
                            target_list.append(temp)

                        temp.append(tar[j])

                    temp = []    
                    cnt = 1

                    while True:
                        try:
                            coin = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[2]/div/div[3]/div[%s]/a/div[2]/div/div/button' % (cnt))[0]
                            num = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[2]/div/div[3]/div[%s]/a/div[1]/div[1]/span/div' % (cnt))[0]
                            link = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[2]/div/div[3]/div[%s]/a' % (cnt))[0]
                            coin_list.append([int(num.text), coin.get_attribute('aria-label')])
                            link_list.append([int(num.text), link.get_attribute('href')])
                            cnt += 1

                        except:
                            break

                    time.sleep(2)

                    while cnt:
                        try :
                            num = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[2]/div/div[3]/div[%s]/a/div[1]/div[1]/span/div' % (cnt))[0]
                            img = driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[2]/div/div[3]/div[%s]/a/div[1]/div[2]/div[1]/div/img' % (cnt))[0]
                            img_list.append([int(num.text), img.get_attribute('src')])
                            cnt -= 1

                        except :
                            img_list.append([int(num.text), ''])
                            cnt -= 1
                            pass
                
                set_coin = set([tuple(i) for i in coin_list])
                coins = [list(i) for i in set_coin]

                set_rank = set([tuple(i) for i in target_list])
                ranks = [list(i) for i in set_rank]

                set_link = set([tuple(i) for i in link_list])
                links = [list(i) for i in set_link]

                set_img = set([tuple(i) for i in img_list])
                imgs = [list(i) for i in set_img]

                err = []
                er = 0
                
                for i in range(len(ranks)):
                    if ranks[i][0] == '':
                        err.append(i)
                    else:
                        ranks[i][0] = int(ranks[i][0])
                        
                for i in err:
                    del ranks[i-er]
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

                rank_sort = sorted(ranks, key = lambda x : x[0])
                coin_sort = sorted(coins, key = lambda x : x[0])
                link_sort = sorted(links, key = lambda x : x[0])
                img_sort = sorted(imgs, key = lambda x : x[0])

                print(len(rank_sort))
                print(len(link_sort))
                print(len(img_sort))

                if not os.path.isdir(img_folder):
                    os.mkdir(img_folder)

                for i in range(len(rank_sort)):
                    try:
                        rank_sort[i].append(coin_sort[i][1])
                        response = requests.get(img_sort[i][1])
                        image = Image.open(BytesIO(response.content))
                        image = image.resize((100,100))
                        image.save(img_folder + '/%s.png' % (img_sort[i][0]), 'png')
                    except:
                        pass
                
                conn = pymysql.connect(host = 'localhost', user = 'bizmeta', password = 'bmeta2044!!', db = 'bizmeta', charset = 'utf8')
                cursor = conn.cursor()
                
                sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                sql2 = '''SET COLLECTION = NULL,
                            VOLUME = NULL,
                            24H = NULL,
                            7D = NULL,
                            FLOOR_PRICE = NULL,
                            OWNERS = NULL,
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
                                24H = %s,
                                7D = %s,
                                FLOOR_PRICE = %s,
                                OWNERS = %s,
                                ITEMS = %s,
                                COIN = %s,
                                IMAGE = %s,
                                LINK = %s
                            WHERE RANKING = %s'''

                    for i in range(len(link_sort)):
                        cursor.execute(sql + sql2, (rank_sort[i][1], rank_sort[i][2], rank_sort[i][3], rank_sort[i][4], rank_sort[i][5], rank_sort[i][6], rank_sort[i][7], poly, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], rank_sort[i][0]))
                    conn.commit()
                
                else:
                    sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                    sql2 = '''SET COLLECTION = %s,
                                VOLUME = %s,
                                24H = %s,
                                7D = %s,
                                FLOOR_PRICE = %s,
                                OWNERS = %s,
                                ITEMS = %s,
                                COIN = %s,
                                IMAGE = %s,
                                LINK = %s
                            WHERE RANKING = %s'''

                    for i in range(len(link_sort)):
                        cursor.execute(sql + sql2, (rank_sort[i][1], rank_sort[i][2], rank_sort[i][3], rank_sort[i][4], rank_sort[i][5], rank_sort[i][6], rank_sort[i][7], rank_sort[i][8], (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], rank_sort[i][0]))
                    conn.commit()
                conn.close()
                    
            except:
                conn = pymysql.connect(host = 'localhost', user = 'bizmeta', password = 'bmeta2044!!', db = 'bizmeta', charset = 'utf8')
                cursor = conn.cursor()

                sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                sql2 = '''SET COLLECTION = NULL,
                            VOLUME = NULL,
                            24H = NULL,
                            7D = NULL,
                            FLOOR_PRICE = NULL,
                            OWNERS = NULL,
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
                                    24H = %s,
                                    7D = %s,
                                    FLOOR_PRICE = %s,
                                    OWNERS = %s,
                                    ITEMS = %s,
                                    COIN = %s,
                                    IMAGE = %s,
                                    LINK = %s
                                WHERE RANKING = %s'''

                        for i in range(len(link_sort)):
                            cursor.execute(sql + sql2, (rank_sort[i][1], rank_sort[i][2], rank_sort[i][3], rank_sort[i][4], rank_sort[i][5], rank_sort[i][6], rank_sort[i][7], poly, (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], rank_sort[i][0]))
                        conn.commit()
                    
                    else:
                        sql = '''UPDATE %s\n''' % (side[no_w] + nft[now])
                        sql2 = '''SET COLLECTION = %s,
                                    VOLUME = %s,
                                    24H = %s,
                                    7D = %s,
                                    FLOOR_PRICE = %s,
                                    OWNERS = %s,
                                    ITEMS = %s,
                                    COIN = %s,
                                    IMAGE = %s,
                                    LINK = %s
                                WHERE RANKING = %s'''

                        for i in range(len(link_sort)):
                            cursor.execute(sql + sql2, (rank_sort[i][1], rank_sort[i][2], rank_sort[i][3], rank_sort[i][4], rank_sort[i][5], rank_sort[i][6], rank_sort[i][7], rank_sort[i][8], (img_folder[1:] + '/' + str(img_sort[i][0]) + '.png'), link_sort[i][1], rank_sort[i][0]))
                        conn.commit()
                    conn.close()
                else :
                    pass

            
            os.system('sh updating.sh')
            
            try:
              driver.find_elements(by = By.XPATH, value = '//*[@id="main"]/div/div[3]/button[2]/i')[0].click()
              
            except:
              break
                
            driver.implicitly_wait(2)

        driver.close()
        display.stop()

    else :
        conn.close()
        pass




