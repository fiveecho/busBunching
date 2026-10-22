import numpy as np
import matplotlib.pyplot as plt
from batch import run_batch
from controlFunction import make_controller

RUN_COUNT = 100

# T_c (s): gain alpha = 1/T_c. Predicted stable window at a 10 s control period:
# about 25 s (delay limit) to about 74 min (boarding-instability limit); see CLAUDE.md.
T_C = [15, 20, 30, 120, 600, 1800, 3600, 5400]

STAGES = {
    "stage 1: no limits": dict(),
    "stage 2: slow-only, delta 0": dict(delta=0, r_max=1.0, r_min=0.5),
}

if __name__ == "__main__":
    baseline = run_batch(RUN_COUNT)
    results = {name: [run_batch(RUN_COUNT, controller=make_controller(T_c=T_c, **params))
                      for T_c in T_C]
               for name, params in STAGES.items()}

    fig, axs = plt.subplots(nrows=4, figsize=(8, 10), sharex=True)
    for ax, key, title, unit in zip(axs, ("prob", "ewt20", "ewt29", "trip"),
                                    ("Average percentage of bunched buses", "Excess Waiting Time, stop 20 (before expressway)",
                                     "Excess Waiting Time, stop 29 (last boarding stop)", "Average trip time"),
                                    ("%", "s", "s", "min")):
        for name, res in results.items():
            ax.errorbar(np.array(T_C) / 60, [r[key] for r in res], yerr=[r[key + "_ci"] for r in res],
                        marker='o', capsize=3, label=name)
        ax.axhline(baseline[key], color='grey', linestyle='--', label='no control')
        ax.axvline(74, color='red', linestyle=':', label='predicted instability (about 74 min)')
        ax.set(title=title, ylabel=unit)
    axs[0].legend(fontsize=8)
    axs[3].set(xscale='log', xlabel='T_c (min), gain = 1/T_c')
    fig.savefig('tc_sweep.png')
    plt.show()
