from json import load, dumps

file = open('tests/sobir.json', encoding='utf-8')
data = load(file)

categories_data = []

for category in data:
    category_data = {
        'id': category['folder_uid_id'],
        'slug': category['folder_chr_link'],
        'parent_id': category['folder_ref_parent'] if category['folder_ref_parent'] else None,
        'name': category['folder_chr_name'],
        'icon': category['folder_img_icon'],
        'desc': category['folder_txt_descr'],
        'title': category['folder_chr_title'],
        'created': category['folder_smp_create'],
        'updated': category['folder_smp_update'],
    }
    categories_data.append(category_data)

file = open('tests/maldex_category.json', 'w', encoding='utf-8')
file.write(dumps(categories_data, indent=4, ensure_ascii=False))
