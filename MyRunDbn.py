# coding=gbk

import sys, os, random, zipfile
from numpy import log
from shutil import copyfile
import matplotlib.pyplot as plt
import time
import cPickle
import numpy
import scipy.io as sio  

####################################
### local import
####################################
from ChalearnLAPEvaluation import evalGesture,exportGT_Gesture
from ChalearnLAPSample import GestureSample
from utils import Extract_feature_Realtime
from utils import Extract_feature_UNnormalized
from utils import normalize
from utils import imdisplay
from utils import createSubmisionFile
############### viterbi path import
from utils import viterbi_path, viterbi_path_log
from utils import viterbi_colab_clean
from utils import viterbi_endframe

####################################
### theano import
####################################
sys.path.append(r'.\TheanoDL')
try:
    import theano
    import theano.tensor as T
    from theano.tensor.shared_randomstreams import RandomStreams
    from logistic_sgd import LogisticRegression
    from mlp import HiddenLayer
    from rbm import RBM
    from grbm import GBRBM
    from utils import zero_mean_unit_variance
    from utils import normalize
    from GRBM_DBN import GRBM_DBN
    from sklearn import preprocessing
except ImportError:
    sys.exit('Please install Theano!')

class RunDbn(object):
    def __init__(self):
        ####################################
        ### Some initialization ############
        ####################################
        self.used_joints = ['ElbowLeft', 'WristLeft', 'ShoulderLeft','HandLeft',
                        'ElbowRight', 'WristRight','ShoulderRight','HandRight',
                        'Head','Spine','HipCenter']#11����
        self.njoints = len(self.used_joints)
        ### load the pre-store normalization constant
        f = open('SK_normalization.pkl','rb')#Ԥ�ȴ���õ�
        SK_normalization = cPickle.load(f)#cPicke�� ������������Ϊ�ļ�����

        self.Mean1 =SK_normalization ['Mean1']#����ľ�ֵ�� ������ ������ʵ���ݹ�һ��Ҫʹ�õ�
        self.Std1 = SK_normalization['Std1']

        #����vitebi�㷨Ҫ������
        ## Load Prior and transitional Matrix Ԥ����õ�ת������
        dic=sio.loadmat('Transition_matrix.mat')#scipy.io �Ǹ���ѧ����ģ�飬iģ��ʵ����MATLAB���ݵĵ���
        self.Transition_matrix = log(dic['Transition_matrix'])
        self.Prior = log(dic['Prior'])
        ##########################
        ### model 1  ��һ�����繹��ģʽ  #
        ##########################        
        self.numpy_rng = numpy.random.RandomState(123)
        self.dbn = GRBM_DBN(numpy_rng=self.numpy_rng, n_ins=528,
        hidden_layers_sizes=[1000, 1000, 500],
        n_outs=201)
        self.dbn.load('dbn_2014-05-23-20-07-28.npy')#Ԥ��ѵ���õĹ���
        
        z=theano.tensor.dmatrix('z')
        #�������theano�����⺯������
        self.validate_model = theano.function(inputs=[z],
            outputs=self.dbn.logLayer.p_y_given_x,#������߼��ع������
            givens={ self.dbn.x: z})


    def myBuildDBNtest(self):
        #��ȡ����֡�У�ԭʼ�ĹǼܵ㣬�õ�һ������Skeleton_matrix ��ͬʱ���عǼ��Ƿ��0��
        #Skeleton_matrix, valid_skel = Extract_feature_UNnormalized(smp, used_joints, 1, smp.getNumFrames())
        time_tic = time.time()  
        import cPickle
        Skeleton_matrix=cPickle.load(open("testSkeleton_matrix","rb"))
        #print Skeleton_matrix
 
        Feature = Extract_feature_Realtime(Skeleton_matrix, self.njoints)

        Feature_normalized = normalize(Feature, self.Mean1, self.Std1)
       
        '''
        ##########################
        ### model 1  ��һ�����繹��ģʽ  #
        ##########################
        dbn = GRBM_DBN(numpy_rng=numpy_rng, n_ins=528,
        hidden_layers_sizes=[1000, 1000, 500],
        n_outs=201)
        dbn.load('dbn_2014-05-23-20-07-28.npy')#Ԥ��ѵ���õĹ���
        #�������theano�����⺯������
        validate_model = theano.function(inputs=[],
            outputs=dbn.logLayer.p_y_given_x,#������߼��ع������
            givens={ dbn.x: shared_x})   '''

        observ_likelihood_1 = self.validate_model(Feature_normalized)#���ú����õ����



        ##########################
        # viterbi path decoding
        #####################
        observ_likelihood_1=observ_likelihood_1[0:50,:]
        #�����Լ����ˣ�ֻ�е�һ������ṹ�ģ�
        log_observ_likelihood = log(observ_likelihood_1.T) 
        #������һ������ �������������Ǹ���   [1884������, 201��] ��Tת����
        print "����ʱ�� %d sec" % int(time.time() - time_tic)
        time_tic = time.time()


        #�������vibiter�㷨��
        print("\t Viterbi path decoding " )
        # do it in log space avoid numeric underflow
        [path, predecessor_state_index, global_score] =viterbi_path_log(
            self.Prior,  self.Transition_matrix, log_observ_likelihood   )

        label=viterbi_endframe(path,5,30)
        # Some gestures are not within the vocabulary
        #[pred_label, begin_frame, end_frame, Individual_score, frame_length] = viterbi_colab_clean(
        #    path, global_score, threshold=-100, mini_frame=19)
 
        print "�����:"
        print label
        print "viterbi����ʱ�� %d sec" % int(time.time() - time_tic)

    def myBuildDBN(self,Skeleton_matrix):
        #��ȡ����֡�У�ԭʼ�ĹǼܵ㣬�õ�һ������Skeleton_matrix ��ͬʱ���عǼ��Ƿ��0��
        #Skeleton_matrix, valid_skel = Extract_feature_UNnormalized(smp, used_joints, 1, smp.getNumFrames())
        time_tic = time.time()  
 
        Feature = Extract_feature_Realtime(Skeleton_matrix, self.njoints)
        Feature_normalized = normalize(Feature, self.Mean1, self.Std1)
        observ_likelihood_1 = self.validate_model(Feature_normalized)#���ú����õ����

        ##########################
        # viterbi path decoding
        #####################
        #observ_likelihood_1=observ_likelihood_1[0:50,:]
        #�����Լ����ˣ�ֻ�е�һ������ṹ�ģ�
        log_observ_likelihood = log(observ_likelihood_1.T) 
        #������һ������ �������������Ǹ���   [1884������, 201��] ��Tת����
        print "����ʱ�� %d sec" % int(time.time() - time_tic)
        
        return log_observ_likelihood
    def myViterbi(self,log_observ_likelihood):  
        time_tic = time.time()

        #�������vibiter�㷨��
        print("\t Viterbi path decoding " )
        # do it in log space avoid numeric underflow
        [path, predecessor_state_index, global_score] =viterbi_path_log(
            self.Prior,  self.Transition_matrix, log_observ_likelihood   )

        label=viterbi_endframe(path,5,30)
        # Some gestures are not within the vocabulary
        #[pred_label, begin_frame, end_frame, Individual_score, frame_length] = viterbi_colab_clean(
        #    path, global_score, threshold=-100, mini_frame=19)
 
        print "�����:"
        print label
        print "viterbi����ʱ�� %d sec" % int(time.time() - time_tic)
        return label

    
            

if __name__=='__main__':
    a=RunDbn(); 
    a.myBuildDBN()
             