import math
from typing import List

EA = 83144.0  # J/mol
R = 8.314     # J/(mol·K)

def calculate_mkt(temperatures_celsius: List[float]) -> float:
    if not temperatures_celsius:
        return 0.0
    
    n = len(temperatures_celsius)
    sum_exp = 0.0
    for t_c in temperatures_celsius:
        t_k = t_c + 273.15
        sum_exp += math.exp(-EA / (R * t_k))
    
    avg_exp = sum_exp / n
    if avg_exp == 0.0:
        return 0.0
        
    mkt_k = (-EA / R) / math.log(avg_exp)
    mkt_c = mkt_k - 273.15
    return mkt_c
