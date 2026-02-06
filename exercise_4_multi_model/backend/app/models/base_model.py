from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": self.__class__.__name__,
            "model": self.model_name
        }
