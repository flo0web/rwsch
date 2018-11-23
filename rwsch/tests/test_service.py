from datetime import datetime
from unittest import TestCase

from rwsch.models import ActivityGroup, ScheduleService


class TestItem:
    def __init__(self, date, rating=0):
        self.date = date
        self.rating = rating


class TestStrategy(ActivityGroup):
    def get_schedule(self, items):
        return []

    @classmethod
    def satisfies(cls, items):
        return True


class ServiceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        ratings = [3, 5, 4, 2, 1, 5, 5, 3, 5, 4, 4, 5, 4, 2, 3, 2, 5, 2, 5, 5, 4, 1, 2, 3]

        items = [
            TestItem(
                date=datetime.strptime('2018-01-01', "%Y-%m-%d").date(),
                rating=ratings[i],
            ) for i in range(0, 24)
        ]

        cls.items = items

    def test_activity_group_determination(self):
        strategies_list = [TestStrategy]
        service = ScheduleService(strategies_list)

        strategy = service.get_activity_group(self.items)

        self.assertIsInstance(strategy, TestStrategy)
