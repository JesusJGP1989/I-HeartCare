# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 00:04:24 2024

@author: Jesús García Palomera
@Project: InnovatecNM  "I-HeartCare"
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Load forecasted data
with open('next_two_days_forecast.json', 'r') as f:
    forecast_data = json.load(f)
forecast_df = pd.DataFrame(forecast_data)
forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
forecast_df.set_index('ds', inplace=True)

# List of files to load actual data
actual_files = [
    'response_2024-08-02_15min.json',
    'response_2024-08-03_15min.json'
]

# Initialize an empty list to store actual DataFrames
actual_dfs = []

# Loop through each file and load the actual data
for file in actual_files:
    with open(file, 'r') as f:
        data = json.load(f)
        # Extract the dataset
        dataset = data["activities-heart-intraday"]["dataset"]
        # Create a DataFrame
        df = pd.DataFrame(dataset)
        # Convert the time column to datetime
        df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
        df['date'] = pd.to_datetime(file.split('_')[1], format='%Y-%m-%d')
        # Combine date and time into a single datetime index
        df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
        # Set the datetime column as the index
        df.set_index('datetime', inplace=True)
        # Drop unnecessary columns
        df.drop(columns=['time', 'date'], inplace=True)
        # Append the DataFrame to the list
        actual_dfs.append(df)

# Concatenate all actual DataFrames
actual_df = pd.concat(actual_dfs)

# Downsample the actual data to every 15 minutes
actual_df = actual_df.resample('15T').mean().dropna()

# Prepare the actual data for comparison
actual_df = actual_df.rename(columns={'value': 'actual'})

# Merge forecast and actual data
comparison_df = forecast_df.join(actual_df, how='outer')

# Fill missing values with forward fill method
comparison_df['actual'].fillna(method='ffill', inplace=True)

# Calculate evaluation metrics
mse = mean_squared_error(comparison_df['actual'], comparison_df['yhat'])
mae = mean_absolute_error(comparison_df['actual'], comparison_df['yhat'])
mape = (abs(comparison_df['actual'] - comparison_df['yhat']) / comparison_df['actual']).mean() * 100

print(f'Mean Squared Error (MSE): {mse}')
print(f'Mean Absolute Error (MAE): {mae}')
print(f'Mean Absolute Percentage Error (MAPE): {mape}%')

# Plot the forecasted vs actual values
plt.figure(figsize=(10, 6))
plt.plot(comparison_df.index, comparison_df['actual'], label='Actual', color='orange')
plt.plot(comparison_df.index, comparison_df['yhat'], label='Forecast', color='blue')

# Check if the uncertainty interval columns exist before plotting them
if 'yhat_lower' in comparison_df.columns and 'yhat_upper' in comparison_df.columns:
    plt.fill_between(comparison_df.index, comparison_df['yhat_lower'], comparison_df['yhat_upper'], color='blue', alpha=0.2)

plt.title('Comparación de la predicción de la frecuencia cardíaca con los valores reales (LPM)')
plt.xlabel('Tiempo')
plt.ylabel('Frecuencia Cardíaca (LPM)')
plt.xticks(rotation=45, fontsize=10)
plt.legend(loc='lower left')
plt.show()
