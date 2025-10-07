import orjson
import os
import tempfile


def deduplicate_by_value(path: str, key: str):
    seen_values = set()

    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name)
    os.close(fd)

    with open(path, 'r', encoding='utf-8') as infile, \
         open(tmp_path, 'w', encoding='utf-8') as outfile:

        for line in infile:
            json_data = orjson.loads(line)
            value = json_data[key]

            if value not in seen_values:
                seen_values.add(value)
                outfile.write(orjson.dumps(json_data).decode("utf-8"))
                outfile.write("\n")

    os.replace(tmp_path, path)


def filter_null_data(path):
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name)
    os.close(fd)

    with open(path, 'r', encoding='utf-8') as infile, \
         open(tmp_path, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            try:
                json_data = orjson.loads(line)
            except orjson.JSONDecodeError:
                continue

            if json_data.get("content") is not None:
                outfile.write(orjson.dumps(json_data).decode("utf-8") + "\n")

    os.replace(tmp_path, path)