import json
import time

import requests
import re

USERNAME = "20033_xmlexport"
PASSWORD = "O2NyQRLZ"


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def upload_product(data):
    print('sobir bot')
    url = 'http://5.35.82.80:9090/product/auto/uploader/'
    try:
        response = requests.post(url, json=data, proxies={"http": None, "https": None})
        print(response.json())
        return response.status_code == 201
    except requests.exceptions.RequestException as e:
        print(e)
        return False


def check_product_exists(product_id):
    url = f"http://5.35.82.80:9090/product/{product_id}/"
    try:
        response = requests.get(url, proxies={"http": None, "https": None})
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except requests.exceptions.RequestException as e:
        print(e)
        return False, None


def update_product_price(product_id, new_price, new_discount_price, quantity):
    url = f"http://5.35.82.80:9090/product/auto/uploader/{product_id}/"
    data = {
        'price': new_price,
        'discount_price': new_discount_price,
        'quantity': quantity,
    }
    try:
        response = requests.put(url, json=data, proxies={"http": None, "https": None})
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(e)
        return False, None


def delete_product(product_id):
    url = f"http://5.35.82.80:9090/product/{product_id}/"
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


def process_portobello_data():
    try:
        products = read_json('products/product/portobello.json')
        price_data = read_json('products/price/portobello_price.json')
    except Exception as e:
        print(f"Failed to read data: {str(e)}")
        return

    local_product_ids = {product['id'] for product in products}
    price_dict = {item['productId']: item['price'] for item in price_data}
    price_discount_dict = {item['productId']: item['discountPrice'] for item in price_data}
    local_price = 0

    remote_product_ids = get_all_product_ids()
    for product_id in remote_product_ids:
        if product_id not in local_product_ids:
            delete_product(product_id)

    count = 0
    for product in products:
        count += 1
        product_id = product['id']
        exists, existing_product_data = check_product_exists(product_id)
        local_discount_price = 0
        if exists:
            existing_price = existing_product_data['price']
            existing_quantity = existing_product_data.get('warehouse''quantity', 0)
            local_price = price_dict.get(product_id)
            local_discount_price = price_discount_dict.get(product_id)
            if int(existing_price) != int(local_price) or float(existing_quantity) != float(
                    product.get('warehouse''quantity', 0)):
                update_product_price(product_id, local_price, local_discount_price, product.get('warehouse''quantity', 0))
        else:
            local_price = price_dict.get(product_id)
            data = {
                'id': product_id,
                'categoryId': product['sectionId'],
                'name': product['name'],
                'brand': product['brand'],
                'article': product['article'],
                'description': product.get('description'),
                'material': product['material1'] if product['material1'] else 'No material',
                'weight': product['weight'],
                'warehouse': product['warehouse'],
                'sizes': product.get('sizes', None),
                'color_name': product.get('color1', 'ЧЕРНЫЙ'),
                'image_set': [{"name": url} for url in product['images']],
                'price': local_price,
                'discount_price': local_discount_price,
                'prints': [{"name": name} for name in product.get('tuning', [])],
                'site': 'Portobello.ru'
            }
            upload_product(data)
        if count % 1000 == 0:
            time.sleep(10)
    time.sleep(5)


def get_id_from_xinda(url):
    product_id = url.split('/')[-2]
    return '7' + product_id.zfill(7)


