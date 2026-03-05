import re
import json

with open("raw.txt", "r", encoding="utf-8") as file:
    text = file.read()

date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
date = date_match.group() if date_match else None

time_match = re.search(r"\d{2}:\d{2}", text)
time = time_match.group() if time_match else None

items = re.findall(r"([A-Za-zА-Яа-я\s]+)\s+(\d+)", text)

parsed_items = []
total_calculated = 0

for name, price in items:
    if "TOTAL" not in name.upper():
        parsed_items.append({
            "name": name.strip(),
            "price": int(price)
        })
        total_calculated += int(price)

payment_match = re.search(r"Payment method:\s*(\w+)", text, re.IGNORECASE)
payment_method = payment_match.group(1) if payment_match else None

total_match = re.search(r"TOTAL:\s*(\d+)", text)
total_from_receipt = int(total_match.group(1)) if total_match else total_calculated

result = {
    "date": date,
    "time": time,
    "items": parsed_items,
    "total": total_from_receipt,
    "payment_method": payment_method
}

print(json.dumps(result, indent=4, ensure_ascii=False))