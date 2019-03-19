import sys
print(sys.version)
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from functools import reduce

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
MaxDataSize = []

# Reading excel files
print("Looping over files:")
while ID < 125: #180 is end / 125 for test
    data = pd.read_excel(path + filename + str(ID) + '.xlsx')

    # Date Time Manip
    data['time_start'] = pd.to_datetime(data['time_start'])

    # Heat Pump Dict completing
    HeatPump[ID] = data[data.flow == 9].drop(['customer_id', 'flow'], axis=1).set_index('time_start').rename(index=str, columns={"id": "DOI"})#.drop_duplicates(keep='first')

    # Preprocessing - Define duplicate values as averages of the two & remove duplicate
    HeatPump[ID][HeatPump[ID].index.duplicated(keep='last')] = (HeatPump[ID][HeatPump[ID].index.duplicated(keep='first')] +
                                                                  HeatPump[ID][HeatPump[ID].index.duplicated(keep='last')]) / 2
    HeatPump[ID] = HeatPump[ID][~HeatPump[ID].index.duplicated(keep='first')]

    # File ID - skip missing files
    ID += 1
    if ID == 134:
        ID += 1
    elif ID == 60:
        ID = 69
    elif ID == 71:
        ID = 78
    print(ID)


########################################################################################################################
###                                                 Preprocess                                                      ####
########################################################################################################################
print(" \n Data PreProcessing phase \n")

# Fill out missing time stamps by None values
print("1st missing data loop:")

id_ref = list(HeatPump.keys())[0]

for id in list(HeatPump.keys())[1:]:
    print(id)

    # Index differences identification
    IndexNone = HeatPump[id].index.difference(HeatPump[id_ref].index)
    size_diff = HeatPump[id].index.difference(HeatPump[id_ref].index).size
    # Creat pd dataframes from differences
    NoneDataFrame = pd.DataFrame({'DOI': ["None"]*size_diff,
                                  'consumption': [None]*size_diff,
                                  'time_start': list(IndexNone)}).set_index('time_start')
    # Concat Reference dataframe with other one
    HeatPump[id_ref] = pd.concat([HeatPump[id_ref], NoneDataFrame]).sort_index()

print("2nd missing data loop:")
for id in list(HeatPump.keys())[1:]:
    print(id)

    # Index differences identification
    IndexNone = HeatPump[id_ref].index.difference(HeatPump[id].index)
    size_diff = HeatPump[id_ref].index.difference(HeatPump[id].index).size
    # Creat pd dataframes from differences
    NoneDataFrame = pd.DataFrame({'DOI': ["None"]*size_diff,
                                  'consumption': [None]*size_diff,
                                  'time_start': list(IndexNone)}).set_index('time_start')
    # Concat Reference dataframe with other one
    HeatPump[id] = pd.concat([HeatPump[id], NoneDataFrame]).sort_index()


## Data Size check
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
SumList = []
for id in HeatPump:
    SumList.append(HeatPump[id].drop('DOI', axis=1))
SumConsumption = reduce(pd.DataFrame.add, SumList)

# Plotting summed demand
plt.close('all')
HeatPump[123].consumption.plot()






# # check
# HeatPump[123].loc["2017-09-08 14:45:00"]
# HeatPump[124].loc["2017-12-30 12:30:00"]

# # Summing demand - size conflict => sum demand function of time stamp
# SumConsumption = [0]*max(MaxDataSize)
# for id, id_next in zip(list(HeatPump.keys()), list(HeatPump.keys())[1:]):
#     print(id, id_next)
#     SumConsumption = HeatPump[id].drop('DOI', axis=1).add(HeatPump[id_next].drop('DOI', axis=1), fill_value=0)