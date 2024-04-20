from json import load, dumps

file = open('sobir.json', encoding='ascii')
data = load(file)

print(dumps(data, indent=4, ensure_ascii=False))
