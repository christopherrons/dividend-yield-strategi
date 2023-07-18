from datetime import datetime, date

from dateutil.relativedelta import relativedelta


class Utils:

    @staticmethod
    def get_date_yesterday() -> date:
        return (datetime.now() + relativedelta(days=-1)).date()

    @staticmethod
    def get_date_today_n_years_back(historical_years: int) -> date:
        return (datetime.now() + relativedelta(years=-historical_years)).date()

    @staticmethod
    def get_date_string_yesterday() -> str:
        return Utils.get_date_yesterday().__str__()

    @staticmethod
    def get_date_string_today_n_years_back(historical_years: int) -> str:
        return Utils.get_date_today_n_years_back(historical_years).__str__()
