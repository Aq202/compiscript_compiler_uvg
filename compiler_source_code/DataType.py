from abc import ABC, abstractmethod

class DataType(ABC):
    
    @abstractmethod
    def getType(self):
        pass
    
    @abstractmethod
    def equalsType(self, __class__):
        pass
    
    @abstractmethod
    def strictEqualsType(self, __class__):
        pass