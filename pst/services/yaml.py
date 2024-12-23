from typing import Dict, List

import yaml


class YamlService:
    def __init__(self, file: str):
        self.file = file

    def read_file(self) -> Dict:
        with open(self.file, "r") as file:
            return yaml.safe_load(file)

    def write_file(self, data: Dict):
        with open(self.file, "w") as file:
            yaml.dump(data, file, default_flow_style=False)

    def get_keys(self, *names: str) -> List[str]:
        current = self.read_file()
        for name in names:
            current = current[name]
        return [k for k in current.keys()]

    def get_value(self, *keys: str) -> Dict:
        value = self.read_file()
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                print(f"No value found for keys: {' -> '.join(keys)}")
                return None
        return value
