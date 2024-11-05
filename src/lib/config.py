import json,importlib
from types import SimpleNamespace

def get_function(function_name="main"):
    return getattr(importlib.import_module(f"src.utils.basics"), function_name)

class Config:

    path: str
    config: SimpleNamespace

    def __init__(self, path: str = "./config.json"):
        # Read config.json file.
        with open("./config.json", "r") as file:
            upd = file.read()
            self.config = json.loads(upd, object_hook=lambda d: SimpleNamespace(**d))
        self.path = path
        self.read_config()

    def __getattr__(self, name):
        return getattr(self.config, name)
    
    def read_config(self):
        # Read config.json file.
        with open(self.path, "r") as file:
            upd = file.read()
            self.config = json.loads(
                upd, object_hook=lambda d: SimpleNamespace(**d))
        return self.config
    
    def save_config(self):
        # Convert the SimpleNamespace object back to a dictionary.
        upd = self._to_dict(self.config)
        with open(self.path, "w") as file:
            file.write(upd)
        # update self.config
        self.read_config()
        return self.config

    def _to_dict(self, obj: SimpleNamespace):
        return json.dumps(obj, default=lambda o: o.__dict__)

config = None

try: config = Config()
except Exception as e: get_function("terminal")("e", e, exitScript=True)