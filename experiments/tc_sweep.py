import numpy as np
import matplotlib.pyplot as plt
from model import FIGURES
from model.batch import run_batch
from model.controlFunction import make_controller

RUN_COUNT = 100

# T_c (s): gain alpha = 1/T_c. Predicted stable window at a 10 s control period:
# 2 x control period = 20 s (sampled-update limit) to about 81 min (boarding-instability limit, T_c < 2/beta); see controlAnalysis.py.
T_C = [15, 20, 30, 120, 600, 1800, 3600, 5400]

STAGES = {
    "no limits": dict(),
    "slow-only (r in [0.5, 1], no headroom)": dict(delta=0, r_max=1.0, r_min=0.5),
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
        ax.axvline(81, color='red', linestyle=':', label='predicted stability limits (20 s and 81 min)')
        ax.axvline(20 / 60, color='red', linestyle=':')
        ax.set(title=title, ylabel=unit)
    axs[0].legend(fontsize=8)
    axs[3].set(xscale='log', xlabel='T_c (min), gain = 1/T_c')
    fig.savefig(FIGURES / 'tc_sweep.png')
    plt.show()
