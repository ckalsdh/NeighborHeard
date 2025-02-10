import os
import requests
import datetime
import pandas as pd
from dotenv import load_dotenv

def get_data(month, day, year=2024, dur=24, keys='ts,latitude,longitude,BMP280 Barometer'):
	load_dotenv()
	THINGSBOARD_URL = os.getenv('THINGSBOARD_URL')
	DEV = os.getenv('DEVICE')

	beg_time = datetime.datetime(year, month, day, 0, 0, 0) + datetime.timedelta(hours=7)
	end_time = beg_time + datetime.timedelta(hours=dur)
	inter = int((end_time-beg_time).total_seconds() * 1000)
	btime = beg_time.strftime('%s') + '000'
	etime = end_time.strftime('%s') + '000'

	jwt = requests.post(
		f"{THINGSBOARD_URL}/api/auth/login",
		headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
		json={'username': 'tenant@thingsboard.org', 'password': 'tenant'}
	).json()['token']

	url = f"{THINGSBOARD_URL}/api/plugins/telemetry/DEVICE/" + DEV \
		+ '/values/timeseries?keys=' + keys \
		+ '&startTs=' + btime \
		+ '&endTs=' + etime \
		+ '&interval=' + str(inter) \
		+ '&limit=1000000000&agg=NONE'

	data = requests.get(
		url, headers={'Content-Type': 'application/json','X-Authorization': f'Bearer {jwt}'}
	).json()

	del data['ts']

	dfs = [pd.DataFrame(data[key]).rename(columns={'value': key}) for key in data.keys()]
	df = pd.concat(dfs, axis=1, join='outer')
	df = df.loc[:,~df.columns.duplicated()]
	df = df.groupby('ts').first().reset_index()
	df = df.dropna()
	df = df.applymap(lambda x: float(f"{x.split('.')[0]}.{x.split('.')[1]}") if not isinstance(x, (int, float)) else x)

	return df