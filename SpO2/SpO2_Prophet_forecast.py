# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 00:04:24 2024

@author: Jesús García Palomera
@Project: InnovatecNM  "I-HeartCare"
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error

# List of files to concatenate
file_list = [
    'response_2024-07-06_main_sleep.json',
    'response_2024-07-07_main_sleep.json',
    'response_2024-07-08_main_sleep.json',
    'response_2024-07-09_main_sleep.json',
    'response_2024-07-11_main_sleep.json',
    'response_2024-07-12_main_sleep.json',
    'response_2024-07-13_main_sleep.json',
    'response_2024-07-14_main_sleep.json'
]

# Initialize an empty list to store DataFrames
dfs = []

# Loop through each file and load the data
for file in file_list:
    with open(file, 'r') as f:
        data = json.load(f)
        # Extract the dataset
        dataset = data["minutes"]
        # Create a DataFrame
        df = pd.DataFrame(dataset)
        # Convert the time column to datetime
        df['minute'] = pd.to_datetime(df['minute'])
        df = df.rename(columns={'minute': 'ds', 'value': 'y'})
        # Append the DataFrame to the list
        dfs.append(df)

# Concatenate all DataFrames
df_prophet = pd.concat(dfs, ignore_index=True)

# Plot the data to understand the irregular sampling
plt.figure(figsize=(10, 6))
plt.plot(df_prophet['ds'], df_prophet['y'], marker='o', linestyle='-', label='SpO2 value')
plt.title('SpO2 from users main sleep')
plt.xlabel('Time')
plt.ylabel('SpO2 (%)')
plt.legend()
plt.show()

# Train the Prophet model
model = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=False)
model.fit(df_prophet)

# Create future dates
future_dates = model.make_future_dataframe(periods=2880, freq='T')  # Create a 48-hour future dataframe with 1-minute intervals
forecast = model.predict(future_dates)

# Plot the forecasted values with thresholds
fig = model.plot(forecast)
plt.axhline(y=90, color='red', linestyle='--', label='Inadecuado (<90%)')
plt.axhline(y=95, color='green', linestyle='--', label='Normal (95%)')
plt.title('Predicción de la medición de oxígeno en los siguientes 2 días (SpO2)')
plt.xlabel('Tiempo')
plt.ylabel('Medición de oxígeno (SpO2)')
plt.legend(loc='lower left')  # Move legend to bottom
plt.show()

