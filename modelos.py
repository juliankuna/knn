from dataclasses import dataclass

@dataclass
class Dato: 
    x: float
    y: float
    clase: int

@dataclass
class Punto: 
    x: float
    y: float
    clase: int
    distancia:float
