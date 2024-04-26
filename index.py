from json import load, dumps

file = open('tests/images.json', 'r', encoding='utf-8')
n = 5000

data = load(file)

for i in range(0, len(data), n):
    new_file = open(f'tests/image{i // n}.json', 'w')
    new_file.write(dumps(data[i], ensure_ascii=False))
    new_file.close()
