import json


def deduplicate_by_value(
    path: str,
    key: str = None
):
    seen_values = set()
    unique_data = []

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            json_data = json.loads(line.strip())
            value = json_data[key]
            
            if value not in seen_values:
                unique_data.append(json_data)
                seen_values.add(value)

    with open(path, 'w', encoding='utf-8') as file:
        for data in unique_data:
            json.dump(data, file, ensure_ascii=False)
            file.write('\n')


if __name__ == "__main__":
    deduplicate_by_value(r"G:\Musubi\crawler\test_link.json", "link")