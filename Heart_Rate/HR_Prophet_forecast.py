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
    'response_2024-07-25_15min.json',
    'response_2024-07-26_15min.json',
    'response_2024-07-27_15min.json',
    'response_2024-07-28_15min.json',
    'response_2024-07-29_15min.json',
    'response_2024-07-30_15min.json',
    'response_2024-07-31_15min.json',
    'response_2024-08-01_15min.json'
]

# Initialize an empty list to store DataFrames
dfs = []

# Loop through each file and load the data
for file in file_list:
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
        dfs.append(df)

# Concatenate all DataFrames
concatenated_df = pd.concat(dfs)

# Downsample the data to every 15 minutes
concatenated_df = concatenated_df.resample('15T').mean().dropna()


# Save the concatenated data to a CSV file
concatenated_df.to_csv('concatenated_heart_rate_data.csv', index=True)

print("Concatenated data has been saved to 'concatenated_heart_rate_data.csv'.")


# Prepare the data for Prophet
df_prophet = concatenated_df.reset_index().rename(columns={'datetime': 'ds', 'value': 'y'})

# Split the data into training and test sets (let's use the last 2 days as test data)
train_df = df_prophet.iloc[:-192]
test_df = df_prophet.iloc[-192:]

# Initialize and fit the Prophet model on the training set
model = Prophet(daily_seasonality=True)
model.fit(train_df)

# Make future dataframe for the test period
future_dates = model.make_future_dataframe(periods=192, freq='15T')
forecast = model.predict(future_dates)

# Extract the forecast for the test period
forecast_test = forecast.iloc[-192:]

# Calculate evaluation metrics
mse = mean_squared_error(test_df['y'], forecast_test['yhat'])
mae = mean_absolute_error(test_df['y'], forecast_test['yhat'])
mape = (abs(test_df['y'] - forecast_test['yhat']) / test_df['y']).mean() * 100

print(f'Mean Squared Error (MSE): {mse}')
print(f'Mean Absolute Error (MAE): {mae}')
print(f'Mean Absolute Percentage Error (MAPE): {mape}%')

# Plot the forecasted values
fig = model.plot(forecast)
plt.plot(test_df['ds'], test_df['y'], label='Actual', color='orange')
plt.title('Predicción de la frecuencia cardíaca en los siguientes 2 días (LPM)')
plt.xlabel('Tiempo')
plt.ylabel('Frecuencia Cardíaca (LPM)')
plt.xticks(rotation=45, fontsize=10)  # Rotate and set font size for x-axis labels
plt.legend()
plt.show()

 #########################################################################
 ############### FORECAST FOR NEXT TWO DAYS ##############################
    
# Initialize and fit the Prophet model
model = Prophet(daily_seasonality=True)
model.fit(df_prophet)
    
# Create a DataFrame for future dates (next 2 days)
future_dates = model.make_future_dataframe(periods=192, freq='15T')
    
# Forecast the next 2 days
forecast = model.predict(future_dates)
    
# Select only the data for the next two days
next_two_days_forecast = forecast.iloc[-192:]
    
# Round the forecast values to integers
next_two_days_forecast['yhat'] = next_two_days_forecast['yhat'].round().astype(int)
   
# Plot the forecasted values with thresholds
fig = model.plot(forecast)
    
# Adding threshold lines
plt.axhline(y=86, color='red', linestyle='--', label='Inadecuado (>86 LPM)')
plt.axhline(y=62, color='blue', linestyle='--', label='Bueno (<62 LPM)')
    
plt.title('Predicción de la frecuencia cardíaca en los siguientes 2 días (LPM)')
plt.xlabel('Tiempo')
plt.ylabel('Frecuencia Cardíaca (LPM)')
plt.xticks(rotation=45, fontsize=10)  # Rotate and set font size for x-axis labels
plt.legend()  # Move legend to the bottom
plt.show()


# Export forecast data for the next two days to JSON file
next_two_days_forecast[['ds', 'yhat']].to_json('next_two_days_forecast.json', orient='records', date_format='iso')

print("Predicted data for the next two days has been exported to next_two_days_forecast.json")