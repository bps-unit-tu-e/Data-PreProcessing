import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from functools import reduce
import pickle

print("Temp data Read phase \n")
########################################################################################################################
###                                                     Read                                                        ####
########################################################################################################################

# Path Definition
path = r"C:\Users\20190285\surfdrive\03_SharedFolders\Shalika_Waqas_Julien\JEMData\HP_temperature"
filename = r"\hp_temperature_cleaned_customer_" #files from ID 123 to 179

# Initialize
TempDic = dict()
ID = 123

# Reading excel files
print("Looping over files:")
while ID < 180: #180 is end / 125 for test
    print(ID)
    data = pd.read_excel(path + filename + str(ID) + '.xlsx')

    # Date Time Manip
    data['time_start'] = pd.to_datetime(data['time_start'])

    # Heat Pump Dict completing
    TempDic[ID] = data.drop(['customer_id', 'fhr', 'hps', 'ind', 'ofc', 'out', 'usr', 'fhr_boiler'], axis=1)\
        .rename(index=str, columns={"fhr_vloertemperatuur": "floortemp"}).rename(index=str, columns={"id": "DOI"}).set_index('time_start')

    # Preprocessing - Define duplicate values as averages of the two & remove duplicate
    TempDic[ID][TempDic[ID].index.duplicated(keep='last')] = (TempDic[ID][TempDic[ID].index.duplicated(keep='first')] +
                                                                  TempDic[ID][TempDic[ID].index.duplicated(keep='last')]) / 2
    TempDic[ID] = TempDic[ID][~TempDic[ID].index.duplicated(keep='first')]

    # File ID - skip missing files
    ID += 1
    if ID == 134:
        ID += 1
    elif ID == 160:
        ID = 169
    elif ID == 171:
        ID = 177


########################################################################################################################
###                                                 Preprocess                                                      ####
########################################################################################################################
print(" \n Data PreProcessing phase \n")

# Replace 0 values with None values
for id in list(TempDic):
    # TempDic[id].floortemp[TempDic[id].floortemp == 0] = None
    TempDic[id].loc[TempDic[id].floortemp == 0] = None
    if TempDic[id].floortemp.isnull().all():    #if all values are NaN, delete data
        del TempDic[id]


# Fill out missing time stamps by None values
print("Missing data loop:")

id_ref = list(TempDic.keys())[0]
date_rng = pd.date_range(start=TempDic[id_ref].index[0], end=TempDic[id_ref].index[-1], freq='15min')
df_ref = pd.DataFrame(date_rng, columns=['time_start']).set_index('time_start')

for id in TempDic:
    print(id)

    # Index differences identification
    IndexNone = df_ref.index.difference(TempDic[id].index)
    size_diff = df_ref.index.difference(TempDic[id].index).size
    # Creat pd dataframes from differences
    NoneDataFrame = pd.DataFrame({'DOI': ["None"]*size_diff,
                                  'floortemp': [None]*size_diff,
                                  'time_start': list(IndexNone)}).set_index('time_start')
    # Concat Reference dataframe with other one
    TempDic[id] = pd.concat([TempDic[id], NoneDataFrame]).sort_index()


# # Data Size check
# MaxDataSize = []
# for id in TempDic:
#     MaxDataSize.append(TempDic[id].floortemp.values.size)


print("Data interpolation")
# Missing Data interpolation
for id in TempDic:
    #TempDic[id].floortemp = TempDic[id].floortemp.astype(float)
    TempDic[id].floortemp = TempDic[id].floortemp.interpolate(method='linear', axis=0).ffill().bfill()



########################################################################################################################
###                                            Data Manipulation                                                    ####
########################################################################################################################

print("\n Data manipulation phase \n")

# Summing consumption
SumTemp = pd.DataFrame
SumTemp = TempDic[list(TempDic.keys())[0]].drop('DOI', axis=1)
for id in list(TempDic.keys())[1:]:
    SumTemp = SumTemp + TempDic[id].drop('DOI', axis=1)
AvgTemp = SumTemp.apply(lambda x: x/len(TempDic.keys()))


# # Plotting temp
# plt.close('all')
# TempDic[124].floortemp.plot()
# AvgTemp.plot()


########################################################################################################################
###                                                Data Saving                                                      ####
########################################################################################################################

print("\n Data Saving phase \n")
AvgTemp.to_csv(r"C:\Users\20190285\surfdrive\05_Data\052_District_Pricenhage\0521_HeatPump"+"\HP_floortemp_avg.csv", index=True)
f = open(r"C:\Users\20190285\surfdrive\05_Data\052_District_Pricenhage\0521_HeatPump"+"\TempDic.pkl","wb")
pickle.dump(TempDic,f)
f.close()



# # check
# TempDic[123].loc["2017-09-08 14:45:00"]
# TempDic[123].loc["2017-12-31 16:45:00"]
# TempDic[124].loc["2017-12-30 12:30:00"]

