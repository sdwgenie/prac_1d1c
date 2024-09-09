import json
import pandas as pd
import numpy as np
import pymysql
import datetime
import math
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from .models import *

# Create your views here.
### Volume, Floor Price marketcap 라인 그래프
def line_chart(request):
    ti = "'e_nftmarketcap'"
    conn = pymysql.connect(host = 'localhost', user = 'id', password = 'pass', db = 'id', charset = 'utf8')
    cursor = conn.cursor()

    cursor.execute('SELECT UPDATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE table_name=%s' % (ti))
    a = cursor.fetchone()
    time = a[0]
    conn.close()

    mark = ENftmarketcap.objects.order_by('-id').values()
    std_vol_mar = ENftmarketcap.objects.filter(id=1).values('volume_marketcap')[0]['volume_marketcap']
    std_flo_mar = ENftmarketcap.objects.filter(id=1).values('floor_price_marketcap')[0]['floor_price_marketcap']
    volume_marketcap = []
    floor_price_marketcap = []
    date = []
    vol_mar_avg = 0
    flo_mar_avg = 0

    for i in mark:
        x = round(i['volume_marketcap'] / std_vol_mar * 1000, 2)
        y = round(i['floor_price_marketcap'] / std_flo_mar * 1000, 2)
        z = i['date_field'][0:2] + '-' + i['date_field'][2:4] + '-' + i['date_field'][4:6]
        volume_marketcap.insert(0, x)
        floor_price_marketcap.insert(0, y)
        date.insert(0, z)

    for i, j in zip(volume_marketcap, floor_price_marketcap):
        vol_mar_avg += i
        flo_mar_avg += j
    
    vol_mar_avg = vol_mar_avg / len(volume_marketcap)
    flo_mar_avg = flo_mar_avg / len(floor_price_marketcap)
    
    marketcapdict = {'volume' : volume_marketcap, 'floor_price' : floor_price_marketcap, 'date' : date, 'vol_mar_avg' : vol_mar_avg, 'flo_mar_avg' : flo_mar_avg, 'mainnet': 'Eth'}
    marketcapjson = json.dumps(marketcapdict)
    return render(request, 'line_chart.html', {'marketcapjson' : marketcapjson, 'time' : time, 'mainnet': 'Ethereum' })
    
