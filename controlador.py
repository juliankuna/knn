from ctypes import alignment
from itertools import tee
from operator import length_hint
import threading
import tkinter
from turtle import width
from matplotlib.dates import DAILY
import matplotlib.pyplot as plt
import numpy as np
from io import open
from cProfile import label
from tkinter import *
from tkinter import ttk
import time
from tkinter import messagebox
from tkinter import filedialog
import math
#import pandas as pd
from modelos import *
from vistas import *
from typing import Any, List, Counter
import matplotlib.patches as mpatches

#(x1,y1) punto de origen, (x2,y2) punto destino
def CalcularDistanciaEuclidea(x1:float, y1:float, x2:float, y2:float) -> float:
    a=np.array((x1,y1))
    b=np.array((x2,y2))
    distancia = np.sqrt(np.sum(np.square(a-b)))
    return distancia

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

def CargarDataSet(stringDatos:List[str]) -> List[Dato]:
    dataSet: List[Dato] = []

    n=1             #Eliminamos la primer linea
    while n<len(stringDatos):
        fila=stringDatos[n].split(',');
        #cargamos una grilla con cada uno de los puntos (x,y,clase,distancia)
        dataSet.append(Dato(float(fila[0]), float(fila[1]),int(fila[2])))        
        n=n+1   
    return dataSet

#Se dej?? de considerar por lo charlado con el profesor Karanik en la clase del 22/09/2022 de utilizar validaci??n cruzada de todo el dataSet
def SepararDataSetEnEntrenamientoyPrueba():
    #contar la cantidad de clases
    clasesEnElDataset = GetClasesEnDataSet([f.clase for f in dataSet])
    
    #Separando todos los puntos del dataset y agrupandolos por su clase
    clasesConSusPuntos= []
    for clase in clasesEnElDataset:
        listaPuntos: list[Punto] = [Punto(f.x,f.y) for f in dataSet if f.clase == clase]
        clasesConSusPuntos.append(ClaseConPuntos(clase,listaPuntos))

    #Cargando el dataSet de entrenamiento y el de prueba
    dataSetEntrenamiento.clear()
    dataSetPrueba:List[Dato] = [] #linea necesaria o sin?? el dataSetPrueba.clear() tiraba error
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

def BuscarVecinos(k:int, punto:Punto, dataSet:List[Dato]) -> List[dict[int, int, int, list[float]]]:
        #Obtenemos todas las distancias a los puntos
        listaDistancias : List[float] = [CalcularDistanciaEuclidea(float(punto.x),float(punto.y), d.x, d.y) for d in dataSet]
        puntoConDistancias:List[DatoConDistancia] = []
        i=0
        for d in dataSet:
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
                
        #Retornamos los k vecinos mas pr??ximos seg??n la distancia euclidea
        return puntoConDistancias[:k]

def ClaseMasFrecuente(ListaClasesVecinos) -> int:
    cantidadClases = Counter(ListaClasesVecinos)   #cantidadClases = Counter({2: 11, 1: 3}) = ({clase: vecesRepetida})
    ClaseMasRepetida = max(cantidadClases,key=cantidadClases.get)
    return ClaseMasRepetida

def DefinirClase(punto) -> int:
        listaVecinos:List[Any] = BuscarVecinos(punto)
        #listamos las clases de todos los k vecinos
        ClasesVecinos:List[int] = [n["clase"] for n in listaVecinos] 
        return ClaseMasFrecuente(ClasesVecinos)

def CargarMatrizPuntos(datosString):
    #Creamos matriz de valores 0 ceros 
    matriz= np.zeros((len(datosString)-1,3))

    n=1             #Eliminamos la primer linea
    while n<len(datosString):
        fila=datosString[n].split(',');
        for j in range(2):                
            matriz [n-1][j] = float(fila[j].strip('\n'))
        matriz [n-1][2] = int(fila[2].strip('\n'))
        #cargamos una grilla con cada uno de los puntos (x,y,clase,distancia)
        n=n+1
    return matriz   

def CargarMatrizKFold(dataSet:List[Dato]):
    longitud=(len(dataSet))
    matrizDistancias= np.zeros((longitud,longitud), float)
    dType = [('clase', int), ('distancia', float)]
    matrizPuntos=np.empty((longitud, longitud),dtype=dType)
    for i in range (0, longitud): #numero de filas
        dato=dataSet[i]
        for j in range (0,longitud): #numero de columnas
            distancia=0
            if (j!=i):
                vecino=dataSet[j]
                if(matrizDistancias[i][j]==0 and matrizDistancias[j][i]==0 ):
                    distancia=CalcularDistanciaEuclidea(dato.x,dato.y,vecino.x,vecino.y)
                    matrizDistancias[i][j]=distancia
                    matrizDistancias[j][i]=distancia
                else:
                    distancia=matrizDistancias[j][i]                
                matrizPuntos[i][j]=(vecino.clase,distancia)
            else:
                matrizPuntos[i][j]=(dato.clase,distancia)
    


    return matrizPuntos

