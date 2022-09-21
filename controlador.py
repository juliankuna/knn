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
from typing import Any, List

#(x1,y1) punto de origen, (x2,y2) punto destino
def CalcularDistanciaEuclidea(x1:float, y1:float, x2:float, y2:float) -> float:
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

def BuscarMinimoEnElDataset() -> Punto:
    xArrayPoints = [f.x for f in dataSet]
    yArrayPoints = [f.y for f in dataSet]
    return Punto(min(xArrayPoints), min(yArrayPoints))

def BuscarMaximoEnElDataset()-> Punto:
    xArrayPoints = [f.x for f in dataSet]
    yArrayPoints = [f.y for f in dataSet]
    return Punto(max(xArrayPoints), max(yArrayPoints))

def GetClasesEnDataSet(todasLasClases)->List[int]:
    listaClases:List[int] = []
    for clase in todasLasClases:
        if clase not in listaClases:
            listaClases.append(clase)
    return listaClases

def IniciarAlgoritmo ():
    try:
        dataSet.clear()        
        datosString=CargarArchivo();       

        #Creamos matriz de valores 0 ceros 
        matriz= np.zeros((len(datosString)-1,3))

        n=1             #Eliminamos la primer linea
        while n<len(datosString):
            fila=datosString[n].split(',');
            for j in range(2):                
                matriz [n-1][j] = float(fila[j].strip('\n'))
            matriz [n-1][2] = int(fila[2].strip('\n'))
            #cargamos una grilla con cada uno de los puntos (x,y,clase,distancia)
            dataSet.append(Dato(float(fila[0]), float(fila[1]),int(fila[2])))        
            n=n+1   
        #contar la cantidad de clases
        clasesEnElDataset = GetClasesEnDataSet([f.clase for f in dataSet])

        #Separando todos los puntos del dataset y agrupandolos por su clase
        clasesConSusPuntos= []
        for clase in clasesEnElDataset:
            listaPuntos: list[Punto] = [Punto(f.x,f.y) for f in dataSet if f.clase == clase]
            clasesConSusPuntos.append(ClaseConPuntos(clase,listaPuntos))

        #Cargando el dataSet de entrenamiento y el de prueba
        dataSetEntrenamiento.clear()
        dataSetPrueba:List[Dato] = [] #linea necesaria o sinó el dataSetPrueba.clear() tiraba error
        dataSetPrueba.clear()
        for claseConPuntos in clasesConSusPuntos:
            cantidadPuntos=len(claseConPuntos.puntos)
            porcentajeEntrenamiento=0.8
            criterioParada= round(porcentajeEntrenamiento * cantidadPuntos)
            cont=0
            for punto in claseConPuntos.puntos:
                if cont < criterioParada: 
                    dataSetEntrenamiento.append(Dato(float(punto.x),float(punto.y), int(claseConPuntos.clase)))
                    cont+=1
                else:
                    dataSetPrueba.append(Dato(float(punto.x),float(punto.y), int(claseConPuntos.clase)))
            
        
        
        #GENERAR GRILLA
        GenerarGrilla()   
    except Exception as e:
        messagebox.showwarning(message="Houston, we have a problem..." + str(e), title="Alerta")
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
    plt.title('Gráfico de puntos con k='+str(valorK.get()))
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
    input_k = Scale(frame1, from_=1, to=15, orient=HORIZONTAL,troughcolor='red',variable=valorK, length= 200)
    input_k.set(5)
    input_k.grid(row = 3,column=1, pady=0,sticky='s', padx = 0)


    botonIniciar = Button(frame1, text='Iniciar algoritmo',command=IniciarAlgoritmo)
    botonIniciar.grid(row=6,column=1,sticky='e',padx=0,pady=10)
    buttonDataSet = Button(frame1, text = "Seleccionar DATASET", width=15,command = setPathFile)
    buttonDataSet.grid(row=1,column=1,sticky='e',padx=5,pady=15)

    frame=Frame(root,width=800,height=600)
    frame.grid(row=1,column=1,padx=20,pady=20)

