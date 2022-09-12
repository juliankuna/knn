from matplotlib.colors import Colormap
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns

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

    # Unique category labels: 'D', 'F', 'G', ...
    color_labels = df['clase'].unique()

    # List of RGB triplets
    rgb_values = sns.color_palette("Set2", 8)

    # Map label to RGB
    color_map = dict(zip(color_labels, rgb_values))
    #df.plot(x='x', y='y', kind = 'scatter')
    plt.scatter(df['x'], df['y'], c=df['clase'].map(color_map))
    plt.show()
