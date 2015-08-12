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
        gesturesList=smp.getGestures()
        # Iterate for each action in this sample
        # Then we also choose 5 frame before and after the ground true data:
        seg_length = 5
        for gesture in gesturesList:
                # Get the gesture ID, and start and end frames for the gesture
                gestureID,startFrame,endFrame=gesture
                # This part is to extract action data

                Skeleton_matrix = numpy.zeros(shape=(5, len(used_joints)*3))
                HipCentre_matrix = numpy.zeros(shape=(5, 3))
                frame_num = 0 
                
                ## extract first 5 frames
                if startFrame-seg_length > 0:
                    Skeleton_matrix, valid_skel = Extract_feature_UNnormalized(smp, used_joints, startFrame-seg_length+1, startFrame)              
                    if not valid_skel:
                        print "No detected Skeleton: ", gestureID
                    else:
                        Feature = Extract_feature_Realtime(Skeleton_matrix, njoints)
                        begin_frame = count
                        end_frame = count+seg_length-1
                        Feature_all[begin_frame:end_frame,:] = Feature#ǰ5֡����������
                        Targets[begin_frame:end_frame, -1] = 1#���һλ��1��
                        count=count+seg_length-1

                ## extract last 5 frames
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
Feature_all_new = Feature_all[0:end_frame, :]
Targets_all_new = Targets[0:end_frame, :]
import cPickle as pickle
Feature_train = { "Feature_all_neutral": Feature_all_new, "Targets_all_new": Targets_all_new }
#���������󱣴�Ϊpkl
pickle.dump( Feature_train, open( "Feature_all_neutral_realtime.pkl", "wb" ) )

import scipy.io as sio
sio.savemat('Feature_all_neutral_realtime.mat', Feature_train)
#����Ϊmat��ʽ











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
#data=os.path.join("D:\\ComputerScienceLanguage\\Kinect\\CODE+Paper\\LAP\\13\\trainning1\\")  
# Get the list of training samples
samples=os.listdir(data)
used_joints = ['ElbowLeft', 'WristLeft', 'ShoulderLeft','HandLeft',
                'ElbowRight', 'WristRight','ShoulderRight','HandRight',
                'Head','Spine','HipCenter']
njoints = len(used_joints)
STATE_NO = 10
count = 0

# pre-allocating the memory
Feature_all =  numpy.zeros(shape=(400000, (njoints*(njoints-1)/2 + njoints**2)*3),dtype=numpy.float32)
Targets = numpy.zeros( shape=(400000, STATE_NO*20+1), dtype=numpy.uint8)
# Access to each sample
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
        gesturesList=smp.getGestures()

        # Iterate for each action in this sample
        for gesture in gesturesList:
            # Get the gesture ID, and start and end frames for the gesture
            gestureID,startFrame,endFrame=gesture
            Skeleton_matrix, valid_skel = Extract_feature_UNnormalized(smp, used_joints, startFrame, endFrame)           
            # to see we actually detect a skeleton:
            if not valid_skel:
                print "No detected Skeleton: ", gestureID
            else:                            
                ### extract the features according to the CVPR2014 paper
                Feature = Extract_feature_Realtime(Skeleton_matrix, njoints)
                Target = numpy.zeros( shape=(Feature.shape[0], STATE_NO*20+1))
                #hmm��20������ ÿ������10������״̬��
                fr_no =  Feature.shape[0]
                for i in range(STATE_NO):  #HMM states force alignment ������ǿ�ƽ�����֡�ֳ�10�ݣ�ÿ����Ϊһ��״̬
                        begin_fr = numpy.round(fr_no* i /STATE_NO) + 1
                        end_fr = numpy.round( fr_no*(i+1) /STATE_NO) 
                        #print "begin: %d, end: %d"%(begin_fr-1, end_fr)
                        seg_length=end_fr-begin_fr + 1
                        targets = numpy.zeros( shape =(STATE_NO*20+1,1))#201 �У�1�� �Ľ������
                        targets[ i + STATE_NO*(gestureID-1)] = 1#��Ӧ�������*20+����״̬���==����ǩ��ȫ����Ÿ�ֵΪ1
                        begin_frame = count
                        end_frame = count+seg_length
                        Feature_all[begin_frame:end_frame,:] = Feature[begin_fr-1:end_fr,:]#������ƴ������
                        Targets[begin_frame:end_frame, :]= numpy.tile(targets.T,(seg_length, 1))
                        #targetsԭ���� 201�У�1�� ת�ú����1��201�У� ==1���о���״̬�����ֵ
                        #tile����չ����������ǩ ����չ��֡���ȣ� �в���
                        count=count+seg_length
        # ###############################################
        ## delete the sample
        del smp

# save the skeleton file:

#���գ�Feature_all �������������� ÿһ�ж���һ�������� ȥ����û�ж�����֡
#Targets �Ƕ�Ӧ����������״̬����֡��ţ�201ά�� �в�Ϊ0 ������������״̬���ֵ
import cPickle as pickle
f = open('Feature_train_realtime.pkl','wb')
pickle.dump( {"Feature_all": Feature_all[0:end_frame, :], "Targets_all": Targets[0:end_frame, :] },f)
f.close()



import scipy.io as sio
sio.savemat('Feature_all_train__realtime.mat', { "Feature_all": Feature_all[0:end_frame, :], "Targets_all": Targets[0:end_frame, :] })




