import pickle
import pandas as pd

########################################################################################################################
###                                                Load Data                                                        ####
########################################################################################################################

path = r"C:\Users\20190285\surfdrive\05_Data\052_District_Pricenhage\0521_HeatPump"
HP_file = "\HeatPump.pkl"
Temp_file = "\TempDic.pkl"
AvgTemp_file = "\HP_floortemp_avg"

with open(path+HP_file, 'rb') as handle:
    HeatPump = pickle.load(handle)
with open(path + Temp_file, 'rb') as handle:
    TempDic = pickle.load(handle)
AvgTemp = pd.read_csv(path + AvgTemp_file + '.csv')
AvgTemp['time_start'] = pd.to_datetime(AvgTemp['time_start'])
AvgTemp = AvgTemp.set_index('time_start')


# COP Calculation

temp_h = 50
temp_c = AvgTemp.sum()[1]/AvgTemp.size

COP_avg = temp_h/(temp_h - temp_c)


COP = AvgTemp.floortemp.apply(lambda x: 1 - x/temp_h)
COP_avgbis = COP.sum()/COP.size


# # Energy demand estimation
#
# COP = 3.4
# SumEnergyDemand = SumConsumption.rename(index=str, columns={"consumption": "demand"})*COP
#
# maxdemand_Wh = SumEnergyDemand.loc[SumEnergyDemand['demand'].idxmax()] #Wh
# maxdemand_W = maxdemand_Wh/15*60 #W