from routePull import routeGet
import numpy as np
from scipy.stats import truncnorm

route = routeGet()

# print(route)


distance = [stop['Distance'] for stop in route]


AVERAGE_BOARD_TIME = 1.52 # https://www.sciencedirect.com/science/article/pii/S1077291X22000753
FIXED_BUS_STOP_DELAY = 5.6 + 10
BEFORE_EXPRESSWAY_INDEX = 20
AVERAGE_PASSENGER_RATE = 10/(5.0*60)
EXPRESSWAY_SPEED = 50.0
ARTERIAL_SPEED = 29.0 
# CRUISE_SPEED = (distance[-1])/(ROUTE_DURATION * 60)
H = 5.0 * 60 # 5 min headway, based on 190 bus service weekday 5-7pm headway

def get_speed(expressway = False):
    if expressway:
        mean, std, low, high = EXPRESSWAY_SPEED, 2, 25, 60
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

        return int(dwell)

    def driving_speed(self):
        if self.index == BEFORE_EXPRESSWAY_INDEX:
            speed = get_speed(expressway=True)
        else:
            speed = get_speed()

        return speed