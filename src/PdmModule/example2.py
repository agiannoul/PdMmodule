from PdmModule.PdMApi import PdmModule,PdmModuleStatic
import pandas as pd
import numpy as np

streamModule =PdmModule()
prediction = streamModule.collect_data(pd.to_datetime("01/01/2023 15:00:15"), np.array([0.52, 0.32,0.22,0.16,0.15,0.12,0.13]), id="1")
