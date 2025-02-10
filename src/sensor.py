##################################
# script to run IN Termux
##################################
import requests, json, time
from pimux import scrip

headers = {"Content-Type": "application/json", "Authorization":"Bearer tj8QNWt14L8EqphPSZDX"}
url=f"http://3.101.37.83:8080/api/v1/tj8QNWt14L8EqphPSZDX/telemetry"

while (1):
        ts = time.time()
        gpscmd = scrip.compute(f"termux-location -p passive -r last")
        senread = scrip.compute(f"termux-sensor -s 'K6DS3TR Accelerometer,BMP280 Barometer' -n 1")
        gps=json.loads(gpscmd["output"])
        sen=json.loads(senread["output"])
        tmp=sen["K6DS3TR Accelerometer"]
        tmp2=sen["BMP280 Barometer"]
        data=json.dumps({"ts":ts,"latitude":gps["latitude"],"longitude":gps["longitude"],"K6DS3TR Accelerometer":tmp["values"][0],"BMP280 Barometer":tmp2["values"][0]})
        resp=requests.post(url, headers=headers, data=data)
