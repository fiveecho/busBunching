import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from helpers import distance
from sim import simulate_run

result = simulate_run(record=True)
snapshots = result["snapshots"]
bunched_buses = result["bunched"]

print(f'route time of bus 0: {result["trip_times"].get(0)} s')
print(f'percentage of buses bunched: {round((len(bunched_buses)/result["n_buses"])*100, 3)}')

if bunched_buses:
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
