#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from PIL import Image
from tqdm import tqdm
from time import sleep
import cv2

class Thumbnail:
    
    def __init__(self):
        self.path_dir = './'
        self.img_list = []
        self.vid_list = []
    
    def file_list(self, path='./'):
        self.path_dir = path
        self.file_list = os.listdir(self.path_dir)
        
        for i in self.file_list:
            self.file_name = i.split('.')

            if self.file_name[-1] == 'jpg' or self.file_name[-1] == 'jpeg' or self.file_name[-1] == 'png' or self.file_name[-1] == 'gif':
                self.img_list.append(i)

            elif self.file_name[-1] == 'mp4' or self.file_name[-1] == 'avi' or self.file_name[-1] == 'mov' or self.file_name[-1] == 'wmv':
                self.vid_list.append(i)
    
    def make_folder(self, path='./thumbnail'):
        self.path_dir = path
        
        if not os.path.exists(self.path_dir):
            os.makedirs(self.path_dir)
            
            return print('dir made')
    
    def img_resize(self, path='./',save_path='./thumbnail/', x=128, y=128):
        self.path_dir = path
        self.save_dir = save_path
        
        for i in tqdm(self.img_list):
            sleep(0.5)
            self.img = Image.open(self.path_dir + i)
            self.img_resize = self.img.resize((x, y))
            # img_resize = img.resize((x,y), Image.LANCZOS) NEAREST < BOX < BILINEAR < HAMMING < BICUBIC < LANCZOS
            self.img_resize.save(self.save_dir + i.split('.')[0] + '_resize.jpg')
            
        return print('img save')
            
    def video_resize(self, path='./',save_path='./thumbnail/', x=128, y=128):
        self.path_dir = path
        self.save_dir = save_path
        
        for i in tqdm(self.vid_list):
            sleep(0.5)
            self.video = cv2.VideoCapture(self.path_dir + i)

            while(self.video.isOpened()):
                self.ret, self.image = self.video.read()
                self.image = cv2.resize(self.image, (x, y))
                cv2.imwrite(self.save_dir + i.split('.')[0] + '_thumbnail.jpg', self.image)
                self.video.release()
                break
            
        return print('vid save')