def GraficarDatosDatasetsOptimos(datasetKnn, matrizDataSetKnn, datasetPonderado, matrizDataSetKnnPonderado):
    global valorKOptimo
    global valorKOptimoPonderado
    global valorKMax

    #Filtro de color
    color_filt=CargarFiltroColores(matrizDataSetKnn) 
    todasLasClasesDelDataset=[f.clase for f in datasetKnn]
    patches=CargarPatches(todasLasClasesDelDataset)
    
    fig = plt.figure()
    graficoK = fig.add_subplot(121)
    graficoKPonderado = fig.add_subplot(122)

    puntosX = [f.x for f in datasetKnn]
    puntosY = [f.y for f in datasetKnn]    
    fig.suptitle(f'Gr??fica comparativa para valores k comprendidos entre 1 y {valorKMax}')
    graficoK.scatter(puntosX,puntosY,color=color_filt,label="Datos")
    graficoK.set_xlabel('Eje x')
    graficoK.set_ylabel('Eje y')
    graficoK.legend(handles=patches)
    graficoK.set_title(f'Gr??fico dataset con k ??ptimo ={valorKOptimo}')

    #Grafico knn ponderado
    color_filt2=CargarFiltroColores(matrizDataSetKnnPonderado) 
    todasLasClasesDelDataset=[f.clase for f in datasetPonderado]
    patches2=CargarPatches(todasLasClasesDelDataset)
    # xPuntos = [f.x for f in datasetPonderado]
    # yPuntos = [f.y for f in datasetPonderado]  
    graficoKPonderado.scatter(puntosX,puntosY,color=color_filt2,label="Datos")
    graficoKPonderado.set_xlabel('Eje x')
    graficoKPonderado.set_ylabel('Eje y')
    graficoKPonderado.legend(handles=patches2)
    graficoKPonderado.set_title(f'Gr??fico dataset con k ponderado ??ptimo ={valorKOptimoPonderado}')
    
    plt.ion()
    plt.show()

def CargarFiltroColores(matrizDataset):
    global colors
    global badColors
    #colors = ['pink','lightgreen','lightblue','orange','lightpurple','lightgray']
    color_filt = []
    for line in matrizDataset:
        if line[2]==0:
            color_filt.append(colors[0])
        elif line[2]==1:
            color_filt.append(colors[1])
        elif line[2]==2:
            color_filt.append(colors[2])
        elif line[2]==3:
            color_filt.append(colors[3])
        elif line[2]==4:
            color_filt.append(colors[4])
        elif line[2]==5:
            color_filt.append(colors[5])  
        elif line[2]==-1: #si clase =-1 significa que hubo una mala clasificaci??n
            color_filt.append(badColors[0]) 
        elif line[2]==-2: #si clase =-2 significa que no pudo clasificar
            color_filt.append(badColors[1])
    return color_filt

def CargarPatches(todasLasClasesDelDataset):
    global badColors
    global colors
    clasesDelDataset=GetClasesEnDataSet(todasLasClasesDelDataset)
    clasesDelDataset.sort(reverse=True)
    counterClases= Counter(todasLasClasesDelDataset)
    malasClasificaciones:int = counterClases[-1]
    indeterminaciones:int = counterClases[-2]
    patches= []
    for i in range(0,len(clasesDelDataset)):
        if(clasesDelDataset[i] >= 0 ):
            patch = mpatches.Patch(color=colors[clasesDelDataset[i]], label=f'Clase {clasesDelDataset[i]}: #{counterClases[clasesDelDataset[i]]}')      
            patches.append(patch)
        else:
            break

    patches.append(mpatches.Patch(color=badColors[0], label=f'Malas clasificaciones: #{malasClasificaciones}'))
    patches.append(mpatches.Patch(color=badColors[1], label=f'Indeterminaciones: #{indeterminaciones}'))
    return patches

def OrdenarColumnasMatrizKFold(matrizKFold,longitudDataSet):
    dType = [('clase', int), ('distancia', float)]
    #Ordenando la matriz para las validaciones cruzadas
    matrizColumnasOrdenadas=np.empty((0,longitudDataSet),dtype=dType)
    for j in range(0, longitudDataSet):
        columna=np.empty(longitudDataSet,dtype=dType)
        for i in range(0, longitudDataSet):
            columna[i]=(matrizKFold[j][i])
        columna=np.sort(columna, order='distancia')      
        matrizColumnasOrdenadas=np.append(matrizColumnasOrdenadas,columna)
    return matrizColumnasOrdenadas

def BarraDeProgreso():
    global my_progress
    global progressMensaje
    my_progress = ttk.Progressbar(frame1, orient=HORIZONTAL, length=300, mode='determinate')     
    my_progress.grid(row=7, column=1,padx=10, pady=5, sticky='e')
    progressMensaje = Label(frame1,text=' ', font=('Comic Sans MS',8))
    progressMensaje.grid(row=8, column=1,padx=10,pady=5, sticky='e')
    progressMensaje['text'] = "Cargando..."
    my_progress.start(10)        

def BarraDeProgreso2():
    global my_progress2
    global progressMensaje2
    my_progress2 = ttk.Progressbar(frame1, orient=HORIZONTAL, length=300, mode='determinate')     
    my_progress2.grid(row=12, column=1,padx=10, pady=5, sticky='e')
    progressMensaje2 = Label(frame1,text=' ', font=('Comic Sans MS',8))
    progressMensaje2.grid(row=13, column=1,padx=10,pady=5, sticky='e')
    progressMensaje2['text'] = "Cargando..."
    my_progress2.start(10)   

