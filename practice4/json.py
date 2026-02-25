import json

FILENAME = "sample-data.json"

with open(FILENAME, "r", encoding="utf-8") as f:
    data = json.load(f)

imdata = data.get("imdata", [])

print("Interface Status")
print("=" * 75)
print(f"{'DN':55} {'Speed':8} {'MTU':6}")
print("-" * 75)

for item in imdata:
    if not isinstance(item, dict) or len(item) == 0:
        continue

    obj_name = next(iter(item))
    obj = item.get(obj_name, {})

    attrs = obj.get("attributes", {})

    dn = attrs.get("dn", "")
    speed = attrs.get("speed", "")
    mtu = attrs.get("mtu", "")

    print(f"{dn:55} {speed:8} {mtu:6}")