def process_xinda_data():
    try:
        products = read_json('products/product/xinda_eload.json')
        product_quantities = read_json('products/product/product_quantities.json')
    except Exception as e:
        print(f"Failed to read data: {str(e)}")
        return
    local_product_ids = {get_id_from_xinda(product['URL']) for product in products}

    remote_product_ids = get_all_product_ids()
    for product_id in remote_product_ids:
        if product_id not in local_product_ids:
            delete_product(product_id)
    count = 0
    sizes = {}
    warehouses = {}
    PRODUCTS = {}
    for product in products:
        count += 1
        product_id = get_id_from_xinda(product['URL'])
        vendor_code = product['Артикул']
        vendor = '.'.join(vendor_code.split('.')[:2])
        size = '.'.join(vendor_code.split('.')[2:])
        sizes[product_id] = {} if size else None
        for pr in product_quantities:
            if pr['Артикул'] == product['Артикул']:
                quantity = int(pr['ОстатокСкладЕвропа']) + int(pr['СкладМоскваСвободный'])
                if size:
                    sizes[product_id][size] = quantity
                warehouses[product_id] = {} if product_id not in warehouses else warehouses[product_id]
                if 'Европа' not in warehouses[product_id]:
                    warehouses[product_id]['Европа'] = int(pr['ОстатокСкладЕвропа'])
                else:
                    warehouses[product_id]['Европа'] += int(pr['ОстатокСкладЕвропа'])
                if 'Москва' not in warehouses[product_id]:
                    warehouses[product_id]['Москва'] = int(pr['СкладМоскваСвободный'])
                else:
                    warehouses[product_id]['Москва'] += int(pr['СкладМоскваСвободный'])
                break
        categories = product['Разделы']['Ид'] if product['Разделы'] else [None]
        category_id = categories[-1]
        prints = product['ТипыНанесения']['ТипНанесения'] if product['ТипыНанесения'] else []
        if type(prints) == dict:
            prints = [prints]
        if product_id not in PRODUCTS:
            PRODUCTS[product_id] = {
                'id': product_id,
                'categoryId': category_id,
                'name': product['Наименование'],
                'brand': product['Характеристики']['Бренд'],
                'article': vendor,
                'description': product['ОписаниеРус'],
                'material': product['Характеристики']['Материал'] if 'Материал' in product[
                    'Характеристики'] else 'No material',
                'weight': product['Характеристики']['ВесНетто'],
                'color_name': product['Характеристики']['Цвет'].split(';')[0],
                'image_set': [{"name": url} for url in product['Фотографии']['Фотография']] if product[
                    'Фотографии'] else [],
                'price': product['Цена'],
                'discount_price': None,
                'prints': [{"name": prinT['Тип']} for prinT in prints],
                'product_size': product['Характеристики']['Размер'],
                'pack': product['Упаковка'],
                'site': 'Xindaorussia.ru'
            }
    for key in PRODUCTS:
        count += 1
        product = PRODUCTS[key]
        product['sizes'] = sizes[key]
        warehouses = warehouses[key]
        product['warehouse'] = [
            {
                'name': warehouse,
                'quantity': warehouses[warehouse],
            } for warehouse in warehouses.keys()
        ]

        exists, existing_product_data = check_product_exists(key)
        if exists:
            update_product_price(key, product['price'], product['discount_price'], product['sizes'], product['warehouse'])
        else:
            upload_product(product)
        if count % 1000 == 0:
            time.sleep(10)
    time.sleep(5)


def get_all_product_ids():
    url = 'http://5.35.82.80:9090/product/all_ids/'
    try:
        response = requests.get(url, proxies={"http": None, "https": None})
        if response.status_code == 200:
            return set(response.json()['product_ids'])
        return set()
    except requests.exceptions.RequestException as e:
        print(e)
        return set()


def get_id_from_url(product_id):
    return '3' + product_id.zfill(7)


def process_name(data):
    product_name = data['name']
    if ',' in product_name:
        main_part, color = product_name.split(',', 1)
        main_part = main_part.strip()
        color = color.strip()
        return color
    else:
        return "Черный"


def fetch_stock_amount(stock_data, product_id):
    """Fetches the stock amount for a given product_id from loaded stock data."""
    # Iterate through each product in the stock data
    for item in stock_data['doct']['stock']:
        if item['product_id'] == product_id:
            return int(item['amount'])  # Return the amount as an integer
    return 0


