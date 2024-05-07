import requests
import xmltodict
import json
import os

# Set the URL
url = 'https://happygifts.ru/http/api.php'

# Parameters to be sent to the API
params = {
    'USER': 'hg7715815318',
    'PW': 'O]4s+Iv3ca39430424df94ad8c0976be1df0ae1a',
    'type': 'all'
}

def extract_and_save_groups(xml_content, filename):
    # Ensure the directory exists
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        # Parse XML content to a Python dictionary
        parsed_xml = xmltodict.parse(xml_content)
        # Extract the Groups object
        # print(json.dumps(parsed_xml, indent=4, ensure_ascii=False))
        groups_data = parsed_xml['Catalog_items_export']['Items']['Item']
        # Convert the extracted data to JSON and save to file
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(groups_data, json_file, indent=4, ensure_ascii=False)
        print(f"Group data extracted and saved to {filename} successfully.")
    except Exception as e:
        print(f"Failed to extract group data or save to JSON: {e}")

def main():
    try:
        # Sending GET request
        response = requests.get(url, params=params)

        # Checking the status code of the response
        if response.status_code == 200:
            # Print the response for debugging
            # print("Response received:", response.text)  # Print first 500 characters of response
            print("Extracting Group data, converting to JSON...")
            extract_and_save_groups(response.text, 'product/happygifts.json')
        else:
            print("Failed to retrieve data: HTTP status code", response.status_code)
    except requests.exceptions.RequestException as e:
        print("HTTP Request failed: ", e)

if __name__=='__main__':
    main()
