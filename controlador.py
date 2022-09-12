import pandas as pd
import os
import glob
  
#CONSUMIENDO LOS DATASETS
#Basado en https://es.acervolima.com/como-leer-todos-los-archivos-de-excel-en-un-directorio-como-pandas-dataframe/

path = os.getcwd()
print(path)
csv_files = glob.glob(os.path.join(path + "\datasets", "*.csv"))  
  
# loop over the list of csv files
for f in csv_files:
    
    # read the csv file
    df = pd.read_csv(f)
      
    # print the location and filename
    print('Location:', f)
    print('File Name:', f.split("\\")[-1])
      
    # print the content
    print('Content:')
    #display(df)
    print(df)