def gifts_data():
    CLEANR = re.compile('<.*?>')
    try:
        products = read_json('products/product/gifts_product.json')
        stock_data = read_json('products/product/gifts_stock.json')
    except Exception as e:
        print(f"Failed to read data: {str(e)}")
        return

    count = 0
    for product in products['doct']['product']:
        count += 1
        product_id = get_id_from_url(product['product_id'])
        amount = fetch_stock_amount(stock_data, product['product_id'])
        exists, existing_product_data = check_product_exists(product_id)

        if exists:
            existing_price = existing_product_data['price']
            existing_quantity = existing_product_data['quantity']
            local_price = product['price']['price']
            local_discount_price = 0
            if int(existing_price) != float(local_price) or float(existing_quantity) != amount:
                update_product_price(product_id, local_price, local_discount_price, existing_quantity)
        else:
            base_url = f"https://api2.gifts.ru/export/v2/catalogue/"
            description = product.get('content', 'No Content')
            if description is None:
                description = 'No Content'
            description = re.sub(CLEANR, '', description)
            category_id = product.get('category', {}).get('page_id', 'Unknown')
            pack = product.get('pack', {})
            sizex = pack.get('sizex', 0)
            sizey = pack.get('sizey', 0)
            sizez = pack.get('sizez', 0)
            image_set = []
            if 'product_attachment' in product:
                image_list = product['product_attachment']
                image_set = [{'name': base_url + item['image']} for item in image_list if
                             isinstance(item, dict) and 'image' in item]
            data = {
                'id': product_id,
                'categoryId': category_id,
                'name': product['name'],
                'brand': product.get('brand', 'No brand'),
                'article': product.get('code', 0),
                'description': description,
                'material': product.get('matherial', 'No material'),
                'weight': product.get('weight', 0),
                'quantity': amount,
                'color_name': process_name(product),
                'image_set': image_set,
                'price': product['price']['price'],
                'discount_price': None,
                'prints': product.get('print', []),
                'product_size': f"Размер: Длина {sizex} см., ширина {sizey} см., высота {sizez} см., диаметр 0 см.",
                'pack': product.get('pack', []),
                'site': 'Gifts.ru',
                # 'sets': [{'product_id': part_id} for part_id in product.get('part_ids', [])]
            }
            upload_product(data)
        if count % 1000 == 0:
            time.sleep(10)
    time.sleep(5)


def get_id_from_happy_gifts(product_id):
    return '5' + product_id.zfill(9)


def process_happygifts_data():
    try:
        products = read_json('products/product/happygifts.json')
    except Exception as e:
        print(f"Failed to read data: {str(e)}")
        return
    local_product_ids = {product['ID'] for product in products}

    remote_product_ids = get_all_product_ids()
    for product_id in remote_product_ids:
        if product_id not in local_product_ids:
            delete_product(product_id)

    count = 1
    sizes = {}
    warehouses = {}
    PRODUCTS = {}
    for product_set in products:
        count += 1
        sub_item = product_set['SubItems']['SubItem']
        sub_item = [sub_item] if type(sub_item) != list else sub_item
        category_id = product_set['GROUP_ID']
        brand = product_set['BrendName']
        materials = product_set['MATERIALS']
        for product in sub_item:
            product_id = product['ID']
            vendor_code = product['FullArticle']
            vendor = vendor_code.split('/')[0]
            size = vendor_code.split('/')[1] if '/' in vendor_code else product['Size']
            quantity = product['FreeQuantityCenter']
            if vendor not in PRODUCTS:
                PRODUCTS[vendor] = {
                    'id': product_id,
                    'categoryId': category_id,
                    'name': product['NAME'],
                    'brand': brand,
                    'article': vendor,
                    'description': product['Description'],
                    'material': materials,
                    'weight': product['UnitWeight'],
                    'is_new': product['New'],
                    'color_name': product['Color'],
                    'image_set': [{"name": f'https://happygifts.ru{url}'} for url in product['Image']] if product['Image'] else [],
                    'price': product['Price'],
                    'discount_price': product['PriceDiscount'],
                    'product_size': size,
                    'pack': {
                        'Количество': product['PackagingQuantity'],
                        'Масса': product['PackagingWeight'],
                        'Объем': product['PackagingVolume'],
                        'Материал': product['PackagingMaterial'],
                        'Тип упаковки': product['PackagingType']
                    },
                    'site': 'happy-gifts.ru'
                }

            if vendor not in sizes:
                if '/' in vendor_code:
                    sizes[vendor] = {}
                    sizes[vendor][size] = quantity
                else:
                    sizes[vendor][None] = quantity
            else:
                if '/' in vendor_code:
                    sizes[vendor][size] = quantity
                else:
                    sizes[vendor][None] = quantity

            if vendor not in warehouses:
                warehouses[vendor] = {
                    'Москва': quantity,
                    'Европа': 0
                }
            else:
                warehouses[vendor]['Москва'] += quantity

    for vendor in PRODUCTS:
        count += 1
        product = PRODUCTS[vendor]
        product['sizes'] = sizes[vendor]
        warehouse = warehouses[vendor]
        product['warehouse'] = [
            {
                'name': city,
                'quantity': warehouse[city],
            } for city in warehouse.keys()
        ]

        exists, existing_product_data = check_product_exists(product['id'])
        if exists:
            update_product_price(product['id'], product['price'], product['discount_price'], product['sizes'], product['warehouse'])
        else:
            upload_product(product)
        if count % 1000 == 0:
            time.sleep(10)
    time.sleep(5)


