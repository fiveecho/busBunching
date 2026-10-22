import numpy as np
import matplotlib.pyplot as plt
from batch import run_batch

RUN_COUNT = 100

if __name__ == "__main__":
    # traffic-noise sweep, no control
    traffic_factor = np.arange(0.0, 1.5, 0.2)
    results = [run_batch(RUN_COUNT, traffic_factor=factor) for factor in traffic_factor]

    fig, axs = plt.subplots(nrows=3, figsize=(8, 8), sharex=True)
    axs[0].set_title('Average percentage of bunched buses')
    axs[0].set(ylabel='%')
    axs[1].set_title('Average Excess Waiting Time')
    axs[1].set(ylabel='s')
    axs[2].set_title('Average trip time')
    axs[2].set(ylabel='min', xlabel = 'traffic factor (1.0 = 5 km/h arterial sd)')
    for ax, key in zip(axs, ("prob", "ewt", "trip")):
        ax.errorbar(traffic_factor, [r[key] for r in results], yerr=[r[key + "_ci"] for r in results],
                    marker='o', capsize=3)
    fig.savefig('traffic_noise_sweep.png')
    plt.show()
