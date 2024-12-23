from dataclasses import dataclass


@dataclass
class DatabaseUser:
    username_parameter_store_path: str
    password_parameter_store_path: str
    username: str = None

    def update_username(self, username: str):
        self.username = username

    def to_yaml(self):
        return {
            # "username": self.username, # Not including here as "username" is already the key for these values in DatabaseInstance.to_yaml()
            "username_parameter_store_path": self.username_parameter_store_path,
            "password_parameter_store_path": self.password_parameter_store_path,
        }