### Daily Volume Histogram
def v_histo(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('volume')
    volume = []

    for i in mark:
        value = ''
        if i['volume'] == '---' or i['volume'] is None:
            pass
            
        else:
            for j in i['volume'].split(','):
                value += j

            if value[-1] == 'K':
                volume.append(float(value[:-1])*1000)

            elif value[-1] == 'M':
                volume.append(float(value[:-1])*1000000)

            else :
                volume.append(float(value))

    gap = max(volume) / 50
    
    volumedict = {'volume' : volume, 'gap' : gap, 'mainnet': 'Eth'}
    volumejson = json.dumps(volumedict)
    return render(request, 'v_histo.html', {'volumejson' : volumejson, 'mainnet': 'Ethereum'})

### Daily Floor Price Histogram
def f_histo(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('floor_price')
    floor_price = []

    for i in mark:
        value = ''
        
        if i['floor_price'] == '---' or i['floor_price'] is None or i['floor_price'] == '—' :
            pass

        elif i['floor_price'][0] == '<':
            value += '0.01'
            floor_price.append(float(value))

        else:
            for j in i['floor_price'].split(','):
                value += j

            if value[-1] == 'K':
                floor_price.append(float(value[:-1])*1000)

            elif value[-1] == 'M':
                floor_price.append(float(value[:-1])*1000000)

            else :
                floor_price.append(float(value))

    gap = max(floor_price) / 50
    
    floor_pricedict = {'floor_price' : floor_price, 'gap' : gap, 'mainnet': 'Eth'}
    floor_pricejson = json.dumps(floor_pricedict)
    return render(request, 'f_histo.html', {'floor_pricejson' : floor_pricejson, 'mainnet': 'Ethereum'})

### Daily Volume Box Graph During 7 Days
def v_box(request):
    mark = ENftmarketcap.objects.order_by('-id').values('date_field')[:10]
    date = []

    for i in mark:
        z = i['date_field'][0:2] + '-' + i['date_field'][2:4] + '-' + i['date_field'][4:6]
        date.insert(0, z)

    now = datetime.datetime.now().time()

    if int(str(now)[0:2]) >= 14 or int(str(now)[0:2]) < 2:
        mark = ENft24HStack.objects.order_by('-id').values('volume')[:5000]
        volume = []
        volume2 = []
       
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['volume'] == '---' or mark[j]['volume'] is None :
                    volume.insert(0, 0)
                    
                else:
                    for j in mark[j]['volume'].split(','):
                        value += j

                    if value[-1] == 'K':
                        value = float(value[:-1])*1000

                    elif value[-1] == 'M':
                        value = float(value[:-1])*1000000

                    else :
                        value = float(value)

                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

    else :
        mark = ENft24HStack.objects.order_by('-id').values('volume')[:4500]
        mark2 = ENft24H.objects.values('volume')
        volume = []
        volume2 = []
       
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['volume'] == '---' or mark[j]['volume'] is None :
                    volume.insert(0, 0)
                    
                else:
                    for j in mark[j]['volume'].split(','):
                        value += j

                    if value[-1] == 'K':
                        value = float(value[:-1])*1000

                    elif value[-1] == 'M':
                        value = float(value[:-1])*1000000

                    else :
                        value = float(value)

                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

        for i in range(100):
            value = ''
            if mark2[i]['volume'] == '---' or mark2[i]['volume'] is None :
                volume.append(0)
                
            else:
                for j in mark2[i]['volume'].split(','):
                    value += j

                if value[-1] == 'K':
                    value = float(value[:-1])*1000

                elif value[-1] == 'M':
                    value = float(value[:-1])*1000000

                else :
                    value = float(value)
                    
                volume.append(float(value))
                volume2.append([len(mark)//500, float(value)])

    num = pd.Series(volume)

    for i in range(len(num)):
        if num[i] == 0:
            num[i] = np.NaN
        else:
            pass

    box = []
    
    for i in range(len(volume)//100):
        if math.isnan(num[100*i : 100*(i+1)].min()):
            box.append([0,0,0,0,0])
        else:
            box.append([num[100*i : 100*(i+1)].min(skipna=True), num[100*i : 100*(i+1)].quantile(.25), num[100*i : 100*(i+1)].mean(skipna=True), num[100*i : 100*(i+1)].quantile(.75), num[100*i : 100*(i+1)].max(skipna=True)])


    boxdict = {'box' : box, 'volume' : volume2, 'date' : date, 'mainnet': 'Eth'}
    boxjson = json.dumps(boxdict)
    return render(request, 'v_box.html', {'boxjson' : boxjson, 'mainnet': 'Ethereum'})

### Daily Floor Price Box Graph During 7 Days
def f_box(request):
    mark = ENftmarketcap.objects.order_by('-id').values('date_field')[:10]
    date = []
    
    for i in mark:
        z = i['date_field'][0:2] + '-' + i['date_field'][2:4] + '-' + i['date_field'][4:6]
        date.insert(0, z)

    now = datetime.datetime.now().time()

    if int(str(now)[0:2]) >= 14 or int(str(now)[0:2]) < 2:
        mark = ENft24HStack.objects.order_by('-id').values('floor_price')[:5000]
        volume = []
        volume2 = []
        
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['floor_price'] == '---' or mark[j]['floor_price'] is None or mark[j]['floor_price'] == '—' :
                    volume.insert(0, 0)

                elif mark[j]['floor_price'][0] == '<':
                    value += '0.01'
                    volume.insert(0, float(value))
                    
                else:
                    for j in mark[j]['floor_price'].split(','):
                        value += j
                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

    else :
        mark = ENft24HStack.objects.order_by('-id').values('floor_price')[:4500]
        mark2 = ENft24H.objects.values('floor_price')
        volume = []
        volume2 = []
       
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['floor_price'] == '---' or mark[j]['floor_price'] is None or mark[j]['floor_price'] == '—' :
                    volume.insert(0, 0)

                elif mark[j]['floor_price'][0] == '<':
                    value += '0.01'
                    volume.insert(0, float(value))
                    
                else:
                    for j in mark[j]['floor_price'].split(','):
                        value += j
                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

        for i in range(100):
            value = ''
            if mark2[i]['floor_price'] == '---' or mark2[i]['floor_price'] is None or mark2[i]['floor_price'] == '—' :
                volume.append(0)

            elif mark2[i]['floor_price'][0] == '<':
                value += '0.01'
                volume.append(float(value))
                volume2.append([len(mark)//500, float(value)])
                
            else:
                for j in mark2[i]['floor_price'].split(','):
                    value += j
                volume.append(float(value))
                volume2.append([len(mark)//500, float(value)])

    num = pd.Series(volume)

    for i in range(len(num)):
        if num[i] == 0:
            num[i] = np.NaN
        else:
            pass
    
    box = []

    for i in range(len(volume)//100):
        if math.isnan(num[100*i : 100*(i+1)].min()):
            box.append([0,0,0,0,0])
        else:
            box.append([num[100*i : 100*(i+1)].min(skipna=True), num[100*i : 100*(i+1)].quantile(.25), num[100*i : 100*(i+1)].mean(skipna=True), num[100*i : 100*(i+1)].quantile(.75), num[100*i : 100*(i+1)].max(skipna=True)])


    boxdict = {'box' : box, 'volume' : volume2, 'date' : date, 'mainnet': 'Eth'}
    boxjson = json.dumps(boxdict)
    return render(request, 'f_box.html', {'boxjson' : boxjson, 'mainnet': 'Ethereum'})

### Daily Volume Pie Chart
def v_pie(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('collection', 'volume')
    volume = ENftmarketcap.objects.order_by('-id').values('volume_total')[0]
    piedict={}
    tnt = 0
    for i in range(100):
        value = ''
        markdict={}
        if mark[i]['volume'] == '---' or mark[i]['volume'] is None :
            pass
        else:
            for j in mark[i]['volume'].split(','):
                value += j

            if value[-1] == 'K':
                value = float(value[:-1])*1000

            elif value[-1] == 'M':
                value = float(value[:-1])*1000000

            else :
                value = float(value)
        
        if i < 10:
            markdict['collection'] = mark[i]['collection']
            value = float(value) / volume['volume_total'] * 100
            tnt += value
            markdict['per'] = value
            piedict[str(i+1)] = markdict

        else :
            pass
    
    tnt = 100 - tnt
    piedict['etc'] = {'collection' : 'etc', 'per' : tnt, 'mainnet': 'Eth'}
    piejson = json.dumps(piedict)
    return render(request, 'v_pie.html', {'piejson' : piejson, 'mainnet': 'Ethereum'})

### Daily Floor Price Pie Chart
def f_pie(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('collection', 'floor_price')
    pri = []
    ind = []
    for i in range(100):
        value = ''
        if mark[i]['floor_price'] == '---' or mark[i]['floor_price'] is None or mark[i]['floor_price'] == '—':
            pri.append([i, 0])

        elif mark[i]['floor_price'][0] == '<':
            value += '0.01'
            pri.append([i, float(value)])

        else:
            for j in mark[i]['floor_price'].split(','):
                value += j

            if value[-1] == 'K':
                value = float(value[:-1])*1000

            elif value[-1] == 'M':
                value = float(value[:-1])*1000000

            else :
                value = float(value)

            pri.append([i, float(value)])

    price = sorted(pri, key = lambda x : -x[1])

    for i in range(10):
        ind.append(price[i][0])

    volume = ENftmarketcap.objects.order_by('-id').values('floor_price_total')[0]
    piedict={}
    tnt = 0

    for i in range(len(ind)):
        value = ''
        markdict={}

        if mark[ind[i]]['floor_price'][0] == '<':
            value += '0.01'

        else:
            for j in mark[ind[i]]['floor_price'].split(','):
                value += j

            if value[-1] == 'K':
                value = float(value[:-1])*1000

            elif value[-1] == 'M':
                value = float(value[:-1])*1000000

            else :
                value = float(value)

        markdict['collection'] = mark[ind[i]]['collection']
        value = float(value) / volume['floor_price_total'] * 100
        markdict['per'] = value
        tnt += float(value)
        piedict[str(i+1)] = markdict
    
    tnt = 100 - tnt
    piedict['etc'] = {'collection' : 'etc', 'per' : tnt, 'mainnet': 'Eth'}
    piejson = json.dumps(piedict)
    return render(request, 'f_pie.html', {'piejson' : piejson, 'mainnet': 'Ethereum'})

### Daily Increase / Decrease Ratio
def change(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('change_field')
    cnt = 0
    for i in range(100):
        if mark[i]['change_field'] == '---' or mark[i]['change_field'] is None or mark[i]['change_field'] == '—':
            pass

        elif mark[i]['change_field'][0:1] == '+':
            cnt += 1

    inc = cnt
    dec = 100 - inc
    changedict = { 'inc' : inc, 'dec' : dec, 'mainnet': 'Eth' }
    changejson = json.dumps(changedict)
    return render(request, 'change.html', {'changejson' : changejson, 'mainnet': 'Ethereum'})

### Volume Marketcap
def v_mark(request):
    ti = "'e_nftmarketcap'"
    conn = pymysql.connect(host = 'localhost', user = 'id', password = 'pass', db = 'id', charset = 'utf8')
    cursor = conn.cursor()

    cursor.execute('SELECT UPDATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE table_name=%s' % (ti))
    a = cursor.fetchone()
    time = a[0]
    conn.close()

    mark = ENftmarketcap.objects.values()
    std_vol_mar = ENftmarketcap.objects.filter(id=1).values('volume_marketcap')[0]['volume_marketcap']
    e_nftmarketcap = []

    for i in range(len(mark)):
        e_dict = {}
        if i == len(mark)-1:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_dict["close"] = round(mark[i]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)

        else:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_dict["close"] = round(mark[i+1]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)
    
    marketcapdict = {'marketcap' : e_nftmarketcap, 'mainnet': 'Eth'}
    marketcapjson = json.dumps(marketcapdict)
    return render(request, 'v_mark.html', {'marketcapjson' : marketcapjson, 'time' : time, 'mainnet': 'Ethereum'})

### Floor Price Marketcap
def f_mark(request):
    mark = ENftmarketcap.objects.values()
    std_flo_mar = ENftmarketcap.objects.filter(id=1).values('floor_price_marketcap')[0]['floor_price_marketcap']
    e_nftmarketcap = []

    for i in range(len(mark)):
        e_dict = {}
        if i == len(mark)-1:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_dict["close"] = round(mark[i]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)

        else:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_dict["close"] = round(mark[i+1]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)
    
    marketcapdict = {'marketcap' : e_nftmarketcap, 'mainnet': 'Eth'}
    marketcapjson = json.dumps(marketcapdict)
    return render(request, 'f_mark.html', {'marketcapjson' : marketcapjson, 'mainnet': 'Ethereum'})

### Mobile 반응형
def mline_chart(request):
    ti = "'e_nftmarketcap'"
    conn = pymysql.connect(host = 'localhost', user = 'id', password = 'pass', db = 'id', charset = 'utf8')
    cursor = conn.cursor()

    cursor.execute('SELECT UPDATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE table_name=%s' % (ti))
    a = cursor.fetchone()
    time = a[0]
    conn.close()

    mark = ENftmarketcap.objects.order_by('-id').values()
    std_vol_mar = ENftmarketcap.objects.filter(id=1).values('volume_marketcap')[0]['volume_marketcap']
    std_flo_mar = ENftmarketcap.objects.filter(id=1).values('floor_price_marketcap')[0]['floor_price_marketcap']
    volume_marketcap = []
    floor_price_marketcap = []
    date = []
    vol_mar_avg = 0
    flo_mar_avg = 0

    for i in mark:
        x = round(i['volume_marketcap'] / std_vol_mar * 1000, 2)
        y = round(i['floor_price_marketcap'] / std_flo_mar * 1000, 2)
        z = i['date_field'][0:2] + '-' + i['date_field'][2:4] + '-' + i['date_field'][4:6]
        volume_marketcap.insert(0, x)
        floor_price_marketcap.insert(0, y)
        date.insert(0, z)

    for i, j in zip(volume_marketcap, floor_price_marketcap):
        vol_mar_avg += i
        flo_mar_avg += j
    
    vol_mar_avg = vol_mar_avg / len(volume_marketcap)
    flo_mar_avg = flo_mar_avg / len(floor_price_marketcap)
    
    marketcapdict = {'volume' : volume_marketcap, 'floor_price' : floor_price_marketcap, 'date' : date, 'vol_mar_avg' : vol_mar_avg, 'flo_mar_avg' : flo_mar_avg, 'mainnet': 'Eth'}
    marketcapjson = json.dumps(marketcapdict)
    return render(request, 'mline_chart.html', {'marketcapjson' : marketcapjson, 'time' : time, 'mainnet': 'Ethereum' })

def mchange(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('change_field')
    cnt = 0
    for i in range(100):
        if mark[i]['change_field'] == '---' or mark[i]['change_field'] is None or mark[i]['change_field'] == '—':
            pass

        elif mark[i]['change_field'][0:1] == '+':
            cnt += 1
            
    inc = cnt
    dec = 100 - inc
    changedict = { 'inc' : inc, 'dec' : dec, 'mainnet': 'Eth' }
    changejson = json.dumps(changedict)
    return render(request, 'mchange.html', {'changejson' : changejson, 'mainnet': 'Ethereum'})

def mv_box(request):
    mark = ENftmarketcap.objects.order_by('-id').values('date_field')[:10]
    date = []

    for i in mark:
        z = i['date_field'][0:2] + '-' + i['date_field'][2:4] + '-' + i['date_field'][4:6]
        date.insert(0, z)

    now = datetime.datetime.now().time()

    if int(str(now)[0:2]) >= 14 or int(str(now)[0:2]) < 2:
        mark = ENft24HStack.objects.order_by('-id').values('volume')[:5000]
        volume = []
        volume2 = []
       
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['volume'] == '---' or mark[j]['volume'] is None :
                    volume.insert(0, 0)
                    
                else:
                    for j in mark[j]['volume'].split(','):
                        value += j

                    if value[-1] == 'K':
                        value = float(value[:-1])*1000

                    elif value[-1] == 'M':
                        value = float(value[:-1])*1000000

                    else :
                        value = float(value)
                        
                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

    else :
        mark = ENft24HStack.objects.order_by('-id').values('volume')[:4500]
        mark2 = ENft24H.objects.values('volume')
        volume = []
        volume2 = []
       
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['volume'] == '---' or mark[j]['volume'] is None :
                    volume.insert(0, 0)
                    
                else:
                    for j in mark[j]['volume'].split(','):
                        value += j

                    if value[-1] == 'K':
                        value = float(value[:-1])*1000

                    elif value[-1] == 'M':
                        value = float(value[:-1])*1000000

                    else :
                        value = float(value)
                        
                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

        for i in range(100):
            value = ''
            if mark2[i]['volume'] == '---' or mark2[i]['volume'] is None :
                volume.append(0)
                
            else:
                for j in mark2[i]['volume'].split(','):
                    value += j

                if value[-1] == 'K':
                        value = float(value[:-1])*1000

                elif value[-1] == 'M':
                    value = float(value[:-1])*1000000

                else :
                    value = float(value)

                volume.append(float(value))
                volume2.append([len(mark)//500, float(value)])

    num = pd.Series(volume)

    for i in range(len(num)):
        if num[i] == 0:
            num[i] = np.NaN
        else:
            pass

    box = []
    
    for i in range(len(volume)//100):
        if math.isnan(num[100*i : 100*(i+1)].min()):
            box.append([0,0,0,0,0])
        else:
            box.append([num[100*i : 100*(i+1)].min(skipna=True), num[100*i : 100*(i+1)].quantile(.25), num[100*i : 100*(i+1)].mean(skipna=True), num[100*i : 100*(i+1)].quantile(.75), num[100*i : 100*(i+1)].max(skipna=True)])

    boxdict = {'box' : box, 'volume' : volume2, 'date' : date, 'mainnet': 'Eth'}
    boxjson = json.dumps(boxdict)
    return render(request, 'mv_box.html', {'boxjson' : boxjson, 'mainnet': 'Ethereum'})

def mv_histo(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('volume')
    volume = []

    for i in mark:
        value = ''
        if i['volume'] == '---' or i['volume'] is None:
            pass
            
        else:
            for j in i['volume'].split(','):
                value += j

            if value[-1] == 'K':
                volume.append(float(value[:-1])*1000)

            elif value[-1] == 'M':
                volume.append(float(value[:-1])*1000000)

            else :
                volume.append(float(value))

    gap = max(volume) / 10
    
    volumedict = {'volume' : volume, 'gap' : gap, 'mainnet': 'Eth'}
    volumejson = json.dumps(volumedict)
    return render(request, 'mv_histo.html', {'volumejson' : volumejson, 'mainnet': 'Ethereum'})

def mf_box(request):
    mark = ENftmarketcap.objects.order_by('-id').values('date_field')[:10]
    date = []
    
    for i in mark:
        z = i['date_field'][0:2] + '-' + i['date_field'][2:4] + '-' + i['date_field'][4:6]
        date.insert(0, z)

    now = datetime.datetime.now().time()

    if int(str(now)[0:2]) >= 14 or int(str(now)[0:2]) < 2:
        mark = ENft24HStack.objects.order_by('-id').values('floor_price')[:5000]
        volume = []
        volume2 = []
        
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['floor_price'] == '---' or mark[j]['floor_price'] is None or mark[j]['floor_price'] == '—':
                    volume.insert(0, 0)
                    
                elif mark[j]['floor_price'][0] == '<':
                    value += '0.01'
                    volume.insert(0, float(value))

                else :
                    for j in mark[j]['floor_price'].split(','):
                        value += j
                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

    else :
        mark = ENft24HStack.objects.order_by('-id').values('floor_price')[:4500]
        mark2 = ENft24H.objects.values('floor_price')
        volume = []
        volume2 = []
       
        for i in range(len(mark)//500):
            for j in range((5*i+4)*100, 500*(i+1)):
                value = ''
                if mark[j]['floor_price'] == '---' or mark[j]['floor_price'] is None or mark[j]['floor_price'] == '—' :
                    volume.append(0)

                elif mark[j]['floor_price'][0] == '<':
                    value += '0.01'
                    volume.insert(0, float(value))
                    
                else:
                    for j in mark[j]['floor_price'].split(','):
                        value += j
                    volume.insert(0, float(value))
                    volume2.insert(0, [len(mark)//500-i-1, float(value)])

        for i in range(100):
            value = ''
            if mark2[i]['floor_price'] == '---' or mark2[i]['floor_price'] is None or mark2[i]['floor_price'] == '—' :
                volume.insert(0, 0)
                
            elif mark2[i]['floor_price'][0] == '<':
                value += '0.01'
                volume.insert(0, float(value))
            
            else :
                for j in mark2[i]['floor_price'].split(','):
                    value += j
                volume.append(float(value))
                volume2.append([len(mark)//500, float(value)])

    num = pd.Series(volume)

    for i in range(len(num)):
        if num[i] == 0:
            num[i] = np.NaN
        else:
            pass
    
    box = []

    for i in range(len(volume)//100):
        if math.isnan(num[100*i : 100*(i+1)].min()):
            box.append([0,0,0,0,0])
        else:
            box.append([num[100*i : 100*(i+1)].min(skipna=True), num[100*i : 100*(i+1)].quantile(.25), num[100*i : 100*(i+1)].mean(skipna=True), num[100*i : 100*(i+1)].quantile(.75), num[100*i : 100*(i+1)].max(skipna=True)])

    boxdict = {'box' : box, 'volume' : volume2, 'date' : date, 'mainnet': 'Eth'}
    boxjson = json.dumps(boxdict)
    return render(request, 'mf_box.html', {'boxjson' : boxjson, 'mainnet': 'Ethereum' })

def mf_histo(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('floor_price')
    floor_price = []

    for i in mark:
        value = ''
        
        if i['floor_price'] == '---' or i['floor_price'] is None or i['floor_price'] == '—' :
            pass

        elif i['floor_price'][0] == '<':
            value += '0.01'
            floor_price.append(float(value))

        else:
            for j in i['floor_price'].split(','):
                value += j

            if value[-1] == 'K':
                floor_price.append(float(value[:-1])*1000)

            elif value[-1] == 'M':
                floor_price.append(float(value[:-1])*1000000)

            else :
                floor_price.append(float(value))

            floor_price.append(float(value))

    gap = max(floor_price) / 10
    
    floor_pricedict = {'floor_price' : floor_price, 'gap' : gap, 'mainnet': 'Eth'}
    floor_pricejson = json.dumps(floor_pricedict)
    return render(request, 'mf_histo.html', {'floor_pricejson' : floor_pricejson, 'mainnet': 'Ethereum'})

def mv_pie(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('collection', 'volume')
    volume = ENftmarketcap.objects.order_by('-id').values('volume_total')[0]
    piedict={}
    tnt = 0
    for i in range(100):
        value = ''
        markdict={}
        if mark[i]['volume'] == '---' or mark[i]['volume'] is None :
            pass
        else:
            for j in mark[i]['volume'].split(','):
                value += j

            if value[-1] == 'K':
                value = float(value[:-1])*1000

            elif value[-1] == 'M':
                value = float(value[:-1])*1000000

            else :
                value = float(value)
        
        if i < 10:
            markdict['collection'] = mark[i]['collection']
            value = float(value) / volume['volume_total'] * 100
            tnt += value
            markdict['per'] = value
            piedict[str(i+1)] = markdict

        else :
            pass
    
    tnt = 100 - tnt
    piedict['etc'] = {'collection' : 'etc', 'per' : tnt, 'mainnet': 'Eth'}
    piejson = json.dumps(piedict)
    return render(request, 'mv_pie.html', {'piejson' : piejson, 'mainnet': 'Ethereum'})

def mf_pie(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('collection', 'floor_price')
    pri = []
    ind = []
    for i in range(100):
        value = ''
        if mark[i]['floor_price'] == '---' or mark[i]['floor_price'] is None or mark[i]['floor_price'] == '—' :
            pri.append([i, 0])

        elif mark[i]['floor_price'][0] == '<':
            value += '0.01'
            pri.append([i, float(value)])

        else:
            for j in mark[i]['floor_price'].split(','):
                value += j

            if value[-1] == 'K':
                value = float(value[:-1])*1000

            elif value[-1] == 'M':
                value = float(value[:-1])*1000000

            else :
                value = float(value)

            pri.append([i, float(value)])

    price = sorted(pri, key = lambda x : -x[1])

    for i in range(10):
        ind.append(price[i][0])

    volume = ENftmarketcap.objects.order_by('-id').values('floor_price_total')[0]
    piedict={}
    tnt = 0

    for i in range(len(ind)):
        value = ''
        markdict={}

        if mark[ind]['floor_price'][0] == '<':
            value += '0.01'

        else :
            for j in mark[ind[i]]['floor_price'].split(','):
                    value += j

        markdict['collection'] = mark[ind[i]]['collection']
        value = float(value) / volume['floor_price_total'] * 100
        markdict['per'] = value
        tnt += float(value)
        piedict[str(i+1)] = markdict
    
    tnt = 100 - tnt
    piedict['etc'] = {'collection' : 'etc', 'per' : tnt, 'mainnet': 'Eth'}
    piejson = json.dumps(piedict)
    return render(request, 'mf_pie.html', {'piejson' : piejson, 'mainnet': 'Ethereum'})

def mv_bar(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('collection', 'volume')
    volume = ENftmarketcap.objects.order_by('-id').values('volume_total')[0]
    bar = []
    tnt = 0
    for i in range(10):
        value = ''

        if mark[i]['volume'] == '---' or mark[i]['volume'] is None :
            pass
            
        else:
            for j in mark[i]['volume'].split(','):
                value += j

            if value[-1] == 'K':
                value = float(value[:-1])*1000

            elif value[-1] == 'M':
                value = float(value[:-1])*1000000

            else :
                value = float(value)

            value = float(value) / volume['volume_total'] * 100
            tnt += value
            bar.append([mark[i]['collection'], value])
    
    tnt = 100 - tnt
    bar.append(['etc', tnt])
    bardict = {'bar' : bar, 'mainnet': 'Eth'}
    barjson = json.dumps(bardict)
    return render(request, 'mv_bar.html', {'barjson' : barjson, 'mainnet': 'Ethereum'})

def mf_bar(request):
    mark = ENft24H.objects.filter(ranking__range=(1,100)).values('collection', 'floor_price')
    pri = []
    ind = []
    for i in range(100):
        value = ''

        if mark[i]['floor_price'] == '---' or mark[i]['floor_price'] is None or mark[i]['floor_price'] == '—' :
            pri.append([i, 0])

        elif mark[i]['floor_price'][0] == '<':
            value += '0.01'
            pri.append([i, float(value)])

        else:
            for j in mark[i]['floor_price'].split(','):
                value += j

            if value[-1] == 'K':
                value = float(value[:-1])*1000

            elif value[-1] == 'M':
                value = float(value[:-1])*1000000

            else :
                value = float(value)
                
            pri.append([i, float(value)])

    price = sorted(pri, key = lambda x : -x[1])

    for i in range(10):
        ind.append(price[i][0])

    volume = ENftmarketcap.objects.order_by('-id').values('floor_price_total')[0]
    bar=[]
    tnt = 0

    for i in range(len(ind)):
        value = ''

        if mark[ind[i]]['floor_price'][0] == '<':
            value += '0.01'
            
        else:
            for j in mark[ind[i]]['floor_price'].split(','):
                    value += j

        value = float(value) / volume['floor_price_total'] * 100
        tnt += float(value)
        bar.append([mark[i]['collection'], value])
    
    tnt = 100 - tnt
    bar.append(['etc', tnt])
    bardict = {'bar' : bar, 'mainnet': 'Eth'}
    barjson = json.dumps(bardict)
    return render(request, 'mf_bar.html', {'barjson' : barjson, 'mainnet': 'Ethereum'})

def mv_mark(request):
    ti = "'e_nftmarketcap'"
    conn = pymysql.connect(host = 'localhost', user = 'id', password = 'pass', db = 'id', charset = 'utf8')
    cursor = conn.cursor()

    cursor.execute('SELECT UPDATE_TIME FROM INFORMATION_SCHEMA.TABLES WHERE table_name=%s' % (ti))
    a = cursor.fetchone()
    time = a[0]
    conn.close()

    mark = ENftmarketcap.objects.values()
    std_vol_mar = ENftmarketcap.objects.filter(id=1).values('volume_marketcap')[0]['volume_marketcap']
    e_nftmarketcap = []

    for i in range(len(mark)):
        e_dict = {}
        if i == len(mark)-1:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_dict["close"] = round(mark[i]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)

        else:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_dict["close"] = round(mark[i+1]['volume_marketcap'] / std_vol_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)
    
    marketcapdict = {'marketcap' : e_nftmarketcap, 'mainnet': 'Eth'}
    marketcapjson = json.dumps(marketcapdict)
    return render(request, 'mv_mark.html', {'marketcapjson' : marketcapjson, 'time' : time, 'mainnet': 'Ethereum' })

def mf_mark(request):
    mark = ENftmarketcap.objects.values()
    std_flo_mar = ENftmarketcap.objects.filter(id=1).values('floor_price_marketcap')[0]['floor_price_marketcap']
    e_nftmarketcap = []

    for i in range(len(mark)):
        e_dict = {}
        if i == len(mark)-1:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_dict["close"] = round(mark[i]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)

        else:
            e_dict["timestamp"] = datetime.datetime(int('20'+mark[i]['date_field'][0:2]), int(mark[i]['date_field'][2:4]), int(mark[i]['date_field'][4:6]), 11, 0, 0).timestamp()*1000
            e_dict["open"] = round(mark[i]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_dict["close"] = round(mark[i+1]['floor_price_marketcap'] / std_flo_mar * 1000, 2)
            e_nftmarketcap.append(e_dict)
    
    marketcapdict = {'marketcap' : e_nftmarketcap, 'mainnet': 'Eth'}
    marketcapjson = json.dumps(marketcapdict)
    return render(request, 'mf_mark.html', {'marketcapjson' : marketcapjson, 'mainnet': 'Ethereum'})






# def percent_24h(request):
#     mark = ENft24H.objects.filter(ranking__range=(1,100)).values('number_24h')
#     cnt = 0
#     for i in range(100):
#         if mark[i]['number_24h'] == '---' or mark[i]['number_24h'] is None:
#             pass
#         elif mark[i]['number_24h'][0:1] == '+':
#             cnt += 1
#     inc = cnt
#     dec = 100 - inc
#     percent_24hdict = { 'inc' : inc, 'dec' : dec, 'mainnet': 'Eth' }
#     percent_24hjson = json.dumps(percent_24hdict)
#     return render(request, 'percent_24h.html', {'percent_24hjson' : percent_24hjson, 'mainnet': 'Ethereum'})

# def percent_7d(request):
#     mark = ENft24H.objects.filter(ranking__range=(1,100)).values('number_7d')
#     cnt = 0
#     for i in range(100):
#         if mark[i]['number_7d'] == '---' or mark[i]['number_7d'] is None:
#             pass
#         elif mark[i]['number_7d'][0:1] == '+':
#             cnt += 1
#     inc = cnt
#     dec = 100 - inc
#     percent_7ddict = { 'inc' : inc, 'dec' : dec, 'mainnet': 'Eth' }
#     percent_7djson = json.dumps(percent_7ddict)
#     return render(request, 'percent_7d.html', {'percent_7djson' : percent_7djson, 'mainnet': 'Ethereum'})

# def mpercent_24h(request):
#     mark = ENft24H.objects.filter(ranking__range=(1,100)).values('number_24h')
#     cnt = 0
#     for i in range(100):
#         if mark[i]['number_24h'] == '---' or mark[i]['number_24h'] is None:
#             pass
#         elif mark[i]['number_24h'][0:1] == '+':
#             cnt += 1
#     inc = cnt
#     dec = 100 - inc
#     percent_24hdict = { 'inc' : inc, 'dec' : dec, 'mainnet': 'Eth' }
#     percent_24hjson = json.dumps(percent_24hdict)
#     return render(request, 'mpercent_24h.html', {'percent_24hjson' : percent_24hjson, 'mainnet': 'Ethereum'})

# def mpercent_7d(request):
#     mark = ENft24H.objects.filter(ranking__range=(1,100)).values('number_7d')
#     cnt = 0
#     for i in range(100):
#         if mark[i]['number_7d'] == '---' or mark[i]['number_7d'] is None:
#             pass
#         elif mark[i]['number_7d'][0:1] == '+':
#             cnt += 1
#     inc = cnt
#     dec = 100 - inc
#     percent_7ddict = { 'inc' : inc, 'dec' : dec, 'mainnet': 'Eth' }
#     percent_7djson = json.dumps(percent_7ddict)
#     return render(request, 'mpercent_7d.html', {'percent_7djson' : percent_7djson, 'mainnet': 'Ethereum'})
