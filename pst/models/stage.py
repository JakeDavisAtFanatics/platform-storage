from dataclasses import dataclass, field
from typing import Dict, List

from pst.models.environment import Environment
from pst.services.yaml import YamlService


@dataclass
class Stage:
    name: str
    environments: List[Environment] = field(default_factory=list)

    def to_yaml(self) -> Dict:
        return {"environments": {env.name: env.to_yaml() for env in self.environments}}
