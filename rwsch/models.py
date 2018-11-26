from abc import abstractmethod, ABC
from datetime import timedelta, datetime
from typing import Type, List


class Period:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def satisfied(self, item) -> bool:
        assert hasattr(item, 'date')

        return self.start > item.date > self.end

    @classmethod
    def from_delta(cls, start=0, end=0):
        assert start < end, 'Дельта окончания должна быть больше дельты начала'

        return cls(
            start=(datetime.now() - timedelta(days=start)).date(),
            end=(datetime.now() - timedelta(days=end)).date()
        )


class SchedulingStrategy(ABC):
    @abstractmethod
    def get_schedule(self, items):
        pass

    @classmethod
    @abstractmethod
    def satisfies(cls, items) -> bool:
        pass


class SchedulingService:
    def __init__(self, strategy_list: List[Type[SchedulingStrategy]]):
        self._strategy_list = strategy_list

    def get_strategy(self, items):
        strategy = None
        for strategy_cls in self._strategy_list:
            if strategy_cls.satisfies(items):
                strategy = strategy_cls()
                break

        if strategy is not None:
            return strategy
