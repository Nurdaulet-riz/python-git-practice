import json
with open("sample-data.json", "r") as file:
    data = json.load(file)
print("Interface Status")
print("=" * 80)
print(f"{'DN':50} {'description':30} {'Speed':10} {'MTU':6}")
print("-" * 80)

for item in data["imdata"]:
    attributes = item["l1PhysIf"]["attributes"]
    
    dn = attributes["dn"]
    description = attributes["Description"]
    speed = attributes["speed"]
    mtu = attributes["mtu"]
    
    print(f"{dn:50} {description:30} {speed:10} {mtu:6}")