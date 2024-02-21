from PdmModule.Handlers.pairdetectionHandler import PairDectionHandler
from PdmModule.utils.structure import Eventpoint,PredictionPoint
from PdmModule.utils.dbcontector import SQLiteHandler

class PdmModule():
    '''
    This class is used to provide an api for streaming usage of Handlers methods.
    The method collect_data is called to pass data and get prediction
    and the method collect_event to pass an event to trigger reset of the technique (In current implementation any event passed triger reset.).


    detector_class: A tecnique handler wich follow the get_Datapoint, get_event interface from Handlers

    parameters : The parameters of the Handlers object to initialize
    '''
    def __init__(self,detector_class=PairDectionHandler,parameters={
        "thresholdtype" : "selftunne",
        "ProfileSize" : 30,
        "thresholdfactor" : 15,
        "ActualProfileSize" : 0.25,
        "sequencesize" : 12,
        "alarmsThreshold" : 0,
        "normz" : False
    }):
        self.sources={}
        self.detector_class=detector_class
        self.parameters=parameters
        self.parameters["resetcodes"]=[('reset',id)]
        self.database=SQLiteHandler()
        self.database.create_table()
    def save_id_model(self,id,timestamp):
        dictemp={"model":self.sources[id]}
        self.database.insert_record(date=timestamp, target=id,modelpickle=dictemp)
    def load_model(self,id):

        listresults=self.database.get_model(id)
        if len(listresults)>0:
            model=listresults[0]
            return model['model']
        else:
            return None
    def collect_data(self,timestamp,data,id):
        '''
            This method accepts a data point with timestamp from a source and returns a prediction. For not seen sources create a new instant of detector.

            timestamp: the timestamp of the data
            data: an numpy array contain features (real numbers)
            id: the source that these data related to
            '''
        if id in self.sources.keys():
            prediction=self.sources[id].get_Datapoint(timestamp,data, id)[0]
            self.save_id_model(id,timestamp)
        else:
            model=self.load_model(id)
            if model is None:
                self.sources[id]=self.detector_class(source=id,**self.parameters)
            else:
                self.sources[id] = model
            prediction=self.sources[id].get_Datapoint(timestamp, data, id)[0]
            self.save_id_model(id, timestamp)
        #prediction = PredictionPoint(anomaly_score, 0.5, alarm,self.thresholdtype,point.timestamp,point.source,notes=description,ensemble_details=(pairthresholds,pair_anomaly_scores))
        if prediction.score is None:
            notes=""
            for qqq in range(len(data)):
                notes+=",0,0"
            prediction = PredictionPoint(0, 0, False, "", timestamp,
                                         id, notes=notes,
                                                 ensemble_details="<>")
        return prediction


    def collect_event(self,timestamp,desc,id):
        '''
               This method trigger rest on the specific source (id) passed

               timestamp: the timestamp of the event
               desc: description of the event
               id: the source in which reset is triggered.
               '''
        ev =Eventpoint(code="reset",source=id,timestamp=timestamp)
        if id in self.sources.keys():
            self.sources[id].get_event(ev)
            self.save_id_model(id,timestamp)

        else:
            model = self.load_model(id)
            if model is None:
                self.sources[id] = self.detector_class(source=id, **self.parameters)
            else:
                self.sources[id] = model
            self.sources[id].get_event(ev)
            self.save_id_model(id,timestamp)

class PdmModuleStatic():
    '''
        This class is used to provide an api for simulating streaming application of a technique.
        So given all data (raw and event timestamps that triger rest to the tecnique, its simulates the stream of data and returns predictions

        The method predict is called to pass data and events for specific source and get all predictions

        detector_class: A tecnique handler wich follow the get_Datapoint, get_event interface from Handlers

        parameters : The parameters of the Handlers object to initialize
        '''
    def __init__(self,detector_class=PairDectionHandler,parameters={
        "thresholdtype" : "selftunne",
        "ProfileSize" : 30,
        "thresholdfactor" : 15,
        "ActualProfileSize" : 0.25,
        "sequencesize" : 12,
        "alarmsThreshold" : 0,
        "normz" : False
    }):
        self.detector_class = detector_class
        self.parameters = parameters
        self.parameters["resetcodes"] = [('reset', id)]


    def predict(self,data,events,id):
        '''
               This method simulate the stream using the raw and event data

               data: a DataFrame of the feature data (each row is a data point) where the index contain timestamps
               events: a DataFrame with events data, it needs to have one column 'dt' with timestamps of events and one 'desc' with a relative description
               id: the source of simulated data.
           '''
        if 'dt' not in events.columns:
            assert False, " A column named dt is expected in event dataframe"

        if 'desc' not in events.columns:
            assert False, " A column named dt is expected in event dataframe"

        handler = self.detector_class(source=id, **self.parameters)
        predictions = []
        dtlist = events['dt'].values
        di = 0
        ei = 0
        for i in range(len(data.index) + len(events.index)):
            if di >= len(data.index):
                break
            elif ei >= len(dtlist):
                prediction = handler.get_Datapoint(data.index[di], data.iloc[di].values, id)[0]
                if prediction.score is None:
                    notes = ""
                    for qqq in range(len(data)):
                        notes += ",0,0"
                    prediction = PredictionPoint(0, 0, False, "", data.index[di], id, notes=notes,
                                                 ensemble_details="<>")
                predictions.append(prediction)
                di += 1
            elif data.index[di] < dtlist[ei]:
                prediction = handler.get_Datapoint(data.index[di], data.iloc[di].values, id)[0]
                if prediction.score is None:
                    notes = ""
                    for qqq in range(len(data)):
                        notes += ",0,0"
                    prediction = PredictionPoint(0, 0, False, "", data.index[di], id, notes=notes,
                                                 ensemble_details="<>")
                predictions.append(prediction)
                di += 1
            else:
                ev = Eventpoint(code="reset", source=id, timestamp=dtlist[ei])
                handler.get_event(ev)
                ei += 1
        return predictions
