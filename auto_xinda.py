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


def process_xinda_data():
    try:
        products = read_json('product/xinda_eload.json')
        product_quantities = read_json('product/product_quantities.json')
    except Exception as e:
        print(f"Failed to read data: {str(e)}")
        return
    local_product_ids = {get_id_from_url(product['URL']) for product in products}

    remote_product_ids = get_all_product_ids()
    for product_id in remote_product_ids:
        if product_id not in local_product_ids:
            delete_product(product_id)

    for product in products:
        product_id = get_id_from_url(product['URL'])
        quantity = 0
        for pr in product_quantities:
            if pr['Артикул'] == product['Артикул']:
                quantity = int(pr['ОстатокСкладЕвропа']) + int(pr['СкладМоскваСвободный'])
                break
        exists, existing_product_data = check_product_exists(product_id)
        if exists:
            existing_price = existing_product_data['price']
            existing_quantity = existing_product_data['quantity']
            if int(existing_price) != int(product['Цена']) or float(existing_quantity) != quantity:
                print('price updated')
                update_product_price(product_id, product['Цена'], 0, existing_product_data['quantity'])
        else:
            categories = product['Разделы']['Ид'] if product['Разделы'] else [None]
            category_id = categories[-1]
            prints = product['ТипыНанесения']['ТипНанесения'] if product['ТипыНанесения'] else []
            if type(prints) == dict:
                prints = [prints]

            data = {
                'id': product_id,
                'categoryId': category_id,
                'name': product['Наименование'],
                'brand': product['Характеристики']['Бренд'],
                'article': product['Артикул'],
                'description': product['ОписаниеРус'],
                'material': product['Характеристики']['Материал'] if 'Материал' in product['Характеристики'] else 'No material',
                'weight': product['Характеристики']['ВесНетто'],
                'quantity': quantity,
                'color_name': product['Характеристики']['Цвет'].split(';')[0],
                'image_set': [{"name": url} for url in product['Фотографии']['Фотография']] if product['Фотографии'] else [],
                'price': product['Цена'],
                'discount_price': None,
                'prints': [{"name": prinT['Тип']} for prinT in prints],
                'product_size': product['Характеристики']['Размер'],
                'pack': product['Упаковка'],
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
    process_xinda_data()


if __name__ == "__main__":
    main()
