from operator import length_hint
from turtle import width
import matplotlib.pyplot as plt
import numpy as np
from io import open
from cProfile import label
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import math
import pandas as pd
from modelos import *

#(x1,y1) punto de origen, (x2,y2) punto destino
def CalcularDistanciaEuclidea(x1:float, y1:float, x2:float, y2:float):
    return round(math.sqrt(( (x2-x1)**2 ) + ( (y2-y1)**2 )),2)

def CargarArchivo ():
    #Abrimos el archivo en modo de solo lectura... leemos las lineas y cerramos el archivo
    texto=''
    try:
        archivo=open(ubicacionArchivo.get(),'r');
        texto=archivo.readlines();
        archivo.close();
    except Exception as e:
        messagebox.showwarning(message="Error al cargar los datos. Verifique que sea correcto el archivo.", title="Alerta")
    finally:
        return texto    

def IniciarAlgoritmo ():
    try:
        texto=CargarArchivo();

        #Creamos matriz de valores 0 ceros 
        matriz = np.zeros((len(texto)-1,3))
        print('*******************************Matriz inicaaaaaaaal:')
        print(matriz)

        n=1             #Eliminamos la primer linea
        while n<len(texto):
            var=texto[n].split(',');
            for j in range(3):
                matriz [n-1][j] = float(var[j].strip('\n'))
            n=n+1
        
        print('*******************************Matriz finaaaaaaaal:')
        print(matriz)
    except Exception as e:
        messagebox.showwarning(message="Houston, we have a problem", title="Alerta")
        return
    #Filtro de color
    color_filt=[]
    color = ['red','green','blue']
    for line in matriz:
        if line[2]==0:
            color_filt.append(color[0])
        elif line[2]==1:
            color_filt.append(color[1])
        elif line[2]==2:
            color_filt.append(color[2])

    plt.close()
    plt.scatter(matriz[:,0],matriz[:,1],color=color_filt)
    plt.xlabel('Eje x')
    plt.ylabel('Eje y')
    plt.title('Gráfico de puntos con k='+str(var_k.get()))
    plt.show()

def setPathFile():
    nombreConRuta = filedialog.askopenfilename(title="Elegir un DataSet",filetypes = (("excel files",".csv"),("all files",".*")));
    nombreInvertido=invertir_cadena(nombreConRuta)
    #invertimos la cadena y spliteamos para separar el nombre de la ruta y que el nombre quede en la posición inicial de la lista
    palabras=nombreInvertido.split('/') 
    #invertimos la primer palabra de la lista, la cual es el nombre invertido del archivo, para setearlo correctamente
    ubicacionArchivo.set(nombreConRuta);
    nombreArchivo.set(invertir_cadena(palabras[0]));

def invertir_cadena(cadena):
    return cadena[::-1]

def GraficarVistaInicial ():
    frame1=Frame(root,width=800,height=600)
    frame1.grid(row=0,column=0,ipadx=10,ipady=10)
    cuadrotexto = Entry(frame1,textvariable=nombreArchivo,width=33)
    Label(frame1,text='Valores Iniciales ',fg='black',font=('Comic Sans MS',10)).grid(row=0,column=0,sticky='nw',padx=0,pady=0)

    cuadrotexto.grid(row=2,column=1,padx=0,pady=0)
    cuadrotexto.config(fg='red',justify='center')
    Label(frame1,text='Nombre Archivo: ',fg='black',font=('Comic Sans MS',10)).grid(row=2,column=0,padx=5,pady=0)
    frame1.config(bd=2)
    frame1.config(relief='solid')

    Label(frame1, text="Valor K: ").grid(row=3, column=0,sticky='se', pady=0, padx = 0)
    input_k = Scale(frame1, from_=1, to=15, orient=HORIZONTAL,troughcolor='red',variable=var_k, length= 200)
    input_k.set(5)
    input_k.grid(row = 3,column=1, pady=0,sticky='s', padx = 0)


    botonIniciar = Button(frame1, text='Iniciar algoritmo',command=IniciarAlgoritmo)
    botonIniciar.grid(row=6,column=1,sticky='e',padx=0,pady=10)
    buttonDataSet = Button(frame1, text = "Seleccionar DATASET", width=15,command = setPathFile)
    buttonDataSet.grid(row=1,column=1,sticky='e',padx=5,pady=15)

    frame=Frame(root,width=800,height=600)
    frame.grid(row=1,column=1,padx=20,pady=20)

root=Tk()
root.title('Algoritmo kNN - Kunaschik, Saucedo, Zitelli');
root.resizable(0,0)
root.geometry('750x450')

nombreArchivo=StringVar()
nombreArchivo.set('')
ubicacionArchivo=StringVar()
ubicacionArchivo.set('')
var_k = IntVar()

GraficarVistaInicial()

root.mainloop()
