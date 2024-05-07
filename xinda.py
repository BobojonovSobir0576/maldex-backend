import json
import os
from ftplib import FTP
import xmltodict

def convert_xml_to_json_and_save(xml_dict, filename):
    # Ensure the directory exists
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        # Save as JSON
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(xml_dict, json_file, indent=4, ensure_ascii=False)
        print(f"XML data converted and saved to {filename} successfully.")
    except Exception as e:
        print(f"Failed to save to JSON: {e}")

def get_data_from_elod_ftp():
    ftp = FTP()
    try:
        ftp.connect('static.xindaorussia.ru')
        ftp.login(user='maldex.ru', passwd='IR5XKKxKWR7JVA7A')

        filename = 'production.xml'
        local_filename = os.path.join('downloads', filename)
        # Ensure the local directory exists
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)

        # Download the file
        with open(local_filename, 'wb') as file:
            ftp.retrbinary(f'RETR {filename}', file.write)

        print(f"File {filename} downloaded successfully")

        # Read the downloaded XML and convert it
        with open(local_filename, 'rb') as file:
            xml_content = file.read()
            parsed_xml = xmltodict.parse(xml_content)
            # Navigate the parsed XML to extract specific parts, for example "Каталог" -> "Разделы" -> "Раздел"
            target_section = parsed_xml["Каталог"]["Товары"]["Товар"]
            print(len(target_section))
            convert_xml_to_json_and_save(target_section, 'product/xinda_eload.json')

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ftp.quit()
        
def get_catalogue_data():
    ftp = FTP()
    try:
        ftp.connect('static.xindaorussia.ru')
        ftp.login(user='maldex.ru', passwd='IR5XKKxKWR7JVA7A')

        filename = 'catalogue.xml'
        local_filename = os.path.join('downloads', filename)
        # Ensure the local directory exists
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)

        # Download the file
        with open(local_filename, 'wb') as file:
            ftp.retrbinary(f'RETR {filename}', file.write)

        print(f"File {filename} downloaded successfully")

        # Read the downloaded XML and convert it
        with open(local_filename, 'rb') as file:
            xml_content = file.read()
            parsed_xml = xmltodict.parse(xml_content)
            # Navigate the parsed XML to extract specific parts, for example "Каталог" -> "Разделы" -> "Раздел"
            target_section = parsed_xml["Каталог"]['Товары']['Товар']
            print(len(target_section))
            convert_xml_to_json_and_save(target_section, 'product/product_quantities.json')

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ftp.quit()

def main():
    get_data_from_elod_ftp()
    get_catalogue_data()

if __name__=="__main__":
    main()