from datetime import datetime
from unittest import TestCase

from examples.serp import strategies
from rwsch.models import SchedulingService


class TestItem:
    def __init__(self, date, rating=0):
        self.date = date
        self.rating = rating


class StrategiesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        strategy_list = [
            strategies.HighActivity,
            strategies.MediumActivity,
            strategies.PastActivity,
            strategies.HighLowActivity,
            strategies.LowLowActivity
        ]

        service = SchedulingService(strategy_list)

        cls.service = service

    def test_high_activity_group(self):
        ratings = [3, 5, 4, 2, 1, 5, 5, 3, 5, 4, 4, 5, 4, 2, 3, 2, 5, 2, 5, 5, 4, 1, 2, 3]

        items = [
            TestItem(
                date=datetime.strptime('2018-01-01', "%Y-%m-%d").date(),
                rating=ratings[i],
            ) for i in range(0, 24)
        ]

        group = self.service.get_strategy(items)
        self.assertIsInstance(group, strategies.HighActivity)

        sch = self.service.get_schedule(items)
        self.assertEqual(sch, [1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 10, 13])

    def test_medium_activity_group(self):
        ratings = [2, 4, 1, 2, 1, 3, 4, 1, 1, 1, 5, 2]

        items = [
            TestItem(
                date=datetime.strptime('2018-01-01', "%Y-%m-%d").date(),
                rating=ratings[i],
            ) for i in range(0, 12)
        ]

        group = self.service.get_strategy(items)
        self.assertIsInstance(group, strategies.MediumActivity)

        sch = self.service.get_schedule(items)
        self.assertEqual(sch, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    def test_past_activity_group(self):
        items = [
            TestItem(datetime.strptime('2018-01-01', "%Y-%m-%d").date()) for _ in range(0, 4)
        ]

        items += [
            TestItem(datetime.strptime('2017-01-01', "%Y-%m-%d").date()) for _ in range(0, 6)
        ]

        group = self.service.get_strategy(items)
        self.assertIsInstance(group, strategies.PastActivity)

        sch = self.service.get_schedule(items)

        self.assertEqual(sch, [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])

    def test_past_activity_last_year_empty(self):
        """
        В этой стратегии возможна ситуация, когда в исследуемом году нет отзывов
        Так как на ноль делить нельзя, сделаем минимальную активность, как для одного отзыва в году
        """

        items = [
            TestItem(datetime.strptime('2017-01-01', "%Y-%m-%d").date()) for _ in range(0, 6)
        ]

        group = self.service.get_strategy(items)
        self.assertIsInstance(group, strategies.PastActivity)

        sch = group.get_schedule(items)
        self.assertIn(sum(sch), [1, 2])

    def test_hi_lo_activity_group(self):
        items = [
            TestItem(datetime.strptime('2018-01-01', "%Y-%m-%d").date()) for _ in range(0, 3)
        ]

        items += [
            TestItem(datetime.strptime('2017-01-01', "%Y-%m-%d").date()) for _ in range(0, 3)
        ]

        items += [
            TestItem(datetime.strptime('2016-01-01', "%Y-%m-%d").date()) for _ in range(0, 3)
        ]

        group = self.service.get_strategy(items)
        self.assertIsInstance(group, strategies.HighLowActivity)

        sch = self.service.get_schedule(items)
        self.assertEqual(sum(sch), 2)

    def test_lo_lo_activity_group(self):
        items = [
            TestItem(datetime.strptime('2018-01-01', "%Y-%m-%d").date()) for _ in range(0, 1)
        ]

        items += [
            TestItem(datetime.strptime('2017-01-01', "%Y-%m-%d").date()) for _ in range(0, 1)
        ]

        items += [
            TestItem(datetime.strptime('2016-01-01', "%Y-%m-%d").date()) for _ in range(0, 1)
        ]

        group = self.service.get_strategy(items)
        self.assertIsInstance(group, strategies.LowLowActivity)

        sch = self.service.get_schedule(items)
        self.assertEqual(sum(sch), 1)
