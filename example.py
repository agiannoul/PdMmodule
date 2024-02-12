from PdmModule.PdMApi import PdmModule,PdmModuleStatic
import pandas as pd
from PdmModule.Handlers.xgboostPairHandler import XgboostPairHandler
def test_id(id):
    streamModule = PdmModule(detector_class=XgboostPairHandler,parameters={
        "thresholdtype" : "selftunne",
        "ProfileSize" : 30,
        "thresholdfactor" : 15,
        "ActualProfileSize" : 0.25,
        "sequencesize" : 12,
        "alarmsThreshold" : 0,
    })
    data = pd.read_csv(f"tempData/NavarchosData/correlation/{id}.csv", index_col=0)
    events=pd.read_csv("tempData/NavarchosData/newerservices.csv",index_col=0)
    data.index=pd.to_datetime(data.index)
    events=events[events["vehicle_id"]==id]
    events['dt']=pd.to_datetime(events['dt'])
    dtlist=events['dt'].values

    di = 0
    ei = 0
    for i in range(len(data.index) + len(events.index)):
        if di >= len(data.index):
            break
        elif ei>=len(dtlist):
            prediction = streamModule.collect_data(timestamp=data.index[di], data=[dd for dd in data.iloc[di].values], id=str(id))
            print(prediction.toString())
            di += 1
        elif data.index[di] < dtlist[ei]:
            prediction=streamModule.collect_data(timestamp=data.index[di],data=[dd for dd in data.iloc[di].values],id=str(id))
            print(prediction.toString())
            di += 1
        else:
            streamModule.collect_event(timestamp=dtlist[ei],desc=events.iloc[ei]["desc"],id=str(id))
            ei+=1


def test_static_id(id):
    streamModule = PdmModule()
    data = pd.read_csv(f"tempData/NavarchosData/correlation/{id}.csv", index_col=0)
    events=pd.read_csv("tempData/NavarchosData/newerservices.csv",index_col=0)
    data.index=pd.to_datetime(data.index)
    events=events[events["vehicle_id"]==id]
    events['dt']=pd.to_datetime(events['dt'])

    staticpdm=PdmModuleStatic()
    predictions=staticpdm.predict(data,events,id)

    for pr in predictions:
        print(pr.toString())




test_id(17)
print("================================================")
test_static_id(17)