def ActualizarMensajeProgreso():
    global banderaFin
    global progressMensaje
    if (banderaFin == False):
        if (progressMensaje['text'] == "Cargando..."):
            progressMensaje['text'] = "Actualizando los pesos de las conexiones..."
        elif (progressMensaje['text'] == "Actualizando los pesos de las conexiones..."):
            progressMensaje['text'] = "Vaciando cuentas bancarias..."
        elif (progressMensaje['text'] == "Vaciando cuentas bancarias..."):
            progressMensaje['text'] = "Buscando los vectores de soporte..."    
        elif (progressMensaje['text'] == "Buscando los vectores de soporte..."):
            progressMensaje['text'] = "Calculando las verosimilitudes..."
        elif (progressMensaje['text'] == "Calculando las verosimilitudes..."):
            progressMensaje['text'] = "Agitando las neuronas..."
        elif (progressMensaje['text'] == "Agitando las neuronas..."):
            progressMensaje['text'] = "Calculando las probabilidades marginales..."
        elif (progressMensaje['text'] == "Calculando las probabilidades marginales..."):
            progressMensaje['text'] = "Evaluando la coherencia del conjunto de reglas..."
        elif (progressMensaje['text'] == "Evaluando la coherencia del conjunto de reglas..."):
            progressMensaje['text'] = "Calculando la vecindad de las neuronas..."
        elif (progressMensaje['text'] == "Calculando la vecindad de las neuronas..."):
            progressMensaje['text'] = "Calculando el error del patr??n..."
        elif (progressMensaje['text'] == "Calculando el error del patr??n..."):
            progressMensaje['text'] = "Aprobando Inteligencia Artificial 2..."
        elif (progressMensaje['text'] == "Aprobando Inteligencia Artificial 2..."):
            progressMensaje['text'] = "Pagando impuestos provinciales en rentas..."
        elif (progressMensaje['text'] == "Pagando impuestos provinciales en rentas..."):
            progressMensaje['text'] = "Cargando"
        root.after(3000, ActualizarMensajeProgreso)

def ActualizarMensajeProgreso2():
    global banderaFin2
    global progressMensaje2
    if (banderaFin == False):
        if (progressMensaje2['text'] == "Cargando..."):
            progressMensaje2['text'] = "Actualizando los pesos de las conexiones..."
        elif (progressMensaje2['text'] == "Actualizando los pesos de las conexiones..."):
            progressMensaje2['text'] = "Vaciando cuentas bancarias..."
        elif (progressMensaje2['text'] == "Vaciando cuentas bancarias..."):
            progressMensaje2['text'] = "Buscando los vectores de soporte..."    
        elif (progressMensaje2['text'] == "Buscando los vectores de soporte..."):
            progressMensaje2['text'] = "Calculando las verosimilitudes..."
        elif (progressMensaje2['text'] == "Calculando las verosimilitudes..."):
            progressMensaje2['text'] = "Agitando las neuronas..."
        elif (progressMensaje2['text'] == "Agitando las neuronas..."):
            progressMensaje2['text'] = "Calculando las probabilidades marginales..."
        elif (progressMensaje2['text'] == "Calculando las probabilidades marginales..."):
            progressMensaje2['text'] = "Evaluando la coherencia del conjunto de reglas..."
        elif (progressMensaje2['text'] == "Evaluando la coherencia del conjunto de reglas..."):
            progressMensaje2['text'] = "Calculando la vecindad de las neuronas..."
        elif (progressMensaje2['text'] == "Calculando la vecindad de las neuronas..."):
            progressMensaje2['text'] = "Calculando el error del patr??n..."
        elif (progressMensaje2['text'] == "Calculando el error del patr??n..."):
            progressMensaje2['text'] = "Aprobando Inteligencia Artificial 2..."
        elif (progressMensaje2['text'] == "Aprobando Inteligencia Artificial 2..."):
            progressMensaje2['text'] = "Pagando impuestos provinciales en rentas..."
        elif (progressMensaje2['text'] == "Pagando impuestos provinciales en rentas..."):
            progressMensaje2['text'] = "Cargando"
                
        root.after(3000, ActualizarMensajeProgreso2)

def PrimerPaso():
    #Separamos la ejecuci??n en 2 hilos, el principal que va a estar corriendo la progressbar 
    #y uno secundario donde se va a correr el algoritmo en segundo plano
    global banderaFin
    if (banderaFin): #significa que ya se hizo click en el bot??n Iniciar Algoritmo anteriormente, asi que primero tenemos que destruir los botones de funcionalidades antes de correr de nuevo el algoritmo
        global botonKOptimos
        global botonGraficoOriginal
        global botonGraficoKOptimos
        global botonTablaAciertosK
        botonKOptimos.destroy()
        botonGraficoKOptimos.destroy()
        botonTablaAciertosK.destroy()
    BarraDeProgreso()
    hiloDelAlgoritmo=threading.Thread(target=IniciarAlgoritmo1)
    hiloDelAlgoritmo.start()

