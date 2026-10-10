from routePull import routeGet
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

route = routeGet()

# print(route)


distance = [stop['Distance'] for stop in route]

# print(distance)

ROUTE_DURATION = 62.0
AVERAGE_BOARD_TIME = 1.52 # https://www.sciencedirect.com/science/article/pii/S1077291X22000753
FIXED_BUS_STOP_DELAY = 5.6 + 10
BEFORE_EXPRESSWAY_INDEX = 20
AVERAGE_PASSENGER_RATE = 10/(5.0*60)
EXPRESSWAY_SPEED = 55.0/(60*60)
ARTERIAL_SPEED = 29.0 /(60*60)
# CRUISE_SPEED = (distance[-1])/(ROUTE_DURATION * 60)
H = 5.0 * 60 # 5 min headway, based on 190 bus service weekday 5-7pm headway
RUN_COUNT = 5000
# print(CRUISE_SPEED)

class Bus:
    def __init__(self, index):
        self.position = 0
        self.index = index
        self.last_stop = 0
        self.speed = ARTERIAL_SPEED
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
            speed = EXPRESSWAY_SPEED
        else:
            speed = ARTERIAL_SPEED

        return speed

bunch_counter = 0

for i in range(RUN_COUNT):

    busStops = [BusStop(distance[i], i) for i in range(len(distance))]



    # For the first bus, assume that time_since_last is always H i.e. ideal headway i.e. 5 mins
    # based on time_since_last, generate passenger loading count
    # then, generate how long it will take to traverse the distance (exception for expressway)


    time = 0
    bus_no = 0
    bus_tracker = []
    bunch = False
    TIMEOUT = 10800


    while not bunch:
        # bus dispatch
        if time > TIMEOUT:
            print('Timeout, no bunching occurred')
            break
        if time % H == 0 and time <= 7200:
            bus_tracker.append(Bus(bus_no))
            bus_no += 1
            # print(f'bus dispatched: bus {bus_no}')
        
        for bus in bus_tracker:
            if bus.terminal:
                continue
            if bus.dwell_end > time:
                continue
            bus.move()
            
            if bus.position == busStops[bus.last_stop + 1].distance:
                if bus.position == busStops[-1].distance:
                    bus.terminal = True
                else:
                    bus.last_stop += 1
                    bus.dwell_end = time + busStops[bus.last_stop].dwell_time(time)
                    bus.speed = busStops[bus.last_stop].driving_speed()

        
        
        if len(bus_tracker) >= 2:
            for i in range(len(bus_tracker) - 1):
                if (bus_tracker[i + 1].position >= bus_tracker[i].position) and not bus_tracker[i + 1].terminal and not bus_tracker[i].terminal:
                    print(f'Bus bunching occurred; bus {bus_tracker[i].index} and bus {bus_tracker[i+1].index} after {time/60} min')
                    bunch = True

        time += 1

    if bunch:
        bunch_counter += 1

print(f"Percentage of peak hour evenings where bunching occurs: {round((bunch_counter/RUN_COUNT)*100, 3)}")
        

