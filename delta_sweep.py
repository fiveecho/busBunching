import numpy as np
import matplotlib.pyplot as plt
from batch import run_batch
from controlFunction import make_controller

RUN_COUNT = 200

# headroom delta as a fraction of cruise speed: buses normally run at r = 1 - delta,
# leaving room to speed up to r = 1 (slow-only cap) when they fall behind
DELTA = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]

# slow-only controller at the gain chosen from the T_c sweep (T_c = 10 min: near-zero bunching
# for about +2.5 min of trip time); add entries here to compare other gains
GAINS = {"T_c = 10 min": 600}
SLOW_ONLY = dict(r_max=1.0, r_min=0.5)

if __name__ == "__main__":
    baseline = run_batch(RUN_COUNT)
    results = {name: [run_batch(RUN_COUNT, controller=make_controller(T_c=T_c, delta=d, **SLOW_ONLY))
                      for d in DELTA]
               for name, T_c in GAINS.items()}

    # metrics against delta
    fig, axs = plt.subplots(nrows=4, figsize=(8, 10), sharex=True)
    for ax, key, title, unit in zip(axs, ("prob", "ewt20", "ewt29", "trip"),
                                    ("Average percentage of bunched buses", "Excess Waiting Time, stop 20 (before expressway)",
                                     "Excess Waiting Time, stop 29 (last boarding stop)", "Average trip time"),
                                    ("%", "s", "s", "min")):
        for name, res in results.items():
            ax.errorbar(DELTA, [r[key] for r in res], yerr=[r[key + "_ci"] for r in res],
                        marker='o', capsize=3, label=name)
        ax.axhline(baseline[key], color='grey', linestyle='--', label='no control')
        ax.set(title=title, ylabel=unit)
    axs[0].legend(fontsize=8)
    axs[3].set(xlabel='headroom delta (fraction of cruise speed); slow-only, r in [0.5, 1]')
    fig.savefig('delta_sweep.png')

    # trade-off: what each extra minute of trip time buys in EWT at the last boarding stop
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    for name, res in results.items():
        ax2.errorbar([r["trip"] for r in res], [r["ewt29"] for r in res],
                     xerr=[r["trip_ci"] for r in res], yerr=[r["ewt29_ci"] for r in res],
                     marker='o', capsize=3, label=name)
        for d, r in zip(DELTA, res):
            ax2.annotate(f"{d:.2f}", (r["trip"], r["ewt29"]), textcoords="offset points", xytext=(5, 5), fontsize=7)
    ax2.plot(baseline["trip"], baseline["ewt29"], 'ks', label='no control')
    ax2.set(xlabel='average trip time (min)', ylabel='EWT at stop 29 (s)',
            title='Cost of control: trip time against EWT (labels: delta)')
    ax2.legend(fontsize=8)
    fig2.savefig('delta_tradeoff.png')
    plt.show()
