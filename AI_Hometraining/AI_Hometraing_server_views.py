from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import *
from collections import deque
import datetime
import json
import os
import natsort
import math

@csrf_exempt

def index(request):

    return render(request, 'index.html')

def main(request):
	
	return render(request, 'main.html')

def report(request):
	exdata = Exercise_Data.objects.order_by('-ex_id')[0].path
	file_list = os.listdir('./static/' + exdata + 'img')
	index = []
	js_list=[]

	file_list = natsort.natsorted(file_list)

	shoulder = 0
	arm = 0
	waist = 0
	leg = 0
	total = 0
	score=[]

	for i in file_list:
		ind = i[0:-4]
		index.append(int(ind))

	with open('./static/' + exdata + 'report.json', 'r') as ex_json :
		exjson = json.load(ex_json)

		for x in exjson:
			js_list.append(x)

	for i in js_list:
		total += exjson[i][0] / len(js_list)
		shoulder += (exjson[i][1] + exjson[i][4]) / (len(js_list)*2)
		arm += (exjson[i][2] + exjson[i][3] + exjson[i][5] + exjson[i][6]) / (len(js_list)*4)
		waist += (exjson[i][7] + exjson[i][8]) / (len(js_list)*2)
		leg += (exjson[i][9] + exjson[i][10] + exjson[i][11] + exjson[i][12]) / (len(js_list)*4)
		score.append(exjson[i][0])

	### 연월일 슬라이싱 후 문자열 삽입
	exdata_ = exdata[9:-1]
	exdata_ = "20" + exdata_[:2] + "/" + exdata_[2:4] + "/" + exdata_[4:6] + " " + exdata_[6:8] + ":" + exdata_[8:10] + ":" + exdata_[10:12] 
	
	### radar 차트 점수 기록	
	total = round(total)
	shoulder = round(shoulder)
	arm = round(arm)
	waist = round(waist)
	leg = round(leg)

	radar_chart = [total, shoulder, arm, waist, leg]
	
	### 평가 멘트
	verygood = "훌륭해요! SquatMaster가 될 자격이 충분합니다!"
	good = "좋습니다! 이대로만 진행하세요"
	soso = "아쉽네요, 조금만 힘을 내서 진행하세요!"
	bad = "어휴, 정말 엉망진창이네요"
	
	shoulder_ment = []
	arm_ment = []
	waist_ment = []
	leg_ment = []

	if shoulder >= 80:
		shoulder_ment.append(verygood)
	elif 60 <= shoulder < 80 :
		shoulder_ment.append(good)
	elif 30 <= shoulder < 60 :
		shoulder_ment.append(soso)
	else :
		shoulder_ment.append(bad)

	if arm >= 80:
		arm_ment.append(verygood)
	elif 60 <= arm < 80 :
		arm_ment.append(good)
	elif 30 <= arm < 60 :
		arm_ment.append(soso)
	else :
		arm_ment.append(bad)

	if waist >= 80:
		waist_ment.append(verygood)
	elif 60 <= waist < 80 :
		waist_ment.append(good)
	elif 30 <= waist < 60 :
		waist_ment.append(soso)
	else :
		waist_ment.append(bad)
	
	if leg >= 80:
		leg_ment.append(verygood)
	elif 60 <= leg < 80 :
		leg_ment.append(good)
	elif 30 <= leg < 60 :
		leg_ment.append(soso)
	else :
		leg_ment.append(bad)

	lvo = "당신의 레벨은 1에 해당합니다. Lunge 운동을 추천드립니다!"
	lvt = "당신의 레벨은 2에 해당합니다. Squat 운동을 추천드립니다!"
	lvth = "당신의 레벨은 3에 해당합니다. Lateral raise 운동을 추천드립니다!"
	lvf = "당신의 레벨은 4에 해당합니다. Handstand 운동을 추천드립니다!"
	lvfi = "당신의 레벨은 5에 해당합니다. Dragonflag 운동을 추천드립니다!"
	lvs = "당신의 레벨은 6에 해당합니다. Planche 운동을 추천드립니다!"
	
	total_ment = []

	if total >= 90:
		total_ment.append(lvs)
	elif 75 <= total < 90 :
		total_ment.append(lvfi)
	elif 60 <= total < 75 :
		total_ment.append(lvf)
	elif 45 <= total < 60 :
		total_ment.append(lvth)
	elif 30 <= total < 45 :
		total_ment.append(lvt)
	else :
		total_ment.append(lvo)

	bad_body = []
	babody = [shoulder, arm, waist, leg]
	# babody_ = ["shoulder", "arm", "waist", "leg"]	

	for i in babody:
		if i < 40:
			bad_body.append(i)

	### 시간에 따른 chart 점수
	line_chart = deque(maxlen=20)

	if len(js_list)!=0:
		a = math.floor(len(js_list) / 20)

		for i in range(len(score)):
			if (i % a) == 0 :
				line_chart.append(score[i])
				
	else:
		for i in range(20):
			line_chart.append(0)

	line_chart=list(line_chart)

	### 부위 별 점수
	### 프레임 점수 값
	context = {
			   'total_ment' : total_ment,
			   'bad_body' : bad_body,
			   'leg_ment' : leg_ment,
			   'waist_ment' : waist_ment,
			   'arm_ment' : arm_ment,
			   'shoulder_ment' : shoulder_ment,
			   'line_chart' : line_chart,
			   'radar_chart' : radar_chart,
			   'exdata_' : exdata_,
			   'exdata' : exdata,
			   'index' : index,
			   'total' : total,
			   'shoulder' : shoulder,
			   'arm' : arm,
			   'waist' : waist,
			   'leg' : leg,
			   'score' : score,}
			

	return render(request, 'report.html', context)

def jso(request):
    ### 전송된 이미지, 점수 데이터 저장
	if (request.method == "POST"):
		time = datetime.datetime.now()
		date = time.strftime('%y%m%d%H%M%S')
		ex_data = request.FILES

		for i in range(len(ex_data.getlist('file'))-1) :
			data = default_storage.save('./static/userdata/%s/img/%d.jpg' % (date,i*30), ContentFile(ex_data.getlist('file')[i].read()))

		data = default_storage.save('./static/userdata/%s/report.json' % (date), ContentFile(ex_data.getlist('file')[-1].read()))

		ex_data = Exercise_Data(path='userdata/%s/' % (date))
		ex_data.save()

	return HttpResponse(request)
