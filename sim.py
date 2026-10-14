from helpers import Bus, BusStop, distance, H

DISPATCH_END = 7200  # last dispatch at t <= 2 h (17:00-19:00 peak)
TIMEOUT = 10800


def simulate_run(record=False):
    """One peak-window run.

    Returns a dict with
        bunched:    set of bus indices involved in any bunch
        n_buses:    number of buses dispatched
        trip_times: {bus index: terminal arrival time - dispatch time} (s), for buses that finished
        snapshots:  list (one per tick) of {bus index: position (km)} for active buses if record, else None
    """
    busStops = [BusStop(distance[j], j) for j in range(len(distance))]
    time = 0
    bus_tracker = []
    dispatch_times = {}
    trip_times = {}
    bunched_buses = set()
    snapshots = [] if record else None

    while time <= TIMEOUT:
        # bus dispatch
        if time % H == 0 and time <= DISPATCH_END:
            bus = Bus(len(bus_tracker))
            bus_tracker.append(bus)
            dispatch_times[bus.index] = time

        for bus in bus_tracker:
            if bus.terminal:
                continue
            if bus.dwell_end > time:
                continue
            bus.move()

            if bus.position == busStops[bus.last_stop + 1].distance:
                if bus.position == busStops[-1].distance:
                    bus.terminal = True
                    trip_times[bus.index] = time - dispatch_times[bus.index]
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
        "trip_times": trip_times,
        "snapshots": snapshots,
    }
