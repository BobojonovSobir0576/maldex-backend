#
import json

import requests

def fetch_data(url, params=None):
    try:
        # Make the GET request with parameters
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Assuming the response is JSON

        else:
            return f"Failed with status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        return f"An error occurred: {e}"

# URL of the API
url = 'https://php-backend.portobello.ru/api/catalog-json/?apiKey=0a265cknZOs9ydbzJszxd5cL1lVMrXUfFrXHcqNU'

# Parameters to send with the request
params = {
    'key1': 'value1',
    'key2': 'value2'
}

# Calling the function
result = fetch_data(url, params)

with open('portobello_category.json', 'w', encoding='utf-8') as file:
    json.dump(result['sections'], file, indent=4, ensure_ascii=False)