def get_id_from_oasis(product_id):
    product_id_str = str(product_id)
    if '-' in product_id_str:
        product_id_str = product_id_str.split('-')[-1]
    padded_id = product_id_str.zfill(9)
    return '6' + padded_id


def extract_color_name(parameters):
    for param in parameters:
        if param.get('@name') == "Цвет товара":
            return param.get('#text', '')
    return ''


def extract_matherial(parameters):
    for param in parameters:
        if param.get('@name') == "Материал товара":
            return param.get('#text', '')
    return ''


def extract_sizes(parameters):
    for param in parameters:
        if param.get('@name') == "Размер товара (см)":
            sizes = param.get('#text', '')
            try:
                sizex, sizey, sizez = sizes.split(' х ')
                return float(sizex), float(sizey), float(sizez)
            except ValueError:
                return 0, 0, 0
    return 0, 0, 0


def safe_get_nested(dictionary, *keys, default=None):
    """Recursively get nested dictionary values safely."""
    current_value = dictionary
    for key in keys:
        if isinstance(current_value, dict):
            current_value = current_value.get(key)
        else:
            return default
    return current_value if current_value is not None else default


def safe_extract_branding(product):
    included_branding = product.get('includedBranding', {})
    if isinstance(included_branding, dict):
        return included_branding.get('name', 'Unknown Brand')
    return 'Unknown Brand'


def oasis_data():
    try:
        products = read_json('products/product/oasis_product.json')
    except Exception as e:
        print(f"Failed to read data: {str(e)}")
        return

    count = 1
    for product in products:
        count += 1
        product_id = get_id_from_oasis(product['@id'])

        exists, existing_product_data = check_product_exists(product_id)

        if exists:
            existing_price = existing_product_data['price']
            existing_quantity = existing_product_data['quantity']
            local_price = product['price']
            local_discount_price = 0
            if int(existing_price) != float(local_price):
                update_product_price(product_id, local_price, local_discount_price, existing_quantity)
        else:
            sizex, sizey, sizez = extract_sizes(product['param'])
            category_ids = product.get('categoryId', [0])
            category_id = int(category_ids[0] if isinstance(category_ids, list) else category_ids)
            data = {
                'id': product_id,
                'categoryId': category_id,
                'name': product['name'],
                'brand': safe_extract_branding(product),
                'article': product.get('vendorCode', 0),
                'description': product.get('description', 'No Content'),
                'material': extract_matherial(product['param']),
                'weight': product.get('weight', 0),
                'quantity': safe_get_nested(product, 'outlets', 'outlet', '@instock', default=0),
                'color_name': extract_color_name(product['param']),
                'image_set': [{"name": url} for url in product['picture']] if product['picture'] else [],
                'price': product['price'],
                'discount_price': product['dealerPrice'],
                'prints': product.get('param', []),
                'product_size': f"Размер: Длина {sizex} см., ширина {sizey} см., высота {sizez} см., диаметр 0 см.",
                'pack': product.get('pack', []),
                'site': 'Oasiscatalog.com',

            }
            upload_product(data)
        if count % 1000 == 0:
            time.sleep(10)
    time.sleep(5)


def main():
    start = time.time()
    process_portobello_data()
    delta = time.time() - start
    print(f"Portobello: {int(delta) // 60}:{int(delta % 60)}")

    start = time.time()
    gifts_data()
    delta = time.time() - start
    print(f"Gifts: {int(delta) // 60}:{int(delta % 60)}")

    start = time.time()
    process_xinda_data()
    delta = time.time() - start
    print(f"Xinda: {int(delta) // 60}:{int(delta % 60)}")

    start = time.time()
    process_happygifts_data()
    delta = time.time() - start
    print(f"Happy Gifts: {int(delta) // 60}:{int(delta % 60)}")

    start = time.time()
    oasis_data()
    delta = time.time() - start
    print(f"Oasis: {int(delta) // 60}:{int(delta % 60)}")


# if __name__ == "__main__":
#     main()
