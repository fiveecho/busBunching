import numpy as np
from sim import simulate_run
from helpers import headway_stats
import matplotlib.pyplot as plt

RUN_COUNT = 100

if __name__ == "__main__":
    traffic_factor = np.arange(0.0, 1.5, 0.2)
    sweep_prob = []
    sweep_ewt = []
    sweep_trip = []
    ci_prob, ci_ewt, ci_trip = [], [], []

    def ci95(x):
        # 95% CI half-width; one value per run, so runs are the independent samples
        return 1.96 * np.std(x, ddof=1) / np.sqrt(len(x))

    for factor in traffic_factor:
        # bunch_counter = 0
        probability_data = []
        ewt_list =[]
        cv_list = []
        trip_list = []

        for run in range(RUN_COUNT):
            # if run % 500 == 0:
            #     print(f'run {run}')

            result = simulate_run(traffic_factor=factor)

            # if result["bunched"]: # if on a container returns true if container is not empty
            #     bunch_counter += 1
            probability_data.append(len(result["bunched"]) / result["n_buses"])
            ewt, cv = headway_stats(result["arrival_times"])
            ewt_list.append(ewt)
            # cv_list.append(cv)
            trip_list.append(np.mean(list(result["trip_times"].values())) / 60)  # per-run mean trip (min); buses in a run are not independent

        prob_runs = np.array(probability_data) * 100
        sweep_prob.append(prob_runs.mean())
        ci_prob.append(ci95(prob_runs))

        ewt_np = np.mean(np.array(ewt_list), axis=0)  # (runs, 31) -> mean per stop
        ewt_runs = np.array(ewt_list)[:, 1:30].mean(axis=1)  # per-run passenger-average EWT, stops 1-29
        sweep_ewt.append(ewt_runs.mean())
        ci_ewt.append(ci95(ewt_runs))
        # cv_np = np.mean(np.array(cv_list), axis=0)

        sweep_trip.append(np.mean(trip_list))
        ci_trip.append(ci95(trip_list))


    fig, axs = plt.subplots(nrows=3, figsize=(8, 8), sharex=True)
    axs[0].set_title('Average percentage of bunched buses')
    axs[0].set(ylabel='%')
    axs[1].set_title('Average Excess Waiting Time')
    axs[1].set(ylabel='s')
    axs[2].set_title('Average trip time')
    axs[2].set(ylabel='min', xlabel = 'traffic factor (1.0 = 5 km/h arterial sd)')
    for ax, y, ci in zip(axs, (sweep_prob, sweep_ewt, sweep_trip), (ci_prob, ci_ewt, ci_trip)):
        ax.errorbar(traffic_factor, y, yerr=ci, marker='o', capsize=3)
    fig.savefig('traffic_noise_sweep.png')
    plt.show()
    # print(f"Percentage of peak hour evenings where bunching occurs: {round((bunch_counter/RUN_COUNT)*100, 3)}")
    # print(f"Average percentage of buses that bunch: {round(np.mean(data)*100, 3)}")
    # print(f"Standard deviation of bus bunch percentage: {round(np.std(data, ddof=1)*100, 3)}")
    # print(f"Average EWT (s) for each bus stop: {np.round(ewt_np, 1).tolist()}")
    # print(f"Average headway CV for each bus stop: {np.round(cv_np, 2).tolist()}")
    # print(f"Average trip time: {trip_np.mean():.1f} min (sd {trip_np.std(ddof=1):.1f}, {len(trip_np)} trips)")
