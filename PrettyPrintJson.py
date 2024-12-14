import json

f = open('lotto_america_winning_nums.json.old', 'r')
data = json.load(f)
print(json.dumps(data, indent=4))
