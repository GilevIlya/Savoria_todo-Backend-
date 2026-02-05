from datetime import datetime

from sqlalchemy.types import Date, TypeDecorator


class DDMMYYYY(TypeDecorator):
    impl = Date
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            return datetime.strptime(value, "%d/%m/%Y").date()

        raise ValueError("Invalid date format, expected dd/mm/yyyy")

    def process_result_value(self, value, dialect):
        return value.strftime("%d/%m/%Y")