#/////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////
def BuscarVecinos(punto:Punto) -> List[dict[int, int, int, list[float]]]:
        #Obtenemos todas las distancias a los puntos
        listaDistancias : List[float] = [CalcularDistanciaEuclidea(float(punto[0]),float(punto[1]), d.x, d.y) for d in dataSetEntrenamiento]
        puntoConDistancias:List[DatoConDistancia] = []
        i=0
        for d in dataSetEntrenamiento:
            puntoConDistancias.append( 
                                {
                                    "x":d.x,
                                    "y":d.y,
                                    "clase":d.clase,
                                    "distancia":listaDistancias[i]
                                })
            i=i+1
        
        #ordenamos por proximidad calculada usando la distancia euclidea
        puntoConDistancias = sorted(puntoConDistancias, key=lambda d : d["distancia"])
        
        puntoConDistancias.pop(0) #eliminamos el primero al ser distancia contra el mismo punto
        
        #Retornamos los k vecinos mas próximos según la distancia euclidea
        return puntoConDistancias[:valorK.get()]

def ClaseMasFrecuente(List) -> int:
    masFrecuente = 0
    clase = List[0]        
    for i in List:
        frecuenciaDeLaClase = List.count(i)
        if(frecuenciaDeLaClase > masFrecuente):
            masFrecuente = frecuenciaDeLaClase
            clase = i
    return clase

def DefinirClase(punto) -> int:
        listaVecinos:List[Any] = BuscarVecinos(punto)
        #listamos las clases de todos los k vecinos
        ClasesVecinos:List[int] = [n["clase"] for n in listaVecinos] 
        return ClaseMasFrecuente(ClasesVecinos)

def GenerarGrilla():
        #Definiendo maximos y minimos para la grilla
        PuntoMaximo:Punto = BuscarMaximoEnElDataset()
        PuntoMinimo:Punto = BuscarMinimoEnElDataset()        
        xMin= PuntoMinimo.x - 1
        xMax= PuntoMaximo.x + 1
        yMin= PuntoMinimo.y - 1
        yMax= PuntoMaximo.y + 1
        
        #Determinando rangos para los vectores de coordenadas x e y.
        vectorX = np.arange(xMin, xMax, 0.5)
        vectorY = np.arange(yMin, yMax, 0.5)

        #Devolvemos una matriz de coordenadas a partir de los vectores de coordenadas
        grid_x, grid_y = np.meshgrid(vectorX, vectorY)

        ListaClasesVecinos : List[Dato] = []
        for n in range( len( grid_x.flatten() ) ):
            punto = np.array( [grid_x.flatten()[n], grid_y.flatten()[n]] )
            ListaClasesVecinos.append(DefinirClase(punto))

        fig = plt.figure()
        fig.suptitle(f"kNN con K={valorK.get()}")
        
        GrillaConDataset = fig.add_subplot(122)
        Grilla = fig.add_subplot(121)

        #Gráfico de la grilla
        GrillaConDataset.scatter(grid_x,grid_y,
                    c = ListaClasesVecinos,
                    alpha = 0.4,
                    cmap= "tab10",
                    marker="s",
                    label="Grilla")

        #Gráfico del dataset
        GrillaConDataset.scatter([d.x for d in dataSetEntrenamiento],
                    [d.y for d in dataSetEntrenamiento],
                    c = [d.clase for d in dataSetEntrenamiento],
                    alpha = 0.9,
                    cmap= "tab10",
                    marker="X",
                    label="DataSet",
                    linewidths=5,
                    linewidth=3)

        Grilla.pcolormesh(grid_x,grid_y,
                    np.asarray(ListaClasesVecinos).reshape(grid_x.shape),
                    shading="auto",
                    alpha = 1,
                    cmap= "tab10")

        plt.title(f"Resultado kNN con K={valorK.get()}")

        GrillaConDataset.set_title('Grilla con DataSet')

        Grilla.set_title('Grilla')
        Grilla.set_xlabel('Eje x')
        Grilla.set_ylabel('Eje y')
        fig.canvas.manager.set_window_title('IA II - Gráfico kNN')
        GrillaConDataset.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=5)                   
        plt.show()
#/////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////
root=Tk()
root.title('Algoritmo kNN - Kunaschik, Saucedo, Zitelli');
root.resizable(0,0)
root.geometry('750x450')

dataSet: List[Dato] = []
dataSetPrueba:List[Dato] = []
dataSetEntrenamiento: List[Dato] = []

clasesConSusPuntos:List[ClaseConPuntos] = []

nombreArchivo=StringVar()
nombreArchivo.set('')
ubicacionArchivo=StringVar()
ubicacionArchivo.set('')
valorK = IntVar()
valorKOptimo = IntVar()
GraficarVistaInicial()


root.mainloop()
