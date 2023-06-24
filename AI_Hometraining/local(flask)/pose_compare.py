import numpy as np
from scipy.spatial import distance
import math

vector=[]
vector2=[]
score_total=[0]


def calculate_pose_score(model,t,v):
  ### 프레임 범위 비교
  try :
    t = (t % 2060)
    index = []
    value = []

    for i in range(len(model['time'])):
        if t - 5000/24 <= model['time'][i] <= t + 3000/24:
            index.append(i)

    max = 0
    cnt = 0
    cnt2 = 0
    
  ### 범위 중 가장 높은 스코어 저장
    for j in index:
        value.append(compare_frame_squart(model['array'][j],v))
        cnt += 1

        for k in range(cnt):
          if value[k][0] > max :
            max = value[k][0]
            cnt2 = k

          else:
            pass

    return value[cnt2]
  
  except :
    return [0,0,0,0,0,0,0,0,0,0,0,0,0]

# v1 = frame_loc(results.pose_landmarks.landmark)
# v2 = frame_loc(results2.pose_landmarks.landmark)
def compare_frame_squart(v1, v2):
    vect=part_of_body(v1)
    vect2=part_of_body(v2)

    vectors_head=head(vect)
    vectors_head2=head(vect2)
    vectors_up=upper_body(vect)
    vectors_up2=upper_body(vect2)
    vectors_core=core(vect)
    vectors_core2=core(vect2)
    vectors_lo=lower_body(vect)
    vectors_lo2=lower_body(vect2)

    user_rw=right_wrist(vect)
    sol_rw=right_wrist(vect2)
    user_re=right_elbow(vect)
    sol_re=right_elbow(vect2)
    user_rs=right_shoulder(vect)
    sol_rs=right_shoulder(vect2)

    user_rp=right_pelvis(vect)
    sol_rp=right_pelvis(vect2)

    user_rk=right_knee(vect)
    sol_rk=right_knee(vect2)
    user_ra=right_ankle(vect)
    sol_ra=right_ankle(vect2)

    user_lw=left_wrist(vect)
    sol_lw=left_wrist(vect2)
    user_le=left_elbow(vect)
    sol_le=left_elbow(vect2)
    user_ls=left_shoulder(vect)
    sol_ls=left_shoulder(vect2)

    user_lp=left_pelvis(vect)
    sol_lp=left_pelvis(vect2)

    user_lk=left_knee(vect)
    sol_lk=left_knee(vect2)
    user_la=left_ankle(vect)
    sol_la=left_ankle(vect2)

    joint_score_RS=score_for_joint(joint_difference(user_rs,sol_rs,),35)
    joint_score_RE=score_for_joint(joint_difference(user_re,sol_re),35)
    joint_score_RW=score_for_joint(joint_difference(user_rw,sol_rw),35)

    joint_score_LS=score_for_joint(joint_difference(user_ls,sol_ls),35)
    joint_score_LE=score_for_joint(joint_difference(user_le,sol_le),35)
    joint_score_LW=score_for_joint(joint_difference(user_lw,sol_lw),35)

    joint_score_RP=score_for_joint(joint_difference(user_rp,sol_rp),35)
    joint_score_LP=score_for_joint(joint_difference(user_lp,sol_lp),35)

    joint_score_RK=score_for_joint(joint_difference(user_rk,sol_rk),35)
    joint_score_RA=score_for_joint(joint_difference(user_ra,sol_ra),35)

    joint_score_LK=score_for_joint(joint_difference(user_lk,sol_lk),35)
    joint_score_LA=score_for_joint(joint_difference(user_la,sol_la),35)

    head_score=np.mean(score_for_vectors(cosine_similarities(vectors_head,vectors_head2),35))
    upper_score=np.mean(score_for_vectors(cosine_similarities(vectors_up,vectors_up2),35))
    core_score=np.mean(score_for_vectors(cosine_similarities(vectors_core,vectors_core2),35))
    lower_score=np.mean(score_for_vectors(cosine_similarities(vectors_lo,vectors_lo2),35))

    score_head=head_score
    score_upper=upper_score*(0.1)+joint_score_RS*(0.2)+joint_score_RE*(0.2)+joint_score_RW*(0.05)+joint_score_LS*(0.2)+joint_score_LE*(0.2)+joint_score_LW*(0.05)
    score_core=core_score*(0.1)+joint_score_RP*(0.45)+joint_score_LP*(0.45)
    scoer_lower=lower_score*(0.1)+joint_score_RK*(0.35)+joint_score_RA*(0.1)+joint_score_LK*(0.35)+joint_score_LA*(0.1)
    total_score=(score_head*(0.05)+score_upper*(0.1)+score_core*(0.2)+scoer_lower*(0.65))*100
    score_total.append(total_score)
    
