from model.batch import run_batch
from model.controlFunction import make_controller

RUN_COUNT = 200

# first-order driver lag (s) between the displayed command and the applied speed fraction.
# Predictions from controlAnalysis.py (fastest mode, T_c = 10 min): phase margin 81 / 70 / 27 deg
# at 0 / 30 / 300 s, and the stability limit tau < 1/p, about 20 min, is reached at 1200 s.
LAGS = [0, 30, 300, 1200]

CONTROLLERS = {
    "no limits, T_c = 10 min": make_controller(T_c=600),                         # the analysed linear loop
    "slow-only, T_c = 10 min": make_controller(T_c=600, r_max=1.0, r_min=0.5),   # the final design
}

if __name__ == "__main__":
    print(f"{'controller':26s} {'lag (s)':>7s} {'% bunched':>11s} {'EWT20 (s)':>11s} {'EWT29 (s)':>11s} {'trip (min)':>11s}")
    for name, controller in CONTROLLERS.items():
        for lag in LAGS:
            r = run_batch(RUN_COUNT, controller=controller, driver_lag=lag)
            print(f"{name:26s} {lag:7d} {r['prob']:6.1f}±{r['prob_ci']:<4.1f} {r['ewt20']:6.1f}±{r['ewt20_ci']:<4.1f} "
                  f"{r['ewt29']:6.1f}±{r['ewt29_ci']:<4.1f} {r['trip']:7.2f}", flush=True)
