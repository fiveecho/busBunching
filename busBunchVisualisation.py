from routePull import routeGet
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from params import Bus, BusStop, distance, H

# route = routeGet()

# print(route)


# distance = [stop['Distance'] for stop in route]

# print(distance)

bunch_counter = 0



busStops = [BusStop(distance[i], i) for i in range(len(distance))]



# For the first bus, assume that time_since_last is always H i.e. ideal headway i.e. 5 mins
# based on time_since_last, generate passenger loading count
# then, generate how long it will take to traverse the distance (exception for expressway)


time = 0
bus_no = 0
bus_tracker = []
bunch = False
snapshots = []
TIMEOUT = 10800
bunched_buses = set()

route_time = []

    # bus dispatch
while time <= TIMEOUT:
    if time % H == 0 and time <= 7200:
        bus_tracker.append(Bus(bus_no))
        bus_no += 1
        print(f'bus dispatched: bus {bus_no}')
    
    for bus in bus_tracker:
        if bus.terminal:
            continue
        if bus.dwell_end > time:
            continue
        bus.move()
        
        if bus.position == busStops[bus.last_stop + 1].distance:
            if bus.position == busStops[-1].distance:
                bus.terminal = True
                if bus.index == 0:
                    print(f'\nroute time: {time}\n')
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

    snapshots.append({
        bus.index: bus.position
        for bus in bus_tracker if not bus.terminal
    })
    
    time += 1

print(f'percentage of buses bunched: {round((len(bunched_buses)/len(bus_tracker))*100, 3)}')        

if bunch:
    # Animation

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlabel("Distance along route (km)")
    ax.set_yticks([])  
    ax.set_xlim(-0.5, distance[-1]+0.5)
    ax.set_ylim(-1, 1)
    ax.plot([0, distance[-1]], [0, 0], linewidth=1, color='r', zorder=0)
    ax.scatter(distance, np.zeros_like(distance),facecolors='w', edgecolors='black', s=10, label='Bus Stops', zorder=1)


    bus_dots = ax.scatter([], [], s=50)

    # Text labels for each bus
    labels = {}

    def update(frame):
        current_positions = snapshots[frame]

        ids = list(current_positions.keys())
        # x and y coordinates for all active buses
        x = list(current_positions.values())
        y = np.zeros_like(x)

        bus_dots.set_offsets(np.column_stack((x, y)))
        bus_dots.set_facecolor(['red' if b in bunched_buses else 'blue' for b in ids])

        # Remove old labels
        for label in labels.values():
            label.remove()

        labels.clear()

        
        # Add bus number above each bus
        for bus_id, position in current_positions.items():
            if bus_id not in bunched_buses:
                labels[bus_id] = ax.text(
                    position,
                    0.15,
                    f"B{bus_id}",
                    ha="center"
                )
            else:
                if frame == len(snapshots) - 1:
                    continue
                else:
                    labels[bus_id] = ax.text(
                                        position,
                                        0.15,
                                        f"B{bus_id}",
                                        ha="center"
                                    )

        ax.set_title(f"Model of bus bunching — t = {frame} s")

        return bus_dots, *labels.values()
        

    STEP = 15

    frame_ids = list(range(0, len(snapshots), STEP)) + [len(snapshots) - 1] 

    ani = FuncAnimation(
        fig,
        update,
        frames=frame_ids,
        interval=50,
        blit=False,
        repeat=False
    )

    # ani.save(filename="tmp/bus_bunch_no_control.gif", writer="pillow", fps=15)

    plt.show()
