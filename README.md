# Bus bunching on Singapore's bus 190

A simulation of bus bunching on SMRT service 190 (Kampong Bahru Terminal to Choa Chu Kang Interchange), built from real LTA stop-distance data and calibrated to the published timetable. The goal is to test a cooperative speed-control law (Daganzo and Pilachowski, 2011) under the constraints a Singapore operator actually faces. The main constraint is that buses can be slowed but not sped up.

**Status:** the uncontrolled baseline is complete. The controller is in progress.

<img width="2400" height="800" alt="Animation of 190 buses along the route, with bunched buses in red" src="https://github.com/user-attachments/assets/81368f2a-8a7e-4990-985b-4adb60d7a8e3" />

## Headline so far

Without control, bunching appears even with no traffic noise at all. Uneven passenger boarding alone bunches about 11% of buses over a two-hour evening peak. At the baseline traffic noise this rises to 65%. Excess wait time grows steadily along the route, reaching about 2 minutes by the last boarding stop.

## Model

The model is tick-based, with 1-second ticks. Buses are dispatched every 5 minutes from 17:00 to 19:00, which gives 25 buses. Each run continues until every bus has reached the terminal.

- **Route:** 31 stops over 22.3 km, from the LTA DataMall BusRoutes API (direction 2). The data is cached in `data/route_190_dir2.json`. It includes a 9.1 km non-stop expressway leg between stop 20 (Raffles Town Club) and stop 21 (Blk 223).
- **Speed:** each bus draws one speed per leg, when it leaves a stop. The draw is a normal distribution truncated at the mean ± 3 sd, so the truncation does not shift the mean (with a floor of 5 km/h arterial and 3 km/h expressway). A *traffic factor* scales both standard deviations. Factor 1.0 is the baseline: 5 km/h on arterial roads, about 13 s of travel-time sd on a typical 0.45 km leg, and 3 km/h on the expressway.
- **Dwell:** a fixed 15.6 s per stop, plus 1.52 s per boarding passenger. Boardings are Poisson-distributed, with mean = arrival rate × time since the previous bus left that stop. Late buses therefore pick up more passengers and fall further behind, which is the feedback that causes bunching. The average dwell works out at 29.3 s.
- **Bunching:** a pair of consecutive buses is counted as bunched once the follower catches or passes its leader. Overtaking is allowed.

