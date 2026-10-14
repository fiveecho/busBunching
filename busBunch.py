import numpy as np
from sim import simulate_run

RUN_COUNT = 5000

if __name__ == "__main__":
    bunch_counter = 0
    probability_data = []

    for run in range(RUN_COUNT):
        if run % 500 == 0:
            print(f'run {run}')

        result = simulate_run()
        if result["bunched"]: # if on a container returns true if container is not empty
            bunch_counter += 1
        probability_data.append(len(result["bunched"]) / result["n_buses"])

    data = np.array(probability_data)
    print(f"Percentage of peak hour evenings where bunching occurs: {round((bunch_counter/RUN_COUNT)*100, 3)}")
    print(f"Average percentage of buses that bunch: {round(np.mean(data)*100, 3)}")
    print(f"Standard deviation of bus bunch percentage: {round(np.std(data, ddof=1)*100, 3)}")
