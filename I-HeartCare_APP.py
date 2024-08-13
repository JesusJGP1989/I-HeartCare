import requests
import json
import base64

class FitbitClient:
    def __init__(self, client_id, client_secret, refresh_token, access_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.token_url = 'https://api.fitbit.com/oauth2/token'
        self.api_base_url = 'https://api.fitbit.com/1/user/-/'

    def _encode_client_creds(self):
        client_creds = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(client_creds.encode()).decode()

    def refresh_access_token(self):
        headers = {
            'Authorization': f'Basic {self._encode_client_creds()}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
        }
        response = requests.post(self.token_url, headers=headers, data=data)

        if response.status_code == 200:
            new_tokens = response.json()
            self.access_token = new_tokens['access_token']
            self.refresh_token = new_tokens['refresh_token']
            print("Access Token refreshed successfully.")
        else:
            raise Exception(f"Failed to refresh token: {response.status_code} - {response.text}")

    def get_heart_rate_data(self, date, detail_level='15min'):
        if not self.access_token:
            raise Exception("Access token is missing. Please refresh the token first.")
        
        url = f"{self.api_base_url}activities/heart/date/{date}/1d/{detail_level}.json"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            heart_rate_data = response.json()
            file_name = f"response_{date}_{detail_level}.json"
            with open(file_name, 'w') as file:
                json.dump(heart_rate_data, file, indent=4)
            print(f"Data saved to {file_name}")
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code} - {response.text}")

# Example usage
client_id = '23PNSC'
client_secret = '75b5591bff1b4b5e71d0409cde5463e0'
refresh_token = 'd2110c59eb410f131d27c55eaa0a22582e79160549f6a61486118baa45f71fbb'
access_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1BOU0MiLCJzdWIiOiJDNThIRlYiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyb3h5IHJociBycHJvIiwiZXhwIjoxNzIzNjAwMDQ1LCJpYXQiOjE3MjM1NzEyNDV9.o4IJxZpnJG-_7Y3JdrK2PJMjn0UGUWRwBjtpDsRFGUg'

# Create a client instance
fitbit_client_1 = FitbitClient(client_id, client_secret, refresh_token, access_token)

# Refresh the access token
#fitbit_client_1.refresh_access_token()

# Get heart rate data
fitbit_client_1.get_heart_rate_data(date='2024-08-13', detail_level='15min')
