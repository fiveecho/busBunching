from helpers import Bus, BusStop, distance, H

DISPATCH_END = 7200  # last dispatch at t <= 2 h (17:00-19:00 peak)
TIMEOUT = 12600  # safety cap only; runs normally end when every bus is terminal


def simulate_run(record=False, controller = None):
    """One peak-window run.

    Returns a dict with
        bunched:    set of bus indices involved in any bunch
        n_buses:    number of buses dispatched
        arrival_times: list (one per bus, by index) of arrival times (s) at stops 0, 1, ...;
                       entry 0 is dispatch, entry k is arrival at stop k; shorter than 31 if cut off
        trip_times: {bus index: terminal arrival time - dispatch time} (s), for buses that finished
        snapshots:  list (one per tick) of {bus index: position (km)} for active buses if record, else None
    """
    busStops = [BusStop(distance[j], j) for j in range(len(distance))]
    time = 0
    bus_tracker = []
    bunched_buses = set()
    snapshots = [] if record else None

    # run until dispatch is over and every bus has reached the terminal (order-independent, so overtaking is fine)
    while (time <= DISPATCH_END or not all(bus.terminal for bus in bus_tracker)) and time <= TIMEOUT:
        # bus dispatch
        if time % H == 0 and time <= DISPATCH_END:
            bus = Bus(len(bus_tracker))
            bus_tracker.append(bus)
            bus.arrival_times.append(time)

        for bus in bus_tracker:
            if bus.terminal:
                continue
            if bus.dwell_end > time:
                continue
            bus.move()

            if bus.position == busStops[bus.last_stop + 1].distance:
                bus.arrival_times.append(time)
                if bus.position == busStops[-1].distance:
                    bus.terminal = True
                else:
                    bus.last_stop += 1
                    bus.dwell_end = time + busStops[bus.last_stop].dwell_time(time)
                    bus.speed = busStops[bus.last_stop].driving_speed()

        # bunching: follower has caught or passed its leader, both still on route
        for j in range(len(bus_tracker) - 1):
            leader, follower = bus_tracker[j], bus_tracker[j + 1]
            if follower.position >= leader.position and not follower.terminal and not leader.terminal:
                bunched_buses.add(leader.index)
                bunched_buses.add(follower.index)

        if record:
            snapshots.append({
                bus.index: bus.position
                for bus in bus_tracker if not bus.terminal
            })

        time += 1

    return {
        "bunched": bunched_buses,
        "n_buses": len(bus_tracker),
        "arrival_times": [bus.arrival_times for bus in bus_tracker],
        "trip_times": {bus.index: bus.arrival_times[-1] - bus.arrival_times[0]
                       for bus in bus_tracker if bus.terminal},
        "snapshots": snapshots,
    }
