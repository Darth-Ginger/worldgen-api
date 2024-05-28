import os, json


def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)
    
leaders = load_json('leaders.json')
leaders = leaders['leaders']

names = [name["name"] for name in leaders]

names_shortened = {name: name.split()[0][0] + name.split()[1][0] for name in names}


relationships = []

for leader in leaders:
    for relation in leader['relationships']:
        name = names_shortened[leader['name']] + '-' + names_shortened[relation]
        relationships.append(name)
        
# print(relationships)


relationships_dict = {}

for leader in leaders:
    for relation, data in leader['relationships'].items():
        name = names_shortened[leader['name']] + '-' + names_shortened[relation]
        relationships_dict[name] = data


for leader in leaders:
    leader['short_name'] = names_shortened[leader['name']]

    leader['relationships'] = [name for name in relationships if name.startswith(leader['short_name'])]

with open('leaders.json', 'w') as file:
    json.dump({"leaders": leaders}, file)

for i in leaders:
    print(i)

