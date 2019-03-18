import sys
print(sys.version)
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


# Path Definition
path = r"C:\Users\20190285\surfdrive\03_SharedFolders\Shalika_Waqas_Julien\JEMData\HP_consumption"
filename = r"\HP_consumption_cleaned_customer_id_" #files from ID 123 to 179

# Initialize
HeatPump = dict()
ID = 123

# Reading excel files
while ID < 180:
    data = pd.read_excel(path + filename + str(ID) + '.xlsx')
    HeatPump[ID] = data[data.flow == 9].drop(['customer_id', 'flow'], axis=1).reset_index().rename(index=str, columns={"id": "DOI"})
    ID += 1
    if ID == 134:
        ID += 1
    elif ID == 60:
        ID = 69
    elif ID == 71:
        ID = 78
    print(ID)


