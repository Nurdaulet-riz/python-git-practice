import json

# Open the JSON file and load data
with open('sample-data.json') as file:
    data = json.load(file)

print("Interface Status")
print("=" * 80)
# Print the header with specific formatting
print(f"{'DN':<50} {'Description':<20} {'Speed':<8} {'MTU':<6}")
print("-" * 80)

# Loop through the network interfaces
for item in data['imdata']:
    # Get the attributes dictionary
    attributes = item['l1PhysIf']['attributes']
    
    dn = attributes['dn']
    descr = attributes.get('descr', '') # Use .get() to avoid errors if empty
    speed = attributes.get('speed', 'inherit')
    mtu = attributes['mtu']
    
    # Print the row with formatting
    print(f"{dn:<50} {descr:<20} {speed:<8} {mtu:<6}")