def PrimerPaso2():
    global banderaFin2
    global botonGraficoK
    global dataSetOriginal
    global valorKElegido
    banderaNumeroKelegido = False
    try:
        valorKElegido = int(entryK.get())
        if (valorKElegido < 1):
            messagebox.showwarning(message=f"Debe ingresar un n??mero mayor o igual a 1 y menor a la cantidad de datos del dataset ({len(dataSetOriginal)})", title="Alerta")
            banderaNumeroKelegido = False
        else:
            if (valorKElegido > len(dataSetOriginal)-1):
                messagebox.showwarning(message=f"Debe ingresar un n??mero mayor o igual a 1 y menor a la cantidad de datos del dataset ({len(dataSetOriginal)})", title="Alerta")
                banderaNumeroKelegido = False
            else:
                banderaNumeroKelegido = True
    except Exception as e:
        messagebox.showwarning(message="Debe ingresar un n??mero entero como valor de k", title="Alerta")
        print(str(e))
        return 
    
    if (banderaNumeroKelegido):
        if (banderaFin2): #significa que ya se hizo click en el bot??n Iniciar Algoritmo anteriormente, asi que primero tenemos que destruir los botones de funcionalidades antes de correr de nuevo el algoritmo
            botonGraficoK.destroy()
        BarraDeProgreso2()
        hiloDelAlgoritmo=threading.Thread(target=IniciarAlgoritmo2)
        hiloDelAlgoritmo.start()

def IniciarAlgoritmo2():
    global dataSet
    global dataSetOriginal
    global matrizColumnasOrdenadas  
    global valorKElegido
    global dataSetKnn2
    global dataSetKnnPonderado2
    global banderaFin2
    #global entryK
    banderaFin2 = False
    dataSet = dataSetOriginal
    matrizKFold = CargarMatrizKFold(dataSet)
    matrizColumnasOrdenadas=OrdenarColumnasMatrizKFold(matrizKFold, len(dataSet))

    dataSetKnn2, dataSetKnnPonderado2 = ObtenerDataSetsCalculados(valorKElegido,valorKElegido)
    banderaFin2 = True  #significa que ya termin?? su ejecuci??n
    AgregarBotonesFuncionalidades2()

def IniciarAlgoritmo1():
    try: 
        global banderaFin   
        global dataSet
        global dataSetOriginal
        global matrizColumnasOrdenadas  
        global valorKMax        
        valorKMax = valorK.get()
        banderaFin = False #significa que el algoritmo sigue en ejecuci??n
        dataSet=dataSetOriginal     
        matrizKFold = CargarMatrizKFold(dataSet)
        matrizColumnasOrdenadas=OrdenarColumnasMatrizKFold(matrizKFold, len(dataSet))
        #Obtener k optimo.
        ObtenerKOptimos(dataSet)

        #Correr el algoritmo para K ??ptimo y para k ponderado ??ptimo 
        # global valorKOptimo
        # global valorKOptimoPonderado
        global dataSetKnn
        global dataSetKnnPonderado

        dataSetKnn, dataSetKnnPonderado = ObtenerDataSetsCalculadosconKOptimos()
        
        ##Comentado hasta solucionar el error generado al querer graficar y trabajar con hilos.
        # matrizDataSetKnn=ArmarMatrizParaGraficar(dataSetKnn)
        # matrizDataSetKnnPonderado=ArmarMatrizParaGraficar(dataSetKnnPonderado)
        
        banderaFin = True  #significa que ya termin?? su ejecuci??n
        AgregarBotonesFuncionalidades()

        ##Comentado hasta solucionar el error generado al querer graficar y trabajar con hilos.
        #GraficarDatosDatasetsOptimos(dataSetKnn, matrizDataSetKnn, dataSetKnnPonderado, matrizDataSetKnnPonderado)
        #GENERAR GRILLA
        #GenerarGrilla()   
        
    except Exception as e:
        messagebox.showwarning(message="Houston, we have a problem..." + str(e), title="Alerta")
        print(str(e))
        return        

def GraficarTablaResultadosK():
    global resultadosK
    global resultadosKPonderado

    resultadosK = sorted(resultadosK, reverse=True, key=lambda d : d["Precisi??n"])
    resultadosKPonderado = sorted(resultadosKPonderado, reverse=True, key=lambda d : d["Precisi??n"])

    frameAux = Toplevel(root)
    frameAux.geometry("800x400")

    tablaResultadosK = ttk.Treeview(frameAux, columns=("#1","#2","#3","#4"), show="headings")
    tablaResultadosK.heading("#1", text="Valor de K",anchor=N)
    tablaResultadosK.heading("#2", text="Precisi??n",anchor=N)
    tablaResultadosK.heading("#3", text="Valor de K (ponderado)",anchor=N)
    tablaResultadosK.heading("#4", text="Precisi??n",anchor=N)
    tablaResultadosK.column("#1",anchor=N)
    tablaResultadosK.column("#2",anchor=N)
    tablaResultadosK.column("#3",anchor=N)
    tablaResultadosK.column("#4",anchor=N)
    
    for i in range(0,len(resultadosK)):
        resk=resultadosK[i]
        resP=resultadosKPonderado[i]
        tablaResultadosK.insert("",'end',values=(resk["k"],resk["Precisi??n"],resP["k"],resP["Precisi??n"]))
    tablaResultadosK.pack(pady=10)

    tablaResultadosK.grid(row=0, column=0, sticky='nsew')
    scrollbar = ttk.Scrollbar(root, orient=tkinter.VERTICAL, command=tablaResultadosK.yview)
    tablaResultadosK.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')
  
    mainloop()

