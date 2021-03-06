import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from functools import reduce
import pickle
import gc
import time


print("Data Read phase \n")
########################################################################################################################
###                                                     Read                                                        ####
########################################################################################################################

# Path Definition
path = r"C:\Users\20190285\surfdrive\03_SharedFolders\Shalika_Waqas_Julien\JEMData\HP_consumption"
filename = r"\HP_consumption_cleaned_customer_id_" #files from ID 123 to 179

# Initialize
HeatPump = dict()
ID = 123

# Reading excel files
print("Looping over files:")

while ID < 180: #180 is end / 125 for test
    print(ID)
    # t1_start = time.perf_counter()
    # t2_start = time.process_time()
    data = pd.read_excel(path + filename + str(ID) + '.xlsx')

    # Date Time Manip
    data['time_start'] = pd.to_datetime(data['time_start'])

    # Heat Pump Dict completing
    HeatPump[ID] = data[data.flow == 9].drop(['customer_id', 'flow'], axis=1).rename(index=str, columns={"id": "DOI"}).set_index('time_start')#.drop_duplicates(keep='first')

    # Preprocessing - Define duplicate values as averages of the two & remove duplicate
    HeatPump[ID][HeatPump[ID].index.duplicated(keep='last')] = (HeatPump[ID][HeatPump[ID].index.duplicated(keep='first')] +
                                                                  HeatPump[ID][HeatPump[ID].index.duplicated(keep='last')]) / 2
    HeatPump[ID] = HeatPump[ID][~HeatPump[ID].index.duplicated(keep='first')]

    # File ID - skip missing files
    ID += 1
    if ID == 134:
        ID += 1
    elif ID == 160:
        ID = 169
    elif ID == 171:
        ID = 177
    del data
    # t1_stop = time.perf_counter()
    # t2_stop = time.process_time()
    # print("--------------------------------------------------")
    # print("Elapsed time: %.1f [s]" % ((t1_stop - t1_start)))
    # print("CPU process time: %.1f [s]" % ((t2_stop - t2_start)))
    # print("--------------------------------------------------")


########################################################################################################################
###                                                 Preprocess                                                      ####
########################################################################################################################
print(" \n Data PreProcessing phase \n")

# Fill out missing time stamps by None values
print("Missing data loop:")

id_ref = list(HeatPump.keys())[0]
date_rng = pd.date_range(start=HeatPump[id_ref].index[0], end=HeatPump[id_ref].index[-1], freq='15min')
df_ref = pd.DataFrame(date_rng, columns=['time_start']).set_index('time_start')

for id in HeatPump:
    print(id)

    # Index differences identification
    IndexNone = df_ref.index.difference(HeatPump[id].index)
    size_diff = df_ref.index.difference(HeatPump[id].index).size
    # Creat pd dataframes from differences
    NoneDataFrame = pd.DataFrame({'DOI': ["None"]*size_diff,
                                  'consumption': [None]*size_diff,
                                  'time_start': list(IndexNone)}).set_index('time_start')
    # Concat Reference dataframe with other one
    HeatPump[id] = pd.concat([HeatPump[id], NoneDataFrame]).sort_index()
    del IndexNone, size_diff, NoneDataFrame
del date_rng
gc.collect()    # Release unreferenced memory

# # Data Size check
# MaxDataSize = []
# for id in HeatPump:
#     MaxDataSize.append(HeatPump[id].consumption.values.size)


print("Data interpolation")
# Missing Data interpolation
for id in HeatPump:
    #HeatPump[id].consumption = HeatPump[id].consumption.astype(float)
    HeatPump[id].consumption = HeatPump[id].consumption.interpolate(method='linear', axis=0).ffill().bfill()



########################################################################################################################
###                                            Data Manipulation                                                    ####
########################################################################################################################

print("\n Data manipulation phase \n")

# Summing consumption
SumConsumption = pd.DataFrame
SumConsumption = HeatPump[list(HeatPump.keys())[0]].drop('DOI', axis=1)
for id in list(HeatPump.keys())[1:]:
    SumConsumption = SumConsumption + HeatPump[id].drop('DOI', axis=1)



# # Plotting summed demand
# plt.close('all')
# HeatPump[123].consumption.plot()
# SumConsumption.plot()


########################################################################################################################
###                                                Data Saving                                                      ####
########################################################################################################################

print("\n Data Saving phase \n")
SumConsumption.to_csv(r"C:\Users\20190285\surfdrive\05_Data\052_District_Pricenhage\0521_HeatPump"+"\HP_consumption_Sum.csv", index=True)
f = open(r"C:\Users\20190285\surfdrive\05_Data\052_District_Pricenhage\0521_HeatPump"+"\HeatPump.pkl","wb")
pickle.dump(HeatPump,f)
f.close()



# # check
# HeatPump[123].loc["2017-03-05 12:45:00"]
# HeatPump[124].loc["2017-12-30 12:30:00"]

# (SumConsumption.loc["2017-01-26 06:30:00"] + SumConsumption.loc["2017-01-26 06:45:00"] \
# + SumConsumption.loc["2017-01-26 05:45:00"] + SumConsumption.loc["2017-01-26 07:00:00"])/15*60