| Parameter | Value | Source |
|---|---|---|
| Stop distances | 31 stops, 22.3 km | LTA DataMall BusRoutes API |
| Headway H | 5 min | Midpoint of 190's PM-peak frequency of 3–7 min (DataMall BusServices) |
| Boarding time | 1.52 s per passenger | [Singapore bus stop study](https://www.sciencedirect.com/science/article/pii/S1077291X22000753) |
| Fixed stop delay | 5.6 s (doors) + 10 s (acceleration and deceleration loss) | Same study. It measured about 9 s to decelerate and 11 s to accelerate; with linear speed ramps, about half of each is lost time (our assumption). |
| Passenger arrivals | 10 per 5 min per stop, the same at every stop | Assumption. Bus capacity suggests about 6–10. |
| Arterial speed | 24.5 km/h (effective) | Calibrated to the 190 timetable, below |
| Expressway speed | 43 km/h (effective) | Calibrated to the 190 timetable, below |

### Calibration

The two speeds are *effective* speeds: they bundle traffic signals, congestion and merging into one number. They were fitted, with traffic noise off, to the scheduled 190 times for departures after 23:30.

| Checkpoint | Timetable | Simulated, no noise | Simulated, baseline noise |
|---|---|---|---|
| Stop 20 (9.0 km) | 32 min | 31.4 | – |
| Stop 21, Blk 223 (18.1 km) | 45 | 44.6 | – |
| Stop 29 (21.5 km) | 57 | 56.8 | 58.3 |

The last 0.8 km to the interchange takes 5–7 min in the timetable, against about 2.5 min in the simulation. This looks like terminal approach or recovery time rather than driving, and comes after the last boarding stop, so it was not fitted. Noisy legs are slower on average than noise-free ones, because slow legs cost more time than fast legs save. At baseline noise, the time to stop 29 therefore comes out 1.3 min above the timetable.

## Metrics

- **% of buses bunched:** the share of the 25 buses involved in at least one bunching event during the run. An isolated pair counts as 2.
- **Excess wait time (EWT):** at each stop, the headways h are the gaps between consecutive bus arrivals, in the order the buses physically arrive. Then

  AWT = Σh² / (2Σh),  SWT = H/2,  EWT = AWT − SWT.

  EWT is the extra time an average passenger, arriving at random, waits because buses are uneven. It is quadratic in headway, because long gaps both catch more passengers and make each of them wait longer. The **route average** over stops 1–29 equals the per-passenger average, because demand is uniform across stops. The first and last bus are left out.
- **Trip time:** dispatch to terminal, averaged within each run. When control is added, this becomes the cost of control.

All results are means over independent runs with 95% confidence intervals (1.96 × sd / √runs). Each run counts as one sample, since buses within a run are not independent.

## Results: no control

![Noise sweep](traffic_noise_sweep.png)

The figure uses 100 runs per level. The table below uses 200 runs per level:

| Traffic factor (arterial sd) | % bunched | EWT, route average | EWT stop 10 | EWT stop 20 | EWT stop 29 | Trip time |
|---|---|---|---|---|---|---|
| 0 (boarding noise only) | 10.8 ± 1.3 | 9 ± 1 s | 1 s | 9 s | 40 s | 59.2 min |
| 0.6 (3 km/h) | 48.6 ± 2.1 | 32 ± 1 s | 8 s | 42 s | 97 s | 59.7 min |
| 1.0 (5 km/h, baseline) | 65.2 ± 1.7 | 53 ± 2 s | 23 s | 77 s | 128 s | 60.8 min |
| 1.4 (7 km/h) | 76.6 ± 1.3 | 75 ± 2 s | 49 s | 107 s | 152 s | 62.7 min |

- **Bunching is not only a traffic problem.** With traffic noise switched off, the boarding feedback alone still bunches about 11% of buses. This is the instability that the first term of Daganzo and Pilachowski's control law is designed to cancel.
- **Headway errors amplify along the route.** At baseline, EWT grows from about 23 s at stop 10 to about 2 min at stop 29. The route average (53 s) hides this: passengers late on the route bear most of the cost.
- **The baseline sits on the steep part of the curve,** so the controller will be tested at several noise levels rather than at the baseline alone.

## Control (in progress)

The planned controller is based on Daganzo and Pilachowski (2011). Each bus adjusts its speed using the gaps to the bus in front and the bus behind, as if neighbouring buses were joined by springs. This project's version adds the realities of operating it:

- slow-only control, capped at the cruise speed, because operators slow buses rather than speed them up;
- headroom δ below the cruise speed;
- driver response lag and an acceleration limit;
- free boundaries at the first and last bus.

The paper's linear analysis only holds while the speed command stays within its limits. The open question this project addresses is how much is lost once the command is clipped.

## Assumptions and limitations

- Traffic noise is independent across buses and legs. Real congestion is shared, so the baseline is probably pessimistic.
- Demand is uniform across stops. Bus capacity and alighting are not modelled, so a full bus keeps gaining boarding delay. This probably makes bunching worse than reality.
- Dispatch is perfectly even, which is optimistic.
- Buses can overtake freely.
- Speeds are lumped effective values, calibrated to off-peak (after 23:30) scheduled times. Peak trips are probably slower.
- H = 5 min is the midpoint of a published 3–7 min range. The real headway varies through the evening.

## How to run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python busBunch.py                 # noise sweep (about 1 min): saves and shows traffic_noise_sweep.png
python busBunchVisualisation.py    # one run, animated
```

The route is already cached. To refresh it from LTA DataMall, set your API key and run `routePull.py`:

```bash
export LTA_ACCOUNT_KEY="your-key"
python routePull.py
```

## References

- Daganzo, C. F. and Pilachowski, J. (2011). Reducing bunching with bus-to-bus cooperation. *Transportation Research Part B*, 45(1), 267–277.
- LTA DataMall: BusRoutes and BusServices APIs.
- Singapore bus stop study, ScienceDirect article S1077291X22000753 (boarding and stop-delay parameters).
