from operator import length_hint
from turtle import width
import matplotlib.pyplot as plt
import numpy as np
from io import open
from cProfile import label
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
#import pandas as pd
from modelos import *
from typing import Any, Counter, List

class GraficadorComparadorKnn:
    def __init__(self, dataSet: List[Dato], resultadosK, resultadosKPonderado,kMax) -> None:
        self.dataSet : List[Dato]   = dataSet
        #self.kNeighborsNumber : int = kNeighborsNumber
        self.resultadosK = resultadosK
        self.resultadosKPonderado = resultadosKPonderado
        self.kMax = kMax

        
    def GraficarTablaComparativaDeLasK(self):
        #PLOT AND GUI TABLE FUNCTIONS
        xList:List[int] = [x["k"] for x in self.resultadosK]
        yList:List[int] = [y["Presición"] for y in self.resultadosK]

        xListP:List[int] = [x["k"] for x in self.resultadosKPonderado]
        yListP:List[int] = [y["Presición"] for y in self.resultadosKPonderado]

        # for KFold in resultadosK:
        #     xList.append(KFold["k"])
        #     yList.append(KFold["accuracy"])

        resultadosDeK = sorted(self.resultadosK, reverse=True, key=lambda d : d["Presición"])
        resultadosDeKPonderado = sorted(self.resultadosKPonderado, reverse=True, key=lambda d : d["Presición"])
        kOptimo = resultadosDeK[0]
        kOptimoPonderado = resultadosDeKPonderado [0]
        

        fig = plt.figure()

        graficoK = fig.add_subplot(121)
        graficoKPonderado = fig.add_subplot(122)
        
        fig.suptitle(f'Gráfica comparativa para valores k comprendidos entre 1 y {self.kMax}')
        graficoK.plot(xList,yList,'b--')
        graficoK.set_title(f"kNN (Óptimo: k={kOptimo['k']}, N° de aciertos = {kOptimo['Presición']})")
        graficoK.set_xlabel('Valor de k')
        graficoK.set_ylabel('Aciertos')
        graficoK.plot(kOptimo["k"], kOptimo["Presición"], color='red', marker="x")

        graficoKPonderado.plot(xListP,yListP,'b--')
        graficoKPonderado.set_title(f"kNN con ponderación (Óptimo: k={kOptimoPonderado['k']}, N° de aciertos = {kOptimoPonderado['Presición']})")
        graficoKPonderado.set_xlabel('Valor de k')
        graficoKPonderado.set_ylabel('Aciertos')
        graficoKPonderado.plot(kOptimoPonderado["k"], kOptimoPonderado["Presición"], color='red', marker="x")
        
        # plt.plot(xList,yList,'b--')
        # plt.title(f"Comparación de valores k (Óptimo: k={kOptimo['k']}, Cantidad de aciertos = {kOptimo['Presición']})")
        # plt.xlabel('Valor de k')
        # plt.ylabel('Aciertos')

        # toShow:List[Any] = []
        # for KFold in resultadosK:
        #     if KFold["Presición"] == kOptimo["Presición"]:
        #         toShow.append([KFold["k"],KFold["Presición"]])


        # plt.annotate(f'Mas preciso: ({kOptimo["k"]};{kOptimo["Presición"]})',
        #             xy=(kOptimo["k"], kOptimo["Presición"]),
        #             xytext=(kOptimo["k"], kOptimo["Presición"]/2),
        #             arrowprops=dict(facecolor='black', arrowstyle="->"))

        #Cargamos la tabla con los resultados de Kfold
        # gui.kfold_results_table.delete(*gui.kfold_results_table.get_children())
        # for bettersKinfo in toShow:
        #     gui.kfold_results_table.insert("", 'end', values=bettersKinfo)
        # gui.kfold_results_table.pack(pady=10)
        plt.ion()
        plt.show()
            
    def ObtenerKOptimos(self):
        resultadosDeK = sorted(self.resultadosK, reverse=True, key=lambda d : d["Presición"])
        resultadosDeKPonderado = sorted(self.resultadosKPonderado, reverse=True, key=lambda d : d["Presición"])
        kOptimo = resultadosDeK[0]
        kOptimoPonderado = resultadosDeKPonderado[0]
        return kOptimo['k'],kOptimoPonderado['k']

