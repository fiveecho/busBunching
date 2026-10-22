import numpy as np
import matplotlib.pyplot as plt
from batch import run_batch
from helpers import BEFORE_EXPRESSWAY_INDEX

RUN_COUNT = 100
PROFILE_RUNS = 200

# boarding feedback: on = model (dwell grows with time since the last bus, Poisson boarding);
# off = every bus dwells for the model's mean, so headway no longer affects dwell
FEEDBACK = {"boarding feedback on (model)": True, "boarding feedback off (constant dwell)": False}

if __name__ == "__main__":
    # 1. traffic-noise sweep, no control, with and without boarding feedback
    traffic_factor = np.arange(0.0, 1.5, 0.2)
    results = {name: [run_batch(RUN_COUNT, traffic_factor=f, passenger_noise=fb) for f in traffic_factor]
               for name, fb in FEEDBACK.items()}

    fig, axs = plt.subplots(nrows=4, figsize=(8, 10), sharex=True)
    for ax, key, title, unit in zip(axs, ("prob", "ewt20", "ewt29", "trip"),
                                    ("Average percentage of bunched buses", "Excess Waiting Time, stop 20 (before expressway)",
                                     "Excess Waiting Time, stop 29 (last boarding stop)", "Average trip time"),
                                    ("%", "s", "s", "min")):
        for name, res in results.items():
            ax.errorbar(traffic_factor, [r[key] for r in res], yerr=[r[key + "_ci"] for r in res],
                        marker='o', capsize=3, label=name)
        ax.set(title=title, ylabel=unit)
    axs[0].legend(fontsize=8)
    axs[3].set(xlabel='traffic factor (1.0 = 5 km/h arterial sd)')
    fig.savefig('traffic_noise_sweep.png')

    # 2. EWT along the route: traffic noise (disturbance) x boarding feedback (unstable plant)
    cases = {
        "traffic + feedback (model)": dict(traffic_factor=1.0, passenger_noise=True),
        "traffic only (feedback off)": dict(traffic_factor=1.0, passenger_noise=False),
        "feedback only (no traffic noise)": dict(traffic_factor=0.0, passenger_noise=True),
        "neither": dict(traffic_factor=0.0, passenger_noise=False),
    }
    stops = np.arange(1, 30)
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    print(f"{'case':34s} {'% bunched':>10s} {'EWT20 (s)':>10s} {'EWT29 (s)':>10s} {'trip (min)':>11s}")
    for name, kw in cases.items():
        r = run_batch(PROFILE_RUNS, **kw)
        ax2.plot(stops, r["ewt_stop"][1:30], marker='.', label=name)
        print(f"{name:34s} {r['prob']:6.1f}±{r['prob_ci']:<3.1f} {r['ewt20']:6.1f}±{r['ewt20_ci']:<3.1f} "
              f"{r['ewt29']:6.1f}±{r['ewt29_ci']:<3.1f} {r['trip']:7.2f}")
    ax2.axvspan(BEFORE_EXPRESSWAY_INDEX, BEFORE_EXPRESSWAY_INDEX + 1, color='grey', alpha=0.2, label='expressway leg')
    ax2.set(xlabel='stop', ylabel='EWT (s)', title='EWT along the route (no control, 200 runs each)')
    ax2.legend(fontsize=8)
    fig2.savefig('feedback_profile.png')
    plt.show()
