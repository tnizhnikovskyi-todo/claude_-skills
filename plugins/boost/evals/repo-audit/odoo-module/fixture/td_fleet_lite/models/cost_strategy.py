class AbstractCostStrategy:
    """Базовая стратегия расчёта стоимости визита. Подклассы переопределяют compute()."""

    def compute(self, service):
        raise NotImplementedError


class DefaultCostStrategy(AbstractCostStrategy):
    def compute(self, service):
        return service.labor_hours * service.hourly_rate + service.parts_cost


def get_cost_strategy(name='default'):
    strategies = {'default': DefaultCostStrategy}
    return strategies[name]()
