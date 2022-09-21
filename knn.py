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
from controlador import BuscarVecinos
from modelos import *
from typing import Any, Counter, List

def ObtenerKOptimo(k:int,dataSet:List[Dato]):
    KFoldResults = []
    PuntosConVecinos = []
    #cargamos la tabla en horizontal de cada punto con sus 9 vecinos
    for d in dataSet:
        PuntosConVecinos.append(BuscarVecinos(d)) 
    
    #contador de aciertos para los k-vecinos
    contadorAciertos = 0
    #Desde k=1 hasta n-1
    for k in range(1,len(PuntosConVecinos)):
        #recorremos una columna y guardamos primero el punto cabecera,
        #y luego una lista de solo las etiquetas de sus vecinos
        for PuntoConVecinos in PuntosConVecinos:
            Punto = Dato(PuntoConVecinos.x,PuntoConVecinos.y,PuntoConVecinos.clase)
            ClasesDeVecinos = PuntoConVecinos["clase"][:k]
            # for i in range(1,k+1):
            #     EtiquetasDeVecinos.append(PuntoConVecinos[i])
            #Contamos las cantidades de cada etiqueta
            cantidadClases = Counter(ClasesDeVecinos)
            ClaseMasRepetida = max(cantidadClases,key=cantidadClases.get)
            ocurrenciasDeMaxValRep = 0
            CantidadDeVecesDeLaClaseMasRepetida = cantidadClases[ClaseMasRepetida]
            for clase in cantidadClases:
                if cantidadClases[clase] == CantidadDeVecesDeLaClaseMasRepetida:
                    ocurrenciasDeMaxValRep=ocurrenciasDeMaxValRep+1
            if ocurrenciasDeMaxValRep == 1:
                if ClaseMasRepetida == Punto.clase:
                    contadorAciertos = contadorAciertos+1
            ocurrenciasDeMaxValRep = 0
        KFoldResults.append({"k":k, "accuracy":contadorAciertos})
        contadorAciertos = 0
    
    #PLOT AND GUI TABLE FUNCTIONS
    xList:List[int] = [x["k"] for x in KFoldResults]
    yList:List[int] = [y["accuracy"] for y in KFoldResults]
    # for KFold in KFoldResults:
    #     xList.append(KFold["k"])
    #     yList.append(KFold["accuracy"])
    
    KFoldResults = sorted(KFoldResults, reverse=True, key=lambda d : d["accuracy"])
    maximo = KFoldResults[0]

    plt.plot(xList,yList,'r--')
    plt.title(f"K Fold Validation ({maximo['k']},{maximo['accuracy']})")
    plt.xlabel('K Number')
    plt.ylabel('K accuracy')

    toShow:List[Any] = []
    for KFold in KFoldResults:
        if KFold["accuracy"] == maximo["accuracy"]:
            toShow.append([KFold["k"],KFold["accuracy"]])

    plt.plot(maximo["k"], maximo["accuracy"], color='green', marker="x")

    plt.annotate(f'Most Acurrate ({maximo["k"]};{maximo["accuracy"]})',
                xy=(maximo["k"], maximo["accuracy"]),
                xytext=(maximo["k"], maximo["accuracy"]/2),
                arrowprops=dict(facecolor='black', arrowstyle="->"))

    #Cargamos la tabla con los resultados de Kfold
    # gui.kfold_results_table.delete(*gui.kfold_results_table.get_children())
    # for bettersKinfo in toShow:
    #     gui.kfold_results_table.insert("", 'end', values=bettersKinfo)
    # gui.kfold_results_table.pack(pady=10)

    plt.ion()
    plt.show()
