from routePull import routeGet
import numpy as np

route = routeGet()

# print(route)

distance = []

for stop in route:
    distance.append(stop['Distance'])

print(distance)

CRUISE_SPEED = (distance[-1])/(80 * 60)

print(CRUISE_SPEED)