def GraficarDatosDatasetsCalculados():
    global dataSetKnn
    global dataSetKnnPonderado
    
    matrizDataSetKnn=ArmarMatrizParaGraficar(dataSetKnn)
    matrizDataSetKnnPonderado=ArmarMatrizParaGraficar(dataSetKnnPonderado)
    GraficarDatosDatasetsOptimos(dataSetKnn, matrizDataSetKnn, dataSetKnnPonderado, matrizDataSetKnnPonderado)

def GraficarClasificacionParaKElegido():
    global dataSetKnn2
    global dataSetKnnPonderado2
    global valorKElegido
    matrizDataSetKnn2=ArmarMatrizParaGraficar(dataSetKnn2)
    matrizDataSetKnnPonderado2=ArmarMatrizParaGraficar(dataSetKnnPonderado2)
    #GraficarDatosDatasetsParaKElegido(dataSetKnn2, matrizDataSetKnn2, dataSetKnnPonderado2, matrizDataSetKnnPonderado2)
       #Filtro de color
    color_filt=CargarFiltroColores(matrizDataSetKnn2) 
    todasLasClasesDelDataset=[f.clase for f in dataSetKnn2]
    patches=CargarPatches(todasLasClasesDelDataset)
    
    fig = plt.figure()
    graficoK = fig.add_subplot(121)
    graficoKPonderado = fig.add_subplot(122)

    puntosX = [f.x for f in dataSetKnn2]
    puntosY = [f.y for f in dataSetKnn2]    
    fig.suptitle(f'Gr??fica comparativa para k={valorKElegido}')
    graficoK.scatter(puntosX,puntosY,color=color_filt,label="Datos")
    graficoK.set_xlabel('Eje x')
    graficoK.set_ylabel('Eje y')
    graficoK.legend(handles=patches)
    graficoK.set_title(f'Gr??fico dataset clasificado con k={valorKElegido}')

    #Grafico knn ponderado
    color_filt2=CargarFiltroColores(matrizDataSetKnnPonderado2) 
    todasLasClasesDelDataset=[f.clase for f in dataSetKnnPonderado2]
    patches2=CargarPatches(todasLasClasesDelDataset)
    # xPuntos = [f.x for f in datasetPonderado]
    # yPuntos = [f.y for f in datasetPonderado]  
    graficoKPonderado.scatter(puntosX,puntosY,color=color_filt2,label="Datos")
    graficoKPonderado.set_xlabel('Eje x')
    graficoKPonderado.set_ylabel('Eje y')
    graficoKPonderado.legend(handles=patches2)
    graficoKPonderado.set_title(f'Gr??fico dataset clasificado con ponderaci??n para k={valorKElegido}')
    
    plt.ion()
    plt.show()

def GraficarDatosOriginalesDelDataset():
    global dataSetOriginal
    matrizAux=ArmarMatrizParaGraficar(dataSetOriginal)
    filtroColores=CargarFiltroColores(matrizAux)
    todasLasClasesDelDataset = [d.clase for d in dataSetOriginal]
    patches=CargarPatches(todasLasClasesDelDataset)

    puntosX = [f.x for f in dataSetOriginal]
    puntosY = [f.y for f in dataSetOriginal]    
    fig, ax = plt.subplots()
    ax.scatter(puntosX,puntosY,color=filtroColores,label="Datos")
    ax.set_xlabel('Eje x')
    ax.set_ylabel('Eje y')
    ax.legend(handles=patches)
    ax.set_title('Gr??fico del dataset original')
    plt.ion()
    plt.show()

def ArmarMatrizParaGraficar(datasetAux:List[Dato]):
    matriz= np.zeros((len(datasetAux),3))
    n=0
    for d in datasetAux:        
        matriz [n][0] = d.x
        matriz [n][1] = d.y
        matriz [n][2] = d.clase
        n=n+1
    return matriz

