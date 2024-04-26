from json import load, dumps

open("mydata-new.json", "wb").write(bin(open("tests/data.json").read()))

