import requests
import re
import xmltodict
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

from requests.exceptions import RequestException

URL_ACCESS = 'https://api2.gifts.ru/export/v2/access'
URL_MANAGE_IP = "https://api2.gifts.ru/export/v2/manageip"
USERNAME = "20033_xmlexport"
PASSWORD = "O2NyQRLZ"



def fetch_data(url, params=None, auth=None):
    try:
        with requests.Session() as session:
            if auth:
                session.auth = auth
            response = session.get(url, params=params)
            response.raise_for_status()  # This will raise an exception for HTTP errors
            return response
    except RequestException as e:
        raise ValueError(f"An error occurred: {e}")  # Raise an exception instead of returning a string



def extract_ip_address(html_content):
    ip_regex = r'\b\d{1,3}(?:\.\d{1,3}){3}\b'
    match = re.search(ip_regex, html_content)
    return match.group(0) if match else None


def update_ip_address(ip_address):
    with requests.Session() as session:
        session.auth = (USERNAME, PASSWORD)
        response = session.get(URL_MANAGE_IP)
        if response.status_code != 200:
            return "Failed to fetch the IP management page."

        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        form_data = {tag['name']: tag.get('value', '') for tag in form.find_all('input') if tag.get('name')}
        form_data['ip_to_register'] = ip_address
        form_action_url = urljoin(response.url, form.get('action', ''))
        post_response = session.post(form_action_url, data=form_data)
        if post_response.status_code == 200:
            print("IP address updated successfully.")
        else:
            print("Failed to update IP address.")


def get_data(URL):
    try:
        response = fetch_data(URL_ACCESS, auth=(USERNAME, PASSWORD))
        ip_address = extract_ip_address(response.text)
        if ip_address:
            update_ip_address(ip_address)
        data = fetch_data(URL, auth=(USERNAME, PASSWORD))
        return data
    except ValueError as e:
        print(e)  # Handle or log the error appropriately
        return None  # Return None or a suitable default
