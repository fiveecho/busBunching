import json
from pathlib import Path
import numpy as np
from scipy.stats import truncnorm

# Cached LTA DataMall route for bus 190, direction 2; refresh with `python routePull.py`
with open(Path(__file__).parent / "data" / "route_190_dir2.json") as f:
    route = json.load(f)

distance = [stop['Distance'] for stop in route]


AVERAGE_BOARD_TIME = 1.52 # https://www.sciencedirect.com/science/article/pii/S1077291X22000753
FIXED_BUS_STOP_DELAY = 5.6 + 10
BEFORE_EXPRESSWAY_INDEX = 20
AVERAGE_PASSENGER_RATE = 10/(5.0*60)
EXPRESSWAY_SPEED = 43.0 # from scheduled bus timings https://sgwiki.miraheze.org/wiki/Bus_Service_190
ARTERIAL_SPEED = 24.5 
# CRUISE_SPEED = (distance[-1])/(ROUTE_DURATION * 60)
H = 5.0 * 60 # 5 min headway, based on 190 bus service weekday 5-7pm headway

def get_speed(expressway = False):
    if expressway:
        mean, std, low, high = EXPRESSWAY_SPEED, 3, 25, 60
    else:
        mean, std, low, high = ARTERIAL_SPEED, 5, 15, 45
    # Convert absolute bounds to standard deviations for SciPy
    a = (low - mean) / std
    b = (high - mean) / std
    
    return truncnorm.rvs(a, b, loc=mean, scale=std)/(60*60)

class Bus:
    def __init__(self, index):
        self.position = 0
        self.index = index
        self.last_stop = 0
        self.speed = get_speed()
        self.dwell_end = -1
        self.terminal = False
        self.arrival_times = []
    def move(self):
        if self.terminal == False:
            self.position += self.speed
            if self.position >= distance[self.last_stop + 1]:
                self.position = distance[self.last_stop + 1]
        

class BusStop:
    def __init__(self, distance, index):
        self.last_bus_time = None
        self.distance = distance
        self.index = index

    def dwell_time(self, current_time):

        if self.last_bus_time == None:
            wait_time = H

        else:
            wait_time = current_time - self.last_bus_time
        
        # average of 10 passengers per headway interval boarding
        passengers = np.random.poisson(lam=max(0,AVERAGE_PASSENGER_RATE*wait_time)) 

        dwell = passengers * AVERAGE_BOARD_TIME + FIXED_BUS_STOP_DELAY

        self.last_bus_time = current_time + dwell

        return dwell

    def driving_speed(self):
        if self.index == BEFORE_EXPRESSWAY_INDEX:
            speed = get_speed(expressway=True)
        else:
            speed = get_speed()

        return speed


def headway_stats(arrival_times, H = H):
    """EWT (s) and headway CV at every stop, from simulate_run's arrival_times.
    Returns two arrays of length 31 (index = stop). Leaves out the first and last bus."""

    A = np.array(arrival_times[1:-1], dtype=float)   # (n_buses - 2, 31): row = bus, column = stop
    h = np.diff(np.sort(A, axis=0), axis=0)           # headways at each stop, in arrival order
    awt = (h**2).sum(axis=0) / (2 * h.sum(axis=0)) # probability passenger shows up in interval h * average waiting time per interval h/2
    ewt = awt - H / 2
    cv = h.std(axis=0, ddof=1) / h.mean(axis=0)
    return ewt, cv
