from helpers import Bus, BusStop
import numpy as np

reference_window = np.array([-1,0,1])

def control(bus, tracker, ): # bus, array of tracked buses
    if type(bus) is not Bus:
        return None
    else:
        current_bus_index = bus.index
        relevant_buses = {b.index: (b.position, b.last_stop) for b in tracker if ((not b.terminal) and (b.index in (reference_window + current_bus_index)))}
        


    # cases --> no leading no following, 
    #   leading no following --> closest to start, use forward headway only
    #   no leading following --> closest to end, ignore all and operate independently  
    #   leading following --> 
    # find headway in time for both in front and behind --> if no actual bus, set 


if "__name__" == "__main__":
    print('Hello world')