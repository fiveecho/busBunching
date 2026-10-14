
import os
import requests

def routeGet():

    url = "https://datamall2.mytransport.sg/ltaodataservice/BusRoutes?$skip=8500"

    payload = {}
    headers = {
    'AccountKey': os.environ["LTA_ACCOUNT_KEY"]  # export LTA_ACCOUNT_KEY=... before running
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()['value']

    # print(type(response.text))

    route_190 = [r for r in data if r["ServiceNo"] == "190" and r['Direction'] == 2]

    route_190.sort(key=lambda r: (r["StopSequence"]))

    for i in range(len(route_190)):
        route_190[i]['StopSequence'] = i

    return route_190


if __name__ == "__main__":
    # Refresh the cached route used by params.py
    import json
    from pathlib import Path

    route = routeGet()
    assert len(route) == 31, f"expected 31 stops, got {len(route)}"
    path = Path(__file__).parent / "data" / "route_190_dir2.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(route, indent=2))
    print(f"wrote {len(route)} stops to {path}")
