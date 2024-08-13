import requests
import json


# Replace these variables with your actual values
access_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1BOU0MiLCJzdWIiOiJDNThIRlYiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyb3h5IHJociBycHJvIiwiZXhwIjoxNzIzNjAwMDQ1LCJpYXQiOjE3MjM1NzEyNDV9.o4IJxZpnJG-_7Y3JdrK2PJMjn0UGUWRwBjtpDsRFGUg'

date = '2024-08-13'  # Example date
detail_level = '15min'  # Or '1sec'

# Define the endpoint URL
url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/{detail_level}.json"

# Define the headers
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Make the GET request
response = requests.get(url, headers=headers)

# Check the response status
if response.status_code == 200:
    # Parse the response JSON
    heart_rate_data = response.json()
    #print(json.dumps(heart_rate_data, indent=4))  # Pretty print the data
    
    # Define the file name
    file_name = f"response_{date}_{detail_level}.json"

    # Write the data to a JSON file
    with open(file_name, 'w') as file:
        json.dump(heart_rate_data, file, indent=4)
        
    print(f"Data saved to {file_name}")
    
else:
    print(f"Failed to retrieve data: {response.status_code}")
    print(response.text)

