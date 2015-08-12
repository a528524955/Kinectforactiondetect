# coding=gbk
#-------------------------------------------------------------------------------
# Name:        Starting Kit for ChaLearn LAP 2014 Track3
# Purpose:     Show basic functionality of provided code
#
# Author:      Xavier Baro
# Author:      Di Wu: stevenwudi@gmail.com
# Created:     24/03/2014
# Copyright:   (c) Chalearn LAP 2014
# Licence:     GPL3
#-------------------------------------------------------------------------------
import sys, os,random,numpy,zipfile
from shutil import copyfile
import matplotlib.pyplot as plt

from ChalearnLAPEvaluation import evalGesture,exportGT_Gesture
from ChalearnLAPSample import GestureSample
from utils import IsLeftDominant
from utils import Extract_feature_Realtime
from utils import Extract_feature_UNnormalized


# Data folder (Training data)
print("Extracting the training files")
#data=os.path.join("M:\\ALP14\\small\\trantest\\")  
data=os.path.join("M:\\ALP14\\trainingall\\");
# Get the list of training samples
samples=os.listdir(data)
used_joints = ['ElbowLeft', 'WristLeft', 'ShoulderLeft','HandLeft',
                'ElbowRight', 'WristRight','ShoulderRight','HandRight',
                'Head','Spine','HipCenter']
njoints = len(used_joints)
STATE_NO = 10
count = 0

# pre-allocating the memory
Feature_all =  numpy.zeros(shape=(100000, (njoints*(njoints-1)/2 + njoints**2)*3),dtype=numpy.float32)
Targets = numpy.zeros( shape=(100000, STATE_NO*20+1), dtype=numpy.uint8)

# Access to each sample
#����ÿһ��zip�ļ�����ȡ������cvs�ļ�����ȡ������֡���õ���Ӧ�ĹǼܵ����
#Ϊ�������Ƕ�ǰ��5֡ȥ�����������������˸���־λ����
#20*10+1������״̬������   ���ʾ�ǿ���״̬�𣿣�
for file_count, file in enumerate(samples):
    #if not file.endswith(".zip"):
    #    continue;        
    if file_count<650: 
        print("\t Processing file " + file)
        # Create the object to access the sample
        smp=GestureSample(os.path.join(data,file))
        # ###############################################
        # USE Ground Truth information to learn the model
        # ###############################################
        # Get the list of actions for this frame
        gesturesList=smp.getGestures()#��ȡ���Ƶ�����
        # Iterate for each action in this sample
        # Then we also choose 5 frame before and after the ground true data:
        seg_length = 5
        for gesture in gesturesList:
                # Get the gesture ID, and start and end frames for the gesture
                gestureID,startFrame,endFrame=gesture#�õ����Ƶ�id ����ʼ����λ��֡
                # This part is to extract action data

                Skeleton_matrix = numpy.zeros(shape=(5, len(used_joints)*3))
                HipCentre_matrix = numpy.zeros(shape=(5, 3))
                frame_num = 0 
                
                ## extract first 5 frames
                if startFrame-seg_length > 0:
                    Skeleton_matrix, valid_skel = Extract_feature_UNnormalized(smp, used_joints, startFrame-seg_length+1, startFrame)  
                    #��ȡ��ʼ֡��ǰ5֡  ����ʼ֡�ĹǼ����꣬���浽�����У������Ƿ��0 ���Ļ�   
                    #һ��������ǰ5֡����������û�ж����ġ� ��͵�����Ȼ�����������á�
                             
                    if not valid_skel:
                        print "No detected Skeleton: ", gestureID
                    else:
                        Feature = Extract_feature_Realtime(Skeleton_matrix, njoints)
                        #��ȡ����������ֻ�е�ǰ֡������ ��ǰ��֡���� ά������

                        #�����ǽ���5֡�������浽 all ��������
                        begin_frame = count
                        end_frame = count+seg_length-1
                        Feature_all[begin_frame:end_frame,:] = Feature#ǰ5֡����������
                        Targets[begin_frame:end_frame, -1] = 1#���һλ��1����ʾû�ж���
                        count=count+seg_length-1

                ## extract last 5 frames
                #��ȡ���������ĺ�5֡
                if endFrame+seg_length < smp.getNumFrames():
                    Skeleton_matrix, valid_skel = Extract_feature_UNnormalized(smp, used_joints, endFrame, endFrame+seg_length-1)              
                    if not valid_skel:
                        print "No detected Skeleton: ", gestureID
                    else:
                        Feature = Extract_feature_Realtime(Skeleton_matrix, njoints)
                        begin_frame = count
                        end_frame = count+seg_length-1
                        Feature_all[begin_frame:end_frame,:] = Feature
                        Targets[begin_frame:end_frame, -1] = 1
                        count=count+seg_length-1
        # ###############################################
        del smp

# save the skeleton file:
#��ԭ�ռ��з���� �õ������� ����Ϊ�ʼ������һ������ռ�
Feature_all_new = Feature_all[0:end_frame, :]
Targets_all_new = Targets[0:end_frame, :]

import cPickle as pickle
#�����ǵ����ʵ䱣���ˡ�
Feature_train = { "Feature_all_neutral": Feature_all_new, "Targets_all_new": Targets_all_new }
#���������󱣴�Ϊpkl
pickle.dump( Feature_train, open( "Feature_all_neutral_realtime.pkl", "wb" ) )

import scipy.io as sio
sio.savemat('Feature_all_neutral_realtime.mat', Feature_train)
#����Ϊmat��ʽ









