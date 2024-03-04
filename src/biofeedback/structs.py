from typing import NamedTuple

class Sample(NamedTuple):
    hr: float
    cadence: float

class TestPoint(NamedTuple):
    avg_hr: float
    avg_sf: float
    
class Parabola(NamedTuple):
    a: float
    b: float
    c: float

class OptHrPoint(NamedTuple):
    x: float
    y: float