def ObtenerDataSetsCalculados(valorK:int, valorKPonderado:int):
    global dataSet
    global matrizColumnasOrdenadas    
    listaValoresK:List[int] = [valorK,valorKPonderado]
    dataSetKnn = []
    dataSetKnnPonderado = []
    longitudDataSet = len(dataSet)
    for posicion in range(0,2):
        k:int = listaValoresK[posicion]
        matrizColumnasOrdenadasAux=np.empty_like(matrizColumnasOrdenadas)
        np.copyto(matrizColumnasOrdenadasAux, matrizColumnasOrdenadas)  #creamos una copia de matrizColumnasOrdenadas        
        #recorremos una columna y guardamos primero el punto cabecera,
        for i in range(0,longitudDataSet):
            datoAux= dataSet[i]
            nuevoDato = Dato(datoAux.x,datoAux.y, datoAux.clase) #Creamos un nuevo Dato para no ocupar referencias a memoria del dataSet original
            columna=matrizColumnasOrdenadasAux[:longitudDataSet]
            matrizColumnasOrdenadasAux=np.delete(matrizColumnasOrdenadasAux,np.s_[0:longitudDataSet])
            claseDato=columna[0]['clase']
            columna= np.delete(columna,[0]) #quitamos el primer item al ser distancia = 0 por ser distancia a si mismo
                
            puntoskVecinos = np.array(columna[:k])   #puntosKVecios= list(clase,distancia)         
                            
            ClasesDeVecinos = np.array(puntoskVecinos['clase'])
            #determinamos cada clase y su cantidad de ocurrencias en los k vecinos
            counterClases = Counter(ClasesDeVecinos)
                
            #determinamos el valor de la clase para el punto analizado en base a sus vecinos
            clasesDistintasVecinos=np.unique(ClasesDeVecinos) #array de 1 de cada clase distinta
            if(posicion == 0):            #kNN Tradicional
                banderaEmpate= False
                if(len(clasesDistintasVecinos) > 1): #significa que hay al menos 2 clases distintas en los vecinos
                    dosClasesMasRepetidas = counterClases.most_common(2)  
                    if(dosClasesMasRepetidas[0][1]==dosClasesMasRepetidas[1][1]): #si las dos clases mas repetidas de los k vecinos se repiten la misma cantidad de veces => hay empate y el algoritmo no puede definir la clase
                        banderaEmpate = True
                        nuevoDato.clase=-2

                #ClaseMasRepetida = 0
                if(banderaEmpate == False):
                    ClaseMasRepetida = max(counterClases,key=counterClases.get)
                    if ClaseMasRepetida != claseDato:
                        nuevoDato.clase=-1 

                dataSetKnn.append(nuevoDato)         
            else:       #si posicion=1 entonces es la segunda vuelta y se esta calculando para el k ponderado
                #kNN Ponderado
                clasePonderadaAux = 0 # clase que se va a comparar a la del dato analizado            
                acuMaxPonderado=0
                banderaEmpatePonderado = False
                    
                if(len(clasesDistintasVecinos) > 1):
                    for clase in clasesDistintasVecinos:
                        acu = 0
                        #kVecinosMismaClase=np.where(puntoskVecinos[0]==clase)
                        kVecinosMismaClase=[p for p in puntoskVecinos if p["clase"]==clase]
                        for aux in kVecinosMismaClase:
                            acu= acu + 1/(aux['distancia']**2)
                            
                        if(acuMaxPonderado < acu):
                            acuMaxPonderado= acu
                            clasePonderadaAux = clase
                            banderaEmpatePonderado = False
                        else:
                            if(acuMaxPonderado == acu):
                                banderaEmpatePonderado = True

                    if(banderaEmpatePonderado == False):
                        if(clasePonderadaAux != claseDato):
                            nuevoDato.clase=-1
                    else:
                        nuevoDato.clase=-2 #el algoritmo no pudo clasificar el punto porque hubo un empate
                else: #k=1 entonces solo se compara la clase del vecino con la del dato
                    ClaseMasRepetida = max(counterClases,key=counterClases.get)
                    if(ClaseMasRepetida != claseDato):
                        nuevoDato.clase=-1
                dataSetKnnPonderado.append(nuevoDato)

    return dataSetKnn, dataSetKnnPonderado

def ObtenerDataSetsCalculadosconKOptimos():
    global valorKOptimo
    global valorKOptimoPonderado
    global dataSetKnn
    global dataSetKnnPonderado
    dataSetKnn = []
    dataSetKnnPonderado = [] 
    dataSetKnn, dataSetKnnPonderado = ObtenerDataSetsCalculados(valorKOptimo, valorKOptimoPonderado)
    return dataSetKnn, dataSetKnnPonderado

def EvaluarKEnElDataSet(k:int):
    global dataSet
    global matrizColumnasOrdenadas
    contadorAciertos=0
    contadorAciertosPonderado=0
    longitudDataSet = len(dataSet)
    matrizColumnasOrdenadasAux = np.copy(matrizColumnasOrdenadas)  #creamos una copia de matrizColumnasOrdenadas
    #recorremos una columna y guardamos primero el punto cabecera,
    for i in range(0,longitudDataSet):
        columna=matrizColumnasOrdenadasAux[:longitudDataSet]
        claseDato=columna[0]['clase']
        matrizColumnasOrdenadasAux=np.delete(matrizColumnasOrdenadasAux,np.s_[0:longitudDataSet])
 
        columna= np.delete(columna,[0]) #quitamos el primer item al ser distancia = 0 por ser distancia a si mismo
            
        puntoskVecinos = np.array(columna[:k])   #puntosKVecios= list(clase,distancia)         
                        
        ClasesDeVecinos = np.array(puntoskVecinos['clase'])
        #determinamos cada clase y su cantidad de ocurrencias en los k vecinos
        counterClases = Counter(ClasesDeVecinos)
            
        #determinamos el valor de la clase para el punto analizado en base a sus vecinos
        clasesDistintasVecinos=np.unique(ClasesDeVecinos) #array de 1 de cada clase distinta
           
        #kNN Tradicional
        banderaEmpate= False
        if(len(clasesDistintasVecinos) > 1): #significa que hay al menos 2 clases distintas en los vecinos
            dosClasesMasRepetidas = counterClases.most_common(2)  
            if(dosClasesMasRepetidas[0][1]==dosClasesMasRepetidas[1][1]): #si las dos clases mas repetidas de los k vecinos se repiten la misma cantidad de veces => hay empate y el algoritmo no puede definir la clase
                banderaEmpate = True

        #ClaseMasRepetida = 0
        if(banderaEmpate == False):
            ClaseMasRepetida = max(counterClases,key=counterClases.get)
            if ClaseMasRepetida == claseDato:
                contadorAciertos = contadorAciertos+1
        
        #kNN Ponderado
        clasePonderadaAux = 0 # clase que se va a comparar a la del dato analizado            
        acuMaxPonderado=0
        banderaEmpatePonderado = False
            
        if(len(clasesDistintasVecinos) > 1):
            for clase in clasesDistintasVecinos:
                acu = 0
                kVecinosMismaClase=[p for p in puntoskVecinos if p["clase"]==clase]
                for aux in kVecinosMismaClase:
                    acu= acu + 1/(aux['distancia']**2)
                    
                if(acuMaxPonderado < acu):
                    acuMaxPonderado= acu
                    clasePonderadaAux = clase
                    banderaEmpatePonderado = False
                else:
                    if(acuMaxPonderado == acu):
                        banderaEmpatePonderado = True

            if(banderaEmpatePonderado == False):
                if(clasePonderadaAux == claseDato):
                    contadorAciertosPonderado = contadorAciertosPonderado + 1  
        else: #k=1 entonces solo se compara la clase del vecino con la del dato
            ClaseMasRepetida = max(counterClases,key=counterClases.get)
            if(ClaseMasRepetida == claseDato):
                contadorAciertosPonderado = contadorAciertosPonderado + 1
    return contadorAciertos,contadorAciertosPonderado

