import numpy as np
from helpers import distance, H, ARTERIAL_SPEED, EXPRESSWAY_SPEED, BEFORE_EXPRESSWAY_INDEX

# Equivalent-arterial coordinate: the route stretched so it runs at ARTERIAL_SPEED throughout.
# The expressway leg is shrunk by ARTERIAL/EXPRESSWAY, and each intermediate stop adds the
# distance an arterial bus would cover during an average dwell. A spacing in this coordinate
# divided by ARTERIAL_SPEED is a nominal time headway.
MEAN_DWELL = 29.3                                   # s, model mean dwell (see CLAUDE.md)
V_ART = ARTERIAL_SPEED / 3600                       # km/s
DWELL_EQ = MEAN_DWELL * V_ART                       # km of arterial road per average dwell

leg_scale = np.array([ARTERIAL_SPEED / EXPRESSWAY_SPEED if k == BEFORE_EXPRESSWAY_INDEX else 1.0
                      for k in range(len(distance) - 1)])
leg_eq = np.diff(distance) * leg_scale              # equivalent length of leg k -> k+1
# equivalent position on arrival at stop k: legs before k, plus dwells at stops 1..k-1
Z_STOP = np.concatenate(([0.0], np.cumsum(leg_eq))) + DWELL_EQ * np.maximum(np.arange(len(distance)) - 1, 0)


def equivalent_position(bus, now):
    """Bus position (km) in the equivalent-arterial coordinate."""
    if bus.terminal:
        return Z_STOP[-1]
    k = bus.last_stop
    z = Z_STOP[k]
    if k == 0:                                      # no dwell at the origin
        return z + (bus.position - distance[0]) * leg_scale[0]
    if bus.position == distance[k]:                 # dwelling: count elapsed dwell, up to the mean
        return z + min(now - bus.arrival_times[-1], MEAN_DWELL) * V_ART
    return z + DWELL_EQ + (bus.position - distance[k]) * leg_scale[k]


def make_controller(T_c=3600.0, delta=0.0, r_min=None, r_max=None):
    """Spring law on nominal time headways; returns control(bus, tracker, now) -> speed fraction r.

    r multiplies the bus's drawn leg speed, so it works the same on arterial and expressway legs.
    T_c:   time (s) to close a headway error; gain alpha = 1/T_c
    delta: headroom as a fraction of cruise speed (r = 1 - delta at zero error)
    Stage 1 (no limits): defaults. Stage 2 (slow-only): r_max=1, delta > 0, r_min e.g. 0.5.
    """
    def control(bus, tracker, now):
        if bus.terminal:   # finished buses are not controlled
            return 1.0
        z = equivalent_position(bus, now)
        front = tracker[bus.index - 1] if bus.index > 0 else None
        rear = tracker[bus.index + 1] if bus.index + 1 < len(tracker) else None

        # missing or terminal neighbour: ghost at the ideal headway (error 0); a terminal bus
        # has stopped moving, so the spacing to it would shrink and wrongly slow the follower
        e_front = 0.0
        if front is not None and not front.terminal:
            e_front = (equivalent_position(front, now) - z) / V_ART - H
        e_rear = 0.0
        if rear is not None:
            e_rear = (z - equivalent_position(rear, now)) / V_ART - H

        r = 1.0 - delta + (e_front - e_rear) / T_c
        if r_max is not None:
            r = min(r, r_max)
        if r_min is not None:
            r = max(r, r_min)
        return max(r, 0.0)   # physical floor in every stage: buses never reverse (r_min is the design floor)

    return control
