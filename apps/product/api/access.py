import requests
import re
import time
import uuid
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db import transaction
from rest_framework import serializers
from requests.exceptions import RequestException

URL_ACCESS = 'https://api2.gifts.ru/export/v2/access'
URL_MANAGE_IP = "https://api2.gifts.ru/export/v2/manageip"
USERNAME = "20033_xmlexport"
PASSWORD = "O2NyQRLZ"

def fetch_data(url, auth=None, max_retries=5):
    retry_count = 0
    while retry_count < max_retries:
        try:
            with requests.Session() as session:
                if auth:
                    session.auth = auth
                response = session.get(url)
                response.raise_for_status()
                return response
        except requests.RequestException as e:
            if response.status_code == 429:
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"An error occurred: {e}")
                return None
    print("Max retries reached. Exiting.")
    return None

def extract_ip_address(html_content):
    ip_regex = r'\b\d{1,3}(?:\.\d{1,3}){3}\b'
    match = re.search(ip_regex, html_content)
    return match.group(0) if match else None

def update_ip_address(ip_address):
    with requests.Session() as session:
        session.auth = (USERNAME, PASSWORD)
        response = session.get(URL_MANAGE_IP)
        if response.status_code != 200:
            print("Failed to fetch the IP management page.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        if not form:
            print("No form found on the IP management page.")
            return

        form_data = {tag['name']: tag.get('value', '') for tag in form.find_all('input') if tag.get('name')}
        form_data['ip_to_register'] = ip_address
        form_action_url = urljoin(response.url, form.get('action', ''))
        post_response = session.post(form_action_url, data=form_data)
        if post_response.status_code == 200:
            print("IP address updated successfully.")
        else:
            print("Failed to update IP address.")

def get_data(url):
    count = 0
    response = fetch_data(URL_ACCESS, auth=(USERNAME, PASSWORD))
    if response:
        ip_address = extract_ip_address(response.text)
        if ip_address:
            update_ip_address(ip_address)
            count += 1
            data = fetch_data(url, auth=(USERNAME, PASSWORD))
            if count % 10 == 0:
                time.sleep(5)
        time.sleep(2)
        return data
    return None