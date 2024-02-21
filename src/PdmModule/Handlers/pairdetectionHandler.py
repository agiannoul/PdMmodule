import numpy as np
from numpy import ndarray
from PdmModule.utils.structure import PredictionPoint,Datapoint,Eventpoint
from PdmModule.Models import pairdetection
import pandas as pd


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    cls.__str__ = __str__
    return cls

@auto_str
class PairDectionHandler():
    # inner or selftunne
    '''
        Techniques Handlers (Handlers)

        In their initialization, they should accept their parameters, source, and reset codes. The source is a string that indicates the source of data that the Technique handler monitors. The reset codes are a list of tuples with all event codes and sources that may cause a reset in the technique (start over). The tuples in that list should be in the form of ev=(code, source) since they are tested like:

        if ev[0] == event.code and ev[1] == event.source:

        Interface:

        1. get_Datapoint(timestamp, vector, source, description) Feed an upcoming sample to the predictor, and a prediction is returned (when no available prediction, a PredictionPoint with None values should be returned).

        Returns a tuple: (PredictionPoint, Datapoint) - the prediction and the data in the form of Datapoint.

        2. get_event(Eventpoint) Feed an upcoming event to the predictor.

        Returns a Boolean, PredictionPoint, Datapoint. A boolean value is returned if the event causes a reset in the technique. Moreover, some techniques (which perform batch prediction) return the predictions and the list of Datapoints that the prediction concerns (if these are None, they are ignored).

        '''

    def __init__(self,source,thresholdtype="inner",thresholdfactor=2,ProfileSize=30,ActualProfileSize=1,resetcodes=[],currentReference=None,constThresholdfilter=float('-inf'),sequencesize=1,alarmsThreshold=0,normz=False):


        self.sequencesize=sequencesize
        self.alarmsThreshold=alarmsThreshold

        self.currentReference=currentReference
        self.normz = normz
        self.constThresholdfilter=constThresholdfilter

        self.resetcodes = resetcodes
        self.thresholdtype = thresholdtype
        self.thresholdfactor = thresholdfactor
        self.source=source
        self.ProfileSize=ProfileSize

        self.pointbuffer = []
        self.profilebuffer = []
        self.profilebuffertimestamps = []


        if thresholdtype=="inner":
            self.ActualProfileSize = ProfileSize
        elif ActualProfileSize<1:
            self.ActualProfileSize=int(ActualProfileSize*self.ProfileSize)
        else:
            self.ActualProfileSize=ActualProfileSize

        self.model = pairdetection.PairDetection(thresholdtype, thresholdfactor,self.ActualProfileSize,constThresholdfilter=self.constThresholdfilter,alarmsThreshold=self.alarmsThreshold,normz=self.normz)


        if self.currentReference is None:
            self.calculated_profile = False
        else:
            temp_datapoint = Datapoint(self.currentReference, None, None, source)
            self.model.initilize(temp_datapoint)
            self.calculated_profile = True
    def manual_update_and_reset(self,thresholdtype=None,thresholdfactor=None):
        if thresholdtype!=None:
            self.thresholdtype = thresholdtype
        if thresholdfactor!=None:
            self.thresholdfactor = thresholdfactor
        self.model = pairdetection.PairDetection(thresholdtype, thresholdfactor,self.ActualProfileSize,constThresholdfilter=self.constThresholdfilter,actualProfileSize=self.alarmsThreshold,normz=self.normz)
    def get_current_reference(self):
        return self.currentReference

    def calculateReferenceData(self):
        if len(self.profilebuffer)>self.ProfileSize:


            data = [[seqdata.current for seqdata in seqpoint] for seqpoint in self.profilebuffer]
            tempnumpy=[]
            for sequense in data:
                tempnumpy.append(np.array([np.array(corrs) for corrs in sequense]))
            tempnumpy=np.array(tempnumpy)
            foundprofile = tempnumpy
            self.calculated_profile = True
            self.currentReference = foundprofile
    def get_Datapoint(self,timestamp : pd.Timestamp,data : ndarray, source) -> PredictionPoint:
        temp_datapoint = Datapoint(self.currentReference, data, timestamp, source)

        if source==self.source:
            self.pointbuffer.append(temp_datapoint)
            if len(self.pointbuffer) >= self.sequencesize:
                self.pointbuffer = self.pointbuffer[-self.sequencesize:]


            if len(self.pointbuffer) < self.sequencesize:
                prediction = PredictionPoint(None, None, None, self.thresholdtype, temp_datapoint.timestamp,
                                             temp_datapoint.source, description="no profile yet")

            elif self.calculated_profile==False:
                # datapoint pass reference domain profile
                self.profilebuffer.append([dd for dd in self.pointbuffer])
                self.profilebuffertimestamps.append(timestamp)
                self.calculateReferenceData()
                if self.calculated_profile:
                    temp_datapoint = Datapoint(self.currentReference, np.array([np.array(corrs) for corrs in self.pointbuffer]), timestamp, source)
                    self.model.initilize(temp_datapoint)
                prediction= PredictionPoint(None, None, None,self.thresholdtype, temp_datapoint.timestamp,temp_datapoint.source,description="no profile yet")
            else:
                temp_datapoint = Datapoint(self.currentReference,
                                           np.array([np.array(corrs.current) for corrs in self.pointbuffer]), timestamp,
                                           source)
                prediction=self.model.get_data(temp_datapoint)
                prediction.description="pair detection"
            return prediction,temp_datapoint
        prediction = PredictionPoint(None, None, None, self.thresholdtype, temp_datapoint.timestamp,
                                     temp_datapoint.source, description="wrong source")
        return prediction,temp_datapoint

    def get_event(self, event: Eventpoint):
        for ev in self.resetcodes:
            if ev[0] == event.code:
                self.reset()
                return True, None, None
        return False, None, None
    def reset(self):
        self.profilebuffer = []
        self.profilebuffertimestamps = []
        self.calculated_profile = False
        self.currentReference = None
        self.model.reset()
        return