import json, os

rel_path = os.path.join('Worlds', 'Arinthia', 'relationships.json')
groups_path = os.path.join('Worlds', 'Arinthia', 'groups.json')
leaders_path = os.path.join('Worlds', 'Arinthia', 'leaders.json')

with open(leaders_path, 'r') as file:
    leaders = json.load(file)
with open(groups_path, 'r') as file:
    groups = json.load(file)
with open(rel_path, 'r') as file:
    relationships = json.load(file)

shortnames = {}

for group, data in groups.items():
    shortnames[data['short_name']] = group

for leader, data in leaders.items():
    shortnames[data['short_name']] = leader

# print(shortnames)
for name,relationship in relationships.items():
    from_ent = name.split('-')[0]
    to_ent = name.split('-')[1]
    try:
        relationship['from'] = shortnames[from_ent]
        relationship['to'] = shortnames[to_ent]
    except:
        continue

for i,k in relationships.items():
    print("{} -> {}".format(i,k))
    
with open(rel_path, 'w') as file:
    json.dump(relationships, file, indent=4)