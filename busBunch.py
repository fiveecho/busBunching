import numpy as np
from sim import simulate_run
from helpers import headway_stats

RUN_COUNT = 1000

if __name__ == "__main__":
    bunch_counter = 0
    probability_data = []
    ewt_list =[]
    cv_list = []
    trip_list = []

    for run in range(RUN_COUNT):
        if run % 500 == 0:
            print(f'run {run}')

        result = simulate_run()

        if result["bunched"]: # if on a container returns true if container is not empty
            bunch_counter += 1
        probability_data.append(len(result["bunched"]) / result["n_buses"])
        ewt, cv = headway_stats(result["arrival_times"])
        ewt_list.append(ewt)
        cv_list.append(cv)
        trip_list.extend(result["trip_times"].values())  # arrival_times[-1] - [0], finished buses only

    data = np.array(probability_data)
    ewt_np = np.mean(np.array(ewt_list), axis=0)  # (runs, 31) -> mean per stop
    cv_np = np.mean(np.array(cv_list), axis=0)
    trip_np = np.array(trip_list) / 60            # minutes

    print(f"Percentage of peak hour evenings where bunching occurs: {round((bunch_counter/RUN_COUNT)*100, 3)}")
    print(f"Average percentage of buses that bunch: {round(np.mean(data)*100, 3)}")
    print(f"Standard deviation of bus bunch percentage: {round(np.std(data, ddof=1)*100, 3)}")
    print(f"Average EWT (s) for each bus stop: {np.round(ewt_np, 1).tolist()}")
    print(f"Average headway CV for each bus stop: {np.round(cv_np, 2).tolist()}")
    print(f"Average trip time: {trip_np.mean():.1f} min (sd {trip_np.std(ddof=1):.1f}, {len(trip_np)} trips)")
