#BLS_data_collection

import requests
import os
import pandas as pd
import json
from datetime import datetime

URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
API_key = "2e94f53db1984894b301b64867ac70c0"
CSV_file = "BLS_data.csv"
seriesId = [
    'LNS12000000',  # Civilian Employment (Seasonally Adjusted)
    'LNS13000000',  # Civilian Unemployment (Seasonally Adjusted)
    'LNS14000000',  # Unemployment Rate (Seasonally Adjusted)
    'CES0000000001',  # Total Nonfarm Employment (Seasonally Adjusted)
    'CES0500000002',  # Total Private Average Weekly Hours of All Employees (Seasonally Adjusted)
    'CES0500000003'   # Total Private Average Hourly Earnings of All Employees (Seasonally Adjusted)
]
# Function for collecting  data - look at sample code again
def collect_bls_data(seriesId, start_year, end_year):
    headers = {'Content-type': 'application/json'}
    payload = json.dumps({
        "seriesid": seriesId,
        "startyear": int(start_year), # "startyear": "2019","endyear": str(datetime.now().year) not okay?
        "endyear": int(end_year),
        "registrationkey": API_key
    })
    response = requests.post(URL, data=payload, headers=headers)
    response.raise_for_status()  # Handles HTTP errors
    return response.json()

#processing data - json
def process_bls_data(json_data):
    processed_data = []
    if 'Results' in json_data and 'series' in json_data['Results']:
        for series in json_data['Results']['series']:
            series_id = series['seriesID']
            for item in series['data']:
                year = int(item['year'])
                period = item['period']
                if period.startswith('M'):  # Monthly period
                    month = period[1:]
                    date_str = f"{year}-{month}-01"
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    value = float(item['value'])
                    processed_data.append({
                        "series_id": series_id,
                        "year": year,
                        "period": period,
                        "date": date,
                        "value": value,
                    })
    return pd.DataFrame(processed_data)

def update_bls_data():
    #start year=2019,  update data for latest month
    if os.path.exists(CSV_file):
        existing_data = pd.read_csv(CSV_file)
        existing_years = existing_data['year'].astype(int)
        start_year = existing_years.max() + 1
    else:
        start_year = 2019

    end_year = datetime.now().year

    json_data = collect_bls_data(seriesId, start_year, end_year)
    updated_df = process_bls_data(json_data)

    if os.path.exists(CSV_file):
        existing_df = pd.read_csv(CSV_file)
        combined_df = pd.concat([existing_df, updated_df]).drop_duplicates(subset=['series_id', 'year', 'period'], keep='last')
    else:
        combined_df = updated_df

    combined_df.to_csv(CSV_file, index=False)

if __name__ == "__main__":
    update_bls_data()