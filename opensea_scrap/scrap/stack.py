import pymysql
from datetime import date, timedelta

nft = ['nft_24h', 'nft_7d', 'nft_30d', 'nft_at']
side = ['a_', 'e_', 'k_', 'p_', 's_', 'ar_', 'av_', 'o_', 'b_']
stack = '_stack'

conn = pymysql.connect(host = 'localhost', user = 'id', password = 'pass', db = 'id', charset = 'utf8')
cursor = conn.cursor()

for tot in range(36):
    
    now = tot // 8
    no_w = tot % 8

    cursor.execute('SELECT * FROM %s ORDER BY RANKING desc' % (side[no_w] + nft[now]))

    a = cursor.fetchone()

    a_list = list(a)

    weight = a_list[0] // 500

    cursor.execute('SELECT * FROM %s WHERE RANKING BETWEEN %s AND %s' % ((side[no_w] + nft[now]), 500*(weight-1)+1, 500*weight))

    a = cursor.fetchall()

    a_list = [ list(i) for i in a ]

    sql = '''INSERT INTO %s(RANKING, DATE_, COLLECTION, VOLUME, CHANGE_, FLOOR_PRICE, SALES, OWNERS_PERCENT, OWNERS, ITEMS_PERCENT, ITEMS, COIN) ''' % (side[no_w] + nft[now] + stack)
    sql2 = '''VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    sql3 = '''INSERT INTO %s(RANKING) ''' % (side[no_w] + nft[now] + stack)
    sql4 = '''VALUES (%s)'''

    for i in range(500*(weight-1), 500*weight):
        try :
            cursor.execute(sql + sql2, (a_list[i][0], date.today(), a_list[i][1], a_list[i][2], a_list[i][3], a_list[i][4], a_list[i][5], a_list[i][6], a_list[i][7], a_list[i][8], a_list[i][9], a_list[i][10]))
            #cursor.execute(sql + sql2, (a_list[i][0], date.today() - timedelta(days=1), a_list[i][1], a_list[i][2], a_list[i][3], a_list[i][4], a_list[i][5], a_list[i][6], a_list[i][7], a_list[i][8], a_list[i][9], a_list[i][10]))
        except :
            cursor.execute(sql3 + sql4, (a_list[i][0]))
        
    conn.commit()

conn.close()
