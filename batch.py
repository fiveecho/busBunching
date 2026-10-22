import numpy as np
from sim import simulate_run
from helpers import headway_stats

EWT_STOPS = (20, 29)   # stop before the expressway; last boarding stop (30, the terminal, is alight-only)


def ci95(x):
    # 95% CI half-width; one value per run, so runs are the independent samples
    return 1.96 * np.std(x, ddof=1) / np.sqrt(len(x))


def run_batch(n_runs=100, **sim_kwargs):
    """Run simulate_run n_runs times and summarise.

    sim_kwargs pass straight through to simulate_run (e.g. traffic_factor=1.0, controller=...).
    Each metric is computed per run first, so runs are the independent samples for the CIs.
    Returns a dict of means and 95% CI half-widths:
        prob, prob_ci:       % of buses bunched
        ewt20, ewt20_ci:     EWT (s) at stop 20 (one key pair per stop in EWT_STOPS)
        ewt29, ewt29_ci:     EWT (s) at stop 29
        ewt_stop:            mean EWT at every stop (array of 31)
        trip, trip_ci:       mean trip time (min), averaged within each run first
    """
    prob, ewt_all, trip = [], [], []
    for _ in range(n_runs):
        result = simulate_run(**sim_kwargs)
        prob.append(100 * len(result["bunched"]) / result["n_buses"])
        ewt, _ = headway_stats(result["arrival_times"])
        ewt_all.append(ewt)
        trip.append(np.mean(list(result["trip_times"].values())) / 60)  # buses in a run are not independent

    ewt_all = np.array(ewt_all)                     # (runs, 31)
    out = {
        "prob": np.mean(prob), "prob_ci": ci95(prob),
        "ewt_stop": ewt_all.mean(axis=0),
        "trip": np.mean(trip), "trip_ci": ci95(trip),
    }
    for k in EWT_STOPS:
        out[f"ewt{k}"], out[f"ewt{k}_ci"] = ewt_all[:, k].mean(), ci95(ewt_all[:, k])
    return out