def ObtenerKOptimos(dataSet):
    global resultadosK
    global resultadosKPonderado
    global valorKMax
    resultadosK = []
    resultadosKPonderado = []

    #z=1 #contador de vueltas del algoritmo
    hasta=valorKMax+1
    for k in range(1,hasta):     #Desde k=1 hasta 15 => range() devuelve valor (Valordesde:Valorhasta-1)
        #contador de aciertos para los k-vecinos  
        contadorAciertos, contadorAciertosPonderado = EvaluarKEnElDataSet(k)
        resultadosK.append({"k": k, "Precisi??n": contadorAciertos})            
        resultadosKPonderado.append({"k":k,"Precisi??n":contadorAciertosPonderado})
    
    global graficadorComparativo
    graficadorComparativo=GraficadorComparadorKnn(dataSet,resultadosK,resultadosKPonderado,valorKMax)    

    global valorKOptimo
    global valorKOptimoPonderado
    #Seteamos los valores para el KOptimo y el KOptimoPonderado
    valorKOptimo, valorKOptimoPonderado= graficadorComparativo.ObtenerKOptimos()

def setPathFile():
    global datosString
    global dataSetOriginal
    nombreConRuta = filedialog.askopenfilename(title="Elegir un DataSet",filetypes = (("excel files",".csv"),("all files",".*")));
    nombreInvertido=invertir_cadena(nombreConRuta)
    #invertimos la cadena y spliteamos para separar el nombre de la ruta y que el nombre quede en la posici??n inicial de la lista
    palabras=nombreInvertido.split('/') 
    #invertimos la primer palabra de la lista, la cual es el nombre invertido del archivo, para setearlo correctamente
    ubicacionArchivo.set(nombreConRuta);
    nombreArchivo.set(invertir_cadena(palabras[0]));

    datosString=CargarArchivo()
    dataSetOriginal= CargarDataSet(datosString)
    GraficarSegundaVista(len(dataSetOriginal))

def invertir_cadena(cadena):
    return cadena[::-1]

def GraficarSegundaVista(largoDataset :int):
    global entryK
    Label (frame1, text="----------Para un rango [1; K-max] ----------", font=('Comic Sans MS',14)).grid(row=3,column=1,padx=10,pady=20)

    labelAviso = Label(frame1,text="Aviso, cuanto mayor sea el valor K-Max elegido, el tiempo de espera aumentar??")
    labelAviso.grid(row=4, column=0,columnspan=2,sticky='se', pady=5, padx = 0)
    labelAviso.config(bg="yellow")
    labelK = Label(frame1, text="Valor K-Max: ").grid(row=5, column=0,sticky='se', pady=0, padx = 0)
    input_k = Scale(frame1, from_=1, to=largoDataset-1, orient=HORIZONTAL,troughcolor='red',variable=valorK, length= 300)
    input_k.set(15)
    input_k.grid(row = 5,column=1, pady=0,sticky='s', padx = 0)
    
    botonObtenerOptimos = Button(frame1, text='Obtener k ??ptimos',command=PrimerPaso)
    botonObtenerOptimos.grid(row=5,column=2,sticky='s',padx=5,pady=10)

    Label (frame1, text="----------Para un valor particular k ----------", font=('Comic Sans MS',14)).grid(row=10,column=1,padx=10,pady=10)
    Label (frame1, text="Valor de k:", font=('Comic Sans MS',10)).grid(row=11,column=0,padx=0,pady=0)
    entryK = Entry(frame1, textvariable="", width=10, justify='center')
    entryK.grid(row=11, column=1, sticky='sw', padx=0, pady=10)
    botonEvaluarK = Button(frame1, text='Evaluar k',command=PrimerPaso2)
    botonEvaluarK.grid(row=11,column=2,sticky='w',padx=10,pady=10)

    botonGraficoOriginal = Button(frame1, text='Gr??fico del dataSet original',command=GraficarDatosOriginalesDelDataset)
    botonGraficoOriginal.grid(row=2,column=2,sticky='w',padx=10,pady=10)

