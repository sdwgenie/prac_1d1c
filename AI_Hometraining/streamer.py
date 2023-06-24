import cv2
import numpy as np
import mediapipe as mp
from flask import Flask, render_template, Response, make_response
from scipy.spatial import distance
import json
import pose_compare
import pickle
from time import time
from flask_cors import CORS, cross_origin
import os
import requests



app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})

dick={}

upload=[]
file_tuple = ()
files_json=()

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

val=[0]

### cam size 지정
height = 650
width = 950
depth = 3

cam_status=0

### 정답 영상 데이터 불러오기
with open("Squat_Model.pickle","rb") as fr:
    model = pickle.load(fr)

cam = cv2.VideoCapture(0)

### loop 시작 전 time 체크
def reset():
    global start_time
    start_time = time()
    
def main_cam():  

    num = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while(True):
            ret_cam, cam_image = cam.read()
            cam_image = cv2.resize(cam_image,(width, height))
            cam_image = cv2.cvtColor(cam_image, cv2.COLOR_BGR2RGB)
            cam_image = cv2.flip(cam_image, 1)
            cam_image.flags.writeable = False
            results = pose.process(cam_image)
            cam_image.flags.writeable = True
            cam_image = cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR)

            if cam_status == 0 :
                try :  
                    mp_drawing.draw_landmarks(
                    cam_image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                    t1 = time()
                    t = t1 - start_time

                    num=num+1
                    # num1.append(num)

                    ### 스코어 저장
                    v = pose_compare.frame_loc(results.pose_landmarks.landmark)
                    pack = pose_compare.calculate_pose_score(model, 1000*t, v)
                    val.append(pack[0])

                    dick['{}'.format(num)]=pack
                    with open('report.json','w')as make_file:
                        json.dump(dick,make_file, ensure_ascii=False, indent='\t')
                        
                except :
                    dick['{}'.format(num)]=[0,0,0,0,0,0,0,0,0,0,0,0,0]
                    with open('report.json','w')as make_file:
                        json.dump(dick,make_file, ensure_ascii=False, indent='\t')
                    print('error')
                    pass

                ret, buffer = cv2.imencode('.jpg', cam_image)
                res_image = buffer.tobytes()
                    
                if (num % 30) == 0:
                  cv2.imwrite('imgs/%d.jpg' % (num), cam_image)
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + res_image + b'\r\n')

            else :
                cam.release()
                cv2.destroyAllWindows()
                break

### Cam 송출
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(main_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')

### Chart 송출
@app.route('/chart')
def chart():
    return render_template('chart.html', data='test')

@app.route('/live-data')
def live_data():
    ### 실시간 Chart 데이터 전송
    data = [time() * 1000, val[-1]]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app.route('/time', methods=['GET','POST'])
@cross_origin(supports_credentials=True)
def rreset():
    return Response(reset())

@app.route('/reset', methods=['GET','POST'])
@cross_origin(supports_credentials=True)
def rreset_page():
    global cam_status
    cam_status = 1
    
    ### 이미지, 점수 서버에 보냄
    file_list=os.listdir('./imgs/')
    file_handles = []
    try:
        for i in file_list:
            file_handles.append(('file', open('./imgs/%s' % (i),'rb')))
        file_handles.append(('file',open('report.json','rb')))

        requests.post('http://doit.withnet.com:8000/jso/', files=file_handles)

    finally:
        for fh in file_handles:
            fh[1].close()

    os.unlink('./report.json')
    for i in range(len(file_list)):
        os.unlink('./imgs/%s.jpg' % ((i)*30))

    return Response()

if __name__ == "__main__":
    app.run(debug=True)
