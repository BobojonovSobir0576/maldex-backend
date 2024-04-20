from json import load, dumps
from apps.product.models import ProductCategories
import requests

file = open('tests/maldex_category.json', encoding='utf-8')
data = load(file)

for category in data:
    pc = ProductCategories.objects.get(id=category['id'])
    icon = category['icon']

    if icon:
        get_image = requests.get('https://maldex-gifts.ru/' + category['icon'])
        file = open('media/icon/' + category['slug'] + '.svg', 'wb')
        file.write(get_image.content)
        file.close()
        pc.icon = 'icon/' + category['slug'] + '.svg'
        pc.save()