def GraficarVistaInicial ():
    cuadrotexto = Entry(frame1,textvariable=nombreArchivo,width=33)
    cuadrotexto.grid(row=2,column=1,padx=0,pady=0)
    cuadrotexto.config(fg='red',justify='center')
    Label(frame1,text='Nombre Archivo: ',fg='black',font=('Comic Sans MS',10)).grid(row=2,column=0,padx=5,pady=0, sticky='e')
    frame1.config(bd=2)
    frame1.config(relief='solid')

    buttonDataSet = Button(frame1, text = "Seleccionar DATASET", width=15,command = setPathFile)
    buttonDataSet.grid(row=1,column=1,padx=5,pady=15)

    frame=Frame(root,width=1600,height=1000)
    frame.grid(row=1,column=1,padx=20,pady=20)

def AgregarBotonesFuncionalidades():
    global frame1
    global my_progress
    global progressMensaje
    global botonKOptimos
    global botonGraficoOriginal
    global botonGraficoKOptimos
    global botonTablaAciertosK
    my_progress.destroy()
    progressMensaje.destroy()
    #Agregamos el bot??n que permita visualizar la tabla comparativa de los rendimientos de los valores de k y de k ponderado
    botonKOptimos = Button(frame1, text='Gr??fico comparativo de los k valores',command=graficadorComparativo.GraficarTablaComparativaDeLasK)
    botonKOptimos.grid(row=9,column=2,padx=10,pady=10)    

    botonGraficoKOptimos = Button(frame1, text='Gr??fico datasets ??ptimos calculados',command=GraficarDatosDatasetsCalculados)
    botonGraficoKOptimos.grid(row=9,column=1,padx=10,pady=10)

    botonTablaAciertosK = Button(frame1, text='Tabla de aciertos de los k valores  ',command=GraficarTablaResultadosK)
    botonTablaAciertosK.grid(row=9,column=0,padx=10,pady=10)

def AgregarBotonesFuncionalidades2():
    global botonGraficoK
    global my_progress2
    global progressMensaje

    my_progress2.destroy()
    progressMensaje2.destroy()
    botonGraficoK = Button(frame1, text='Gr??fico clasificativo para el k elegido ', command=GraficarClasificacionParaKElegido)
    botonGraficoK.grid(row=12, column=1, padx=0, pady=0)

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

        #Gr??fico de la grilla
        GrillaConDataset.scatter(grid_x,grid_y,
                    c = ListaClasesVecinos,
                    alpha = 0.4,
                    cmap= "tab10",
                    marker="s",
                    label="Grilla")

        #Gr??fico del dataset
        GrillaConDataset.scatter([d.x for d in dataSet],
                    [d.y for d in dataSet],
                    c = [d.clase for d in dataSet],
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
        fig.canvas.manager.set_window_title('IA II - Gr??fico kNN')
        GrillaConDataset.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=5)                   
        plt.show()

#Variables globales
dType = [('clase', int), ('distancia', float)]
matrizColumnasOrdenadas=np.empty((0,600),dtype=dType)

datosString:List[str] = None
dataSet:List[Dato] = None
dataSetOriginal:List[Dato] = None
dataSetKnn:List[Dato] = None
dataSetKnnPonderado:List[Dato] = None
dataSetKnn2:List[Dato] = None
dataSetKnnPonderado2:List[Dato] = None
resultadosK = []
resultadosKPonderado = []
colors = ['pink','lightgreen','lightblue','orange','lightpurple','lightgray']
badColors= ['red','black']

root=Tk()
root.title('Algoritmo kNN - Kunaschik, Saucedo, Zitelli');
root.resizable(0,0)
root.geometry('1024x720')

clasesConSusPuntos:List[ClaseConPuntos] = []

nombreArchivo=StringVar()
nombreArchivo.set('')
ubicacionArchivo=StringVar()
ubicacionArchivo.set('')
valorK = IntVar()
valorKMax = 0
valorKOptimo:int = 0
valorKOptimoPonderado:int = 0
valorKElegido:int = 0
frame1=Frame(root,width=1600,height=1000)
frame1.grid(row=0,column=0,ipadx=10,ipady=10)
entryK:Entry = Entry(frame1, textvariable="", width=10, justify='center')

graficadorComparativo:GraficadorComparadorKnn = None
GraficarVistaInicial()
banderaFin = False
banderaFin2 = False

#botones de funcionalidades y progressbar
my_progress = ttk.Progressbar(frame1, orient=HORIZONTAL, length=300, mode='determinate')
progressMensaje = Label(frame1,text=' ', font=('Comic Sans MS',8))
my_progress2 = ttk.Progressbar(frame1, orient=HORIZONTAL, length=300, mode='determinate')
progressMensaje2 = Label(frame1,text=' ', font=('Comic Sans MS',8))
botonKOptimos = Button(frame1, text='Gr??fico comparativo de los k valores')
botonGraficoOriginal = Button(frame1, text='Gr??fico del dataSet original')
botonGraficoKOptimos = Button(frame1, text='Gr??fico datasets ??ptimos calculados')
botonTablaAciertosK = Button(frame1, text='Tabla de aciertos de los k valores ')
botonGraficoK = Button(frame1, text='Gr??fico clasificativo para el k elegido ')
#Cada un segundo, si el algoritmo sigue corriendo, que cambie el mensaje de la barra de progreso
if (banderaFin == False):
    root.after(1000, ActualizarMensajeProgreso)
if (banderaFin2 == False):
    root.after(1000, ActualizarMensajeProgreso2)
root.mainloop()