### 확인용 코드

    return score_total[-1],joint_score_RS*100,joint_score_RE*100,joint_score_RW*100,joint_score_LS*100,joint_score_LE*100,joint_score_LW*100,joint_score_RP*100,joint_score_LP*100,joint_score_RK*100,joint_score_RA*100,joint_score_LK*100,joint_score_LA*100

def frame_loc(result):
    coordinate=[]
    for i in result:
        if float(str(i).split()[7])>=0.7:
          #visuablity의 값을 조정하여 키포인트이 좌표를 반영할지를 결정한다.
            coordinate.append(np.array([float(str(i).split()[1]),float(str(i).split()[3])]))
        else:
            coordinate.append(np.array([np.nan,np.nan]))
    return coordinate

def part_of_body(coordinate):

  vectors=[]
  
#head
  #0
  R_Ear_to_R_Eye_O=coordinate[6]-coordinate[8]
  vectors.append(R_Ear_to_R_Eye_O)
  #1
  R_Eye_O_to_R_Eye=coordinate[5]-coordinate[6]
  vectors.append(R_Eye_O_to_R_Eye)
  #2
  R_Eye_to_R_Eye_I=coordinate[4]-coordinate[5]
  vectors.append(R_Eye_to_R_Eye_I)
  #3
  R_Eye_I_to_nose=coordinate[0]-coordinate[4]
  vectors.append(R_Eye_I_to_nose)
  #4
  L_Ear_to_L_Eye_O=coordinate[3]-coordinate[7]
  vectors.append(L_Ear_to_L_Eye_O)
  #5
  L_Eye_O_to_L_Eye=coordinate[2]-coordinate[3]
  vectors.append(L_Eye_O_to_L_Eye)
  #6
  L_Eye_to_L_Eye_I=coordinate[1]-coordinate[2]
  vectors.append(L_Eye_to_L_Eye_I)
  #7
  L_Eye_I_to_nose=coordinate[0]-coordinate[1]
  vectors.append(L_Eye_I_to_nose)
  #8
  M_R_to_M_L=coordinate[9]-coordinate[10]
  vectors.append(M_R_to_M_L)

#shoulder
  #9
  R_S_to_L_S=coordinate[11]-coordinate[12]
  vectors.append(R_S_to_L_S)
#right-arm
  #10
  R_S_to_R_E=coordinate[14]-coordinate[12]
  vectors.append(R_S_to_R_E)
  #11
  R_E_to_R_W=coordinate[16]-coordinate[14]
  vectors.append(R_E_to_R_W)
  #12
  R_W_to_R_T=coordinate[22]-coordinate[16]
  vectors.append(R_W_to_R_T)
  #13
  R_W_to_R_I=coordinate[20]-coordinate[16]
  vectors.append(R_W_to_R_I)
  #14
  R_W_to_R_P=coordinate[18]-coordinate[16]
  vectors.append(R_W_to_R_P)
#left-arm
  #15
  L_S_to_L_E=coordinate[13]-coordinate[11]
  vectors.append(L_S_to_L_E)
  #16
  L_E_to_L_W=coordinate[15]-coordinate[13]
  vectors.append(L_E_to_L_W)
  #17
  L_W_to_L_T=coordinate[21]-coordinate[15]
  vectors.append(L_W_to_L_T)
  #18
  L_W_to_L_I=coordinate[19]-coordinate[15]
  vectors.append(L_W_to_L_I)
  #19
  L_W_to_L_P=coordinate[17]-coordinate[15]
  vectors.append(L_W_to_L_P)

#core
  #20
  R_S_to_R_H=coordinate[24]-coordinate[12]
  vectors.append(R_S_to_R_H)
  #21
  L_S_to_L_H=coordinate[23]-coordinate[11]
  vectors.append(L_S_to_L_H)
  #22
  R_H_to_L_H=coordinate[23]-coordinate[24]
  vectors.append(R_H_to_L_H)
