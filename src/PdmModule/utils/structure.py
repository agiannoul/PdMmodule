import pandas as pd
from pandas import DataFrame
from numpy import ndarray



class PredictionPoint():
    '''
    PredictionPoint - BatchPredictionPoint (utils.structure)

    All predictions generated by TechniquesHandlers are in the form of PredictionPoints.

    This is a simple class to represent a prediction, with the following fields:

        score: the anomaly score (list in case of Batch).
        threshold: threshold value (list in case of Batch).
        alarm: if this prediction causes an alarm (list in case of Batch).
        thresholdtype: metadata regarding the threshold technique used.
        timestamp: timestamp of prediction (list in case of Batch).
        source: The source that the prediction concerns.
        description: A description (a valid prediction should have the name of the technique).
        notes: Metadata (optional notes).
        ensemble_details: In case this prediction is from an ensemble technique, metadata text.

    '''
    def __init__(self, score, threshold, alarm, thresholdtype, timestamp, source, description="",notes="",ensemble_details=None):
        self.score = score
        self.threshold = threshold
        self.alarm = alarm
        self.thresholdtype = thresholdtype
        self.timestamp = timestamp
        self.source = source
        self.description = description
        self.notes = notes
        self.ensemble_details = ensemble_details

    def toString(self):
        kati=f"{self.source},{self.timestamp},{self.alarm}{self.notes},{self.ensemble_details}"
        #if kati[-1] == ",":
        #    kati= kati[:-1]
        return kati

class BatchPredictionPoint():
    def __init__(self, score, threshold, alarm, timestamp, source,thresholdtype=None, description="",ensemble_details=None):
        self.score = score
        self.threshold = threshold
        self.thresholdtype = thresholdtype
        self.alarm = alarm
        self.timestamp = timestamp
        self.source = source
        self.description = description
        self.ensemble_details = ensemble_details


class Datapoint():
    '''
    Datapoint (utils.structure)

    Represents a data sample.

        current: an ndarray
        reference: a DataFrame of vectors that represent the reference set related to the data sample.
        source: a string indicating the source of the sample.
        timestamp: the timestamp of the sample.

    '''
    def __init__(self,reference :DataFrame,current: ndarray,timestamp : pd.Timestamp,source):
        self.reference = reference
        self.current = current
        self.source = source
        self.timestamp = timestamp

class SimpleDatapoint():

    def __init__(self,current: ndarray,timestamp : pd.Timestamp,source):
        self.current = current
        self.source = source
        self.timestamp = timestamp
        self.description = None

class Eventpoint():
    '''
    EventPoint (utils.structure)

    All events are in the form of PredictionPoints.

    This is a simple class to represent a prediction, with the following fields:

        code: unique code of an event.
        timestamp: timestamp of the prediction.
        source: The source that the prediction concerns.
        details: Text, description, or any details.
        type: Metadata for the type of event (isolated, configuration, AD) used in context generation.

    '''
    def __init__(self,code,source,timestamp,details=None,type=None):
        self.code = code
        self.source = source
        self.timestamp = timestamp
        self.details = details
        self.type = type