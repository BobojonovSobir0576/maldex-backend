import json
import requests


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def upload_product(data):
    url = 'http://192.168.0.163:8000/product/auto/uploader/'
    try:
        response = requests.post(url, json=data, proxies={"http": None, "https": None})
        # print(response.json())
        return response.status_code == 201
    except requests.exceptions.RequestException as e:
        print(e)
        return False


def check_product_exists(product_id):
    url = f"http://192.168.0.163:8000/product/{product_id}/"
    try:
        response = requests.get(url, proxies={"http": None, "https": None})
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except requests.exceptions.RequestException as e:
        print(e)
        return False, None


def update_product_price(product_id, new_price, new_discount_price, quantity):
    url = f"http://192.168.0.163:8000/product/auto/uploader/{product_id}/"
    data = {
        'price': new_price,
        'discount_price': new_discount_price,
        'quantity': quantity
    }
    try:
        response = requests.put(url, json=data, proxies={"http": None, "https": None})
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(e)
        return False, None


def delete_product(product_id):
    url = f"http://192.168.0.163:8000/product/{product_id}/"
    try:
        response = requests.delete(url, proxies={"http": None, "https": None})
        if response.status_code == 204:
            print(f"Successfully deleted product ID {product_id}")
            return True
        else:
            print(f"Failed to delete product ID {product_id}: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(e)
        return False


def get_id_from_url(url):
    product_id = url.split('/')[-2]
    return '7' + product_id.zfill(7)


def process_happygifts_data():
    try:
        products = read_json('product/happygifts.json')
    except Exception as e:
        print(f"Failed to read data: {str(e)}")
        return
    local_product_ids = {product['ID'] for product in products}

    remote_product_ids = get_all_product_ids()
    for product_id in remote_product_ids:
        if product_id not in local_product_ids:
            delete_product(product_id)

    for product_set in products:
        products_set = product_set['SubItems']['SubItem']
        products_set = [products_set] if type(products_set) == dict else products_set
        category_id = product_set['GROUP_ID']
        article = product_set['Article']
        weight = product_set['UnitWeight']
        brand = product_set['BrendName']
        for product in products_set:
            product_id = product['ID']
            exists, existing_product_data = check_product_exists(product_id)
            if exists:
                existing_price = existing_product_data['price']
                existing_quantity = existing_product_data['quantity']
                if float(existing_price) != float(product['Price']) or float(existing_quantity) != int(product['FreeQuantityCenter']):
                    print('price updated')
                    update_product_price(product_id, product['Price'], product['PriceDiscount'], existing_product_data['quantity'])
            else:
                data = {
                    'id': product_id,
                    'categoryId': category_id,
                    'name': product['NAME'],
                    'brand': brand,
                    'article': article,
                    'description': product['Description'],
                    'material': product['Material1'],
                    'weight': weight,
                    'quantity': product['FreeQuantityCenter'],
                    'color_name': product['Color'],
                    'image_set': [{"name": 'https://happygifts.ru' + url} for url in product['Image']] if 'Image' in product else [],
                    'price': product['Price'],
                    'discount_price': product['PriceDiscount'] if 'PriceDiscount' in product else 0,
                    'product_size': product['Size'],
                    'pack': {
                        'quantity': product['PackagingQuantity'],
                        'weight': product['PackagingWeight'],
                        'volume': product['PackagingVolume'],
                        'size': product['PackagingSize'],
                        'material': product['PackagingMaterial'],
                        'type': product['PackagingType'],
                    },
                }
                upload_product(data)


def get_all_product_ids():
    url = 'http://192.168.0.163:8000/product/all_ids/'
    try:
        response = requests.get(url, proxies={"http": None, "https": None})
        if response.status_code == 200:
            return set(response.json()['product_ids'])
        return set()
    except requests.exceptions.RequestException as e:
        print(e)
        return set()


def main():
    process_happygifts_data()


if __name__ == "__main__":
    main()