#lower body
  #right leg

  #23   
  R_H_to_R_K=coordinate[26]-coordinate[24]
  vectors.append(R_H_to_R_K)
  #24
  R_K_to_R_A=coordinate[28]-coordinate[26]
  vectors.append(R_K_to_R_A)
  #25
  R_A_to_R_h=coordinate[30]-coordinate[28]
  vectors.append(R_A_to_R_h)
  #26
  R_A_to_R_F_I=coordinate[32]-coordinate[28]
  vectors.append(R_A_to_R_F_I)
  #left leg

  #27
  L_H_to_L_K=coordinate[25]-coordinate[23]
  vectors.append(L_H_to_L_K)
  #28
  L_K_to_L_A=coordinate[27]-coordinate[25]
  vectors.append(L_K_to_L_A)
  #29
  L_A_to_L_h=coordinate[29]-coordinate[27]
  vectors.append(L_A_to_L_h)
  #30
  L_A_to_L_F_I=coordinate[31]-coordinate[27]
  vectors.append(L_A_to_L_F_I)

  return vectors


def right_wrist(vectors):
  joint_of_right_wrist=distance.cosine(vectors[14],(-vectors[11]))
  return joint_of_right_wrist

def right_elbow(vectors):
  joint_of_right_elbow=distance.cosine(vectors[11],(-vectors[10]))
  return joint_of_right_elbow

def right_shoulder(vectors):
  joint_of_right_shoulder=distance.cosine(vectors[9],vectors[10])
  return joint_of_right_shoulder

def left_wrist(vectors):
  joint_of_left_wrist=distance.cosine(vectors[19],(-vectors[16]))
  return joint_of_left_wrist

def left_elbow(vectors):
  joint_of_left_elbow=distance.cosine(-(vectors[15]),vectors[16])
  return joint_of_left_elbow

def left_shoulder(vectors):
  joint_of_left_shoulder=distance.cosine((-vectors[9]),vectors[15])
  return joint_of_left_shoulder

def right_pelvis(vectors):
  joint_of_right_pelvis=distance.cosine(vectors[23],(-vectors[20]))
  return joint_of_right_pelvis

def left_pelvis(vectors):
  joint_of_left_pelvis=distance.cosine(vectors[27],(-vectors[21]))
  return joint_of_left_pelvis

def right_knee(vectors):
  joint_of_right_wrist=distance.cosine(vectors[24],(-vectors[23]))
  return joint_of_right_wrist

def right_ankle(vectors):
  joint_of_right_elbow=distance.cosine(vectors[26],(-vectors[24]))
  return joint_of_right_elbow

def left_knee(vectors):
  joint_of_right_wrist=distance.cosine(vectors[28],(-vectors[27]))
  return joint_of_right_wrist

def left_ankle(vectors):
  joint_of_right_elbow=distance.cosine(vectors[30],(-vectors[28]))
  return joint_of_right_elbow

def joint_difference(joint,joint2):
  #joint는 user의 관절 각도와 정답의 관절
  difference=abs(joint-joint2)
  return difference

def head(vecters):
  #머리와 관련된 벡터값을 가져온다.
  head_vectors=[]
  for i in [3,7]:
    head_vectors.append(vecters[i])
  return head_vectors

def upper_body(vecters):
  #상체와 관련된 벡터값을 가져온다.
  upper_vectors=[]
  for i in [9,10,11,13,15,16,18]:
    upper_vectors.append(vecters[i])
  return upper_vectors

def core(vectors):
  #코어와 관련된 벡터값을 가져온다.
  core_vectors=[]
  for i in [20,21,22]:
    core_vectors.append(vectors[i])
  return core_vectors

def lower_body(vecters):
  #하체와 관련된 벡터값을 가져온다.
  lower_vectors=[]
  for i in [23, 24, 26, 27, 28, 30]:
    lower_vectors.append(vecters[i])
  return lower_vectors

def cosine_similarities(vectors,vectors2):
  #코사인 유사도를 구한다. 
  similaritise=[]
  for i, j in zip(vectors,vectors2):
    similarity=(distance.cosine(i,j))
    similaritise.append(similarity)
    
  return similaritise


def score_for_vectors(similaritise,degree):
  #유사도를 점수로 환산.
  #degree 조정으로 오차각도 조절
  vector_scores=[]
  Limit=float(1-math.cos(math.radians(degree)))
  for i in similaritise:
    if (i<Limit):
      vector_scores.append((Limit-i)/Limit)
    else:
      vector_scores.append(0)
  return vector_scores

def score_for_joint(deference,degree):
#각도값를 점수로 환산.
#degree 조정으로 오차각도 조절
  Limit=float(1-math.cos(math.radians(degree)))
  if (deference<Limit):
    joint_score=(Limit-deference)/Limit
  else:
    joint_score=0
  return joint_score
