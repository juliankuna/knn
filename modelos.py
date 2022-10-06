from dataclasses import dataclass
from typing import List
@dataclass
class Dato: 
    x: float
    y: float
    clase: int

@dataclass
class Punto: 
    x: float
    y: float

@dataclass
class ClaseConPuntos:
    clase:int
    puntos:List[Punto]
@dataclass
class DatoConDistancia: 
    x: float
    y: float
    clase: int
    distancia:float

@dataclass
class DatoConClasesVecinos: 
    x: float
    y: float
    clase: int
    clasesVecinos:List[int]

@dataclass
class ClaseYDistancia:
    clase: int
    distancia:float


@dataclass
class DatoPrueba: 
    dato: Dato
    distancia:float