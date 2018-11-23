from random import randint

from rwsch.models import SchedulingStrategy, Period


class HighActivity(SchedulingStrategy):
    """Группа высокой активности"""

    def get_schedule(self, items):
        """
        Первый 2 месяца ср негатив в мес за год + 0.3 * ср позитив в мес за год
        Дальше увеличивается на 30% ежемесячно
        """

        period = Period.from_delta(0, 365)

        pos_items = list(i for i in items if (period.satisfied(i) and i.rating > 3))
        neg_items = list(i for i in items if (period.satisfied(i) and i.rating < 4))

        avg_pos = len(pos_items) / 12
        avg_neg = len(neg_items) / 12

        schedule = []
        for m in range(0, 12):
            if m <= 2:
                limit = avg_neg + (0.3 * avg_pos)
            else:
                limit = schedule[-1] * 1.3

            schedule.append(limit)

        return [round(l) for l in schedule]

    @classmethod
    def satisfies(cls, items):
        """
        Количество отзывов больше 2 в месяц (30 дней) за последний год
        Минимум 24 отзыва за последний год
        """
        period = Period.from_delta(0, 365)

        items = list(i for i in items if period.satisfied(i))

        avg = len(items) / 12

        return avg >= 2


class MediumActivity(SchedulingStrategy):
    """Группа средней активности"""

    def get_schedule(self, items):
        """
        Первый месяц ср негатив в мес за год + 0.3 * ср позитив в мес за год
        Дальше увеличивается на 1 отзыв в месяц
        """

        period = Period.from_delta(0, 365)

        pos_items = list(i for i in items if (period.satisfied(i) and i.rating > 3))
        neg_items = list(i for i in items if (period.satisfied(i) and i.rating < 4))

        avg_pos = len(pos_items) / 12
        avg_neg = len(neg_items) / 12

        schedule = []
        for m in range(0, 12):
            if m == 0:
                limit = avg_neg + (0.3 * avg_pos)
            else:
                limit = schedule[-1] + 1

            schedule.append(limit)

        return [round(l) for l in schedule]

    @classmethod
    def satisfies(cls, items):
        """
        Количество отзывов больше 1 в 60 дней за последний год
        Минимум 6 отзывов за последний год
        """

        period = Period.from_delta(0, 365)

        items = list(i for i in items if period.satisfied(i))

        avg = len(items) / 6

        return avg >= 1


class PastActivity(SchedulingStrategy):
    """Группа с активностью не в текущем году"""

    def get_schedule(self, items):
        return []

    @classmethod
    def satisfies(cls, items):
        """
        Количество отзывов больше 3 в год (365) за последниие 3 года (1095 дней)
        """

        periods = [
            Period.from_delta(365, 2 * 365),
            Period.from_delta(2 * 365, 3 * 365),
        ]

        for period in periods:
            period_items = [i for i in items if period.satisfied(i)]

            avg = len(period_items) / 6

            if avg >= 1:
                return True

        return False


class HighLowActivity(SchedulingStrategy):
    """Группа с низкой активностью 3-6 отзывов в год"""

    def get_schedule(self, items):
        """
        2 отзыва в год, в первом и во втором полугодии случайным образом
        """

        schedule = [0 for _ in range(0, 12)]

        rnd_month = randint(0, 5)
        schedule[rnd_month] = 1

        rnd_month = randint(6, 11)
        schedule[rnd_month] = 1

        return schedule

    @classmethod
    def satisfies(cls, items):
        """
        Количество отзывов больше 3 в год (365) за последниие 3 года (1095 дней)
        Минимум 9 отзывов за последние три года
        """

        period = Period.from_delta(0, 3 * 365)

        items = list(i for i in items if period.satisfied(i))

        avg = len(items) / 3

        return avg >= 3


class LowLowActivity(SchedulingStrategy):
    """Группа с низкой активностью 1-2 отзыва в год"""

    def get_schedule(self, items):
        """
        1 отзыв в год, в первом и во втором полугодии случайным образом
        """

        schedule = [0 for _ in range(0, 12)]

        rnd_month = randint(0, 11)
        schedule[rnd_month] = 1

        return schedule

    @classmethod
    def satisfies(cls, items):
        """
        Количество отзывов больше 1 в год (365) за последниие 3 года (1095 дней)
        Минимум 3 отзыва за последние три года
        """

        period = Period.from_delta(0, 3 * 365)

        items = list(i for i in items if period.satisfied(i))

        avg = len(items) / 3

        return avg >= 1
