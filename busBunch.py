import numpy as np
from scipy.stats import truncnorm
from params import Bus, BusStop, distance, H

RUN_COUNT = 5000

bunch_counter = 0
probability_data = []

for i in range(RUN_COUNT):

    if i%500 == 0:
        print(f'run {i}')

    busStops = [BusStop(distance[i], i) for i in range(len(distance))]



    # For the first bus, assume that time_since_last is always H i.e. ideal headway i.e. 5 mins
    # based on time_since_last, generate passenger loading count
    # then, generate how long it will take to traverse the distance (exception for expressway)

    bunched_buses = set()
    time = 0
    bus_no = 0
    bus_tracker = []
    bunch = False
    TIMEOUT = 10800


    while time <= TIMEOUT:
        # bus dispatch
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
                    # print(f'Bus bunching occurred; bus {bus_tracker[i].index} and bus {bus_tracker[i+1].index} after {time/60} min')
                    bunch = True
                    bunched_buses.add(bus_tracker[i].index) 
                    bunched_buses.add(bus_tracker[i+1].index)

        time += 1

    if bunch:
        bunch_counter += 1
    bunch_percentage = len(bunched_buses)/len(bus_tracker)
    probability_data.append(bunch_percentage)


data = np.array(probability_data)
print(f"Percentage of peak hour evenings where bunching occurs: {round((bunch_counter/RUN_COUNT)*100, 3)}")
print(f"Average percentage of buses that bunch: {round(np.mean(data)*100, 3)}")
print(f"Standard deviation of bus bunch percentage: {round(np.std(data, ddof=1), 3)}")
        

