import matplotlib.pyplot as plt
from tkinter import *
from modelos import *
from typing import  List

class GraficadorComparadorKnn:
    def __init__(self, dataSet: List[Dato], resultadosK, resultadosKPonderado,kMax) -> None:
        self.dataSet : List[Dato]   = dataSet
        self.resultadosK = resultadosK
        self.resultadosKPonderado = resultadosKPonderado
        self.kMax = kMax

        
    def GraficarTablaComparativaDeLasK(self):
        xList:List[int] = [x["k"] for x in self.resultadosK]
        yList:List[int] = [y["Precisión"] for y in self.resultadosK]

        xListP:List[int] = [x["k"] for x in self.resultadosKPonderado]
        yListP:List[int] = [y["Precisión"] for y in self.resultadosKPonderado]

        resultadosDeK = sorted(self.resultadosK, reverse=True, key=lambda d : d["Precisión"])
        resultadosDeKPonderado = sorted(self.resultadosKPonderado, reverse=True, key=lambda d : d["Precisión"])
        kOptimo = resultadosDeK[0]
        kOptimoPonderado = resultadosDeKPonderado [0]

        fig = plt.figure()

        graficoK = fig.add_subplot(121)
        graficoKPonderado = fig.add_subplot(122)
        
        fig.suptitle(f'Gráfica comparativa para valores k comprendidos entre 1 y {self.kMax}')
        graficoK.plot(xList,yList,'b--')
        graficoK.set_title(f"kNN (Óptimo: k={kOptimo['k']}, N° de aciertos = {kOptimo['Precisión']})")
        graficoK.set_xlabel('Valor de k')
        graficoK.set_ylabel('Aciertos')
        graficoK.plot(kOptimo["k"], kOptimo["Precisión"], color='red', marker="x")

        graficoKPonderado.plot(xListP,yListP,'b--')
        graficoKPonderado.set_title(f"kNN con ponderación (Óptimo: k={kOptimoPonderado['k']}, N° de aciertos = {kOptimoPonderado['Precisión']})")
        graficoKPonderado.set_xlabel('Valor de k')
        graficoKPonderado.set_ylabel('Aciertos')
        graficoKPonderado.plot(kOptimoPonderado["k"], kOptimoPonderado["Precisión"], color='red', marker="x")

        #Para abrir el gráfico ocupando toda la pantalla
        figManager = plt.get_current_fig_manager()
        figManager.window.state('zoomed')
        
        plt.ion()
        plt.show()
            
    def ObtenerKOptimos(self):
        resultadosDeK = sorted(self.resultadosK, reverse=True, key=lambda d : d["Precisión"])
        resultadosDeKPonderado = sorted(self.resultadosKPonderado, reverse=True, key=lambda d : d["Precisión"])
        kOptimo = resultadosDeK[0]
        kOptimoPonderado = resultadosDeKPonderado[0]
        return kOptimo['k'],kOptimoPonderado['k']

