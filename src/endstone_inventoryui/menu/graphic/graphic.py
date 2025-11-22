from abc import ABC, abstractmethod

from endstone import Player


class Graphic(ABC):

    @abstractmethod
    def send(self, player: Player):
        pass

    @abstractmethod
    def send_data(self, player: Player):
        pass

    @abstractmethod
    def open(self, player: Player):
        pass

    @abstractmethod
    def remove(self, player: Player):
        pass
