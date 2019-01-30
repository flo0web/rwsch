import random
from abc import abstractmethod, ABC
from datetime import timedelta, datetime
from enum import Enum
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


class ForecastLimitItem(Enum):
    PERIOD = 0
    RATING = 1


def distribute(n_items: int = 1, n_receivers: int = 1):
    """Функция distribute распределяет количество ресурсов - n_items
    между количеством получателей - n_receivers.
    В результате возвращается список длиной n_receivers, заполненый значениями ресурсов,
    которое предназначено каждому из получателей"""

    # генерируем список получателей
    receivers = [0 for _ in range(0, n_receivers)]

    while n_items > 0:
        # Каждая итерация в этом цикле определяет шансы каждого получателя на получение ресурса

        if n_items >= len(receivers):
            # Если ресурсов больше, чем получателей, то шанс = 100
            chance = 100
        else:
            # Иначе рассчитываем шанс через соотношение количества получателей и ресурсов
            chance = int(
                round(n_items / float(len(receivers)), 2) * 100
            )

        receiver_idx = 0
        while True:
            if chance == 100 or random.randint(0, 100) <= chance:
                receivers[receiver_idx] += 1
                n_items -= 1

            # Останавливаем цикл, если ресурсы исчерпаны
            if n_items == 0:
                break

            if receiver_idx < (len(receivers) - 1):
                receiver_idx += 1
            else:
                break

    return receivers


class SchedulingStrategy(ABC):
    @abstractmethod
    def get_schedule(self, items):
        """Рассчет расписания постинга для конерктного класса стратегии
        В результате должен получиться список количества постов для каждого месяца на год вперед:
        [1, 2, 2, ..., 3]
        Если в конкретном месяце не предвидится постов, то в качестве значения нужно использовать 0:
        [1, 0, 2, ..., 3]"""
        pass

    def _get_projection(self, items):
        """Рассчет проекции динамики отзывов из прошлого для конкретного класса стратегии.
        Строится на основании среднего количества отзывов в месяц и средней оценки за определенный период.
        В результате должен получиться список оценок для каждого месяца на год вперед:
        [[3.5, 3.5, 3.5], [3.5, 3.5, 3.5], ..., [3.5, 3.5, 3.5]]
        Если в конкретном месяце не предвидится постов, то в качестве значения нужно использовать пустой список:
        [[3.5, 3.5, 3.5], [], [3.5, 3.5, 3.5], ..., [3.5, 3.5, 3.5]]"""

        last_year = Period.from_delta(0, 365)

        items_last_year = list(i for i in items if last_year.satisfied(i))
        items_rating = sum([i.rating for i in items_last_year]) / float(len(items_last_year))

        items_projection = distribute(len(items_last_year), 12)

        return [[items_rating for _ in range(0, items_per_month)] for items_per_month in items_projection]

    def get_forecast(self, items, limit_item: ForecastLimitItem, limit_value):
        if limit_item == ForecastLimitItem.PERIOD:
            assert limit_value in range(1, 13), "Period limit must be in range 1, 12"
        elif limit_item == ForecastLimitItem.RATING:
            assert limit_value in range(1, 6), "Rating limit must be in range 1, 5"
        else:
            raise ValueError('Unknown limit item')

        schedule = self.get_schedule(items)
        projection = self._get_projection(items)

        # Для определения достижения оценки может понадобиться расширить расписание постинга
        # Максимальный срок для прогноза достижения оценки составляет 36 месяцев
        if limit_item == ForecastLimitItem.RATING:
            # К стандартному расписанию постинга, которое составляет 12 месяцев, добавим еще 24
            # В качестве количества постов для каждого добавленного месяца
            # возьмем среднее количество из стандартного расписания за 3 последних месяца
            schedule += [int(sum(schedule[-3:]) / 3.0) for _ in range(0, 24)]

            # Проекцию увеличим в 2 раза
            projection.extend(projection * 2)

        # Скомпонуем расписание и проекцию в один список для удобства итерирования
        future = zip(projection, schedule)

        forecast = []
        ratings = [i.rating for i in items]
        for period_num, (items_projected, items_scheduled) in enumerate(future, start=1):
            ratings += [rating for rating in items_projected]
            ratings += [5 for _ in range(0, items_scheduled)]

            rating_current_month = sum(ratings) / float(len(ratings))

            forecast.append({
                'period_number': period_num,
                'items_from_sch': items_scheduled,
                'rating_from_sch': 5 if items_scheduled > 0 else '-',
                'items_from_history': len(items_projected),
                'rating_from_history': sum(items_projected) / len(items_projected) if len(items_projected) > 0 else '-',
                'items_total': len(ratings),
                'rating_avg': rating_current_month,
            })

            if limit_item == ForecastLimitItem.PERIOD and period_num == limit_value:
                break

            elif limit_item == ForecastLimitItem.RATING and rating_current_month >= limit_value:
                break

        return forecast

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
