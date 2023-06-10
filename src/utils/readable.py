from typing import Union

SIZE_UNITS = {
    0: "B",
    1: "KB",
    2: "MB",
    3: "GB",
    4: "TB",
    5: "PB",
    6: "EB",
    7: "ZB",
    8: "YB",
}

DATE_UNITS = {
    "long": {
        0: "millisecond(s)",
        1: "second(s)",
        2: "minute(s)",
        3: "hour(s)",
        4: "day(s)",
        5: "week(s)",
        6: "month(s)",
        7: "year(s)",
        8: "decade(s)",
    },
    "short": {
        0: "ms",
        1: "s",
        2: "m",
        3: "h",
        4: "days",
        5: "weeks",
        6: "months",
        7: "years",
        8: "decades",
    },
}


class HumanFormat:
    @staticmethod
    def ToBytes(size: Union[str, int]) -> str:
        """Convert Bytes To Bytes So That Human Can Read It"""
        if isinstance(size, str):
            try:
                size = int(size)
            except ValueError:
                size = None
        if not size:
            return f"0 {SIZE_UNITS[0]}"
        size = int(size)
        index, power = 0, 2**10
        while size > power:
            size /= power
            index += 1
        try:
            real_size = f"{str(round(size, 2))} {SIZE_UNITS[index]}"
        except KeyError:
            size = size * ((index - (len(SIZE_UNITS) - 1)) * (2**10))
            real_size = f"{str(round(size, 2))} {SIZE_UNITS[-1]}"
        return real_size


    @staticmethod
    def Time(milliseconds: int, milli: bool = False, units: str = None) -> str:
        # sourcery skip: low-code-quality
        """Time Formatter"""
        if not units or units.lower() not in list(DATE_UNITS):
            units = "short"
        if milliseconds == 0:
            return f"0 {DATE_UNITS[units][0]}"
        if not milli:
            milliseconds *= 1000

        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        months, weeks = divmod(weeks, 4)
        years, months = divmod(months, 12)

        result = (
            (f"{str(round(years))} {DATE_UNITS[units][7]}, " if years else "")
            + (f"{str(round(months))} {DATE_UNITS[units][6]}, " if months else "")
            + (f"{str(round(weeks))} {DATE_UNITS[units][5]}, " if weeks else "")
            + (f"{str(round(days))} {DATE_UNITS[units][4]}, " if days else "")
            + (f"{str(round(hours))} {DATE_UNITS[units][3]}, " if hours else "")
            + (f"{str(round(minutes))} {DATE_UNITS[units][2]}, " if minutes else "")
            + (f"{str(round(seconds))} {DATE_UNITS[units][1]}, " if seconds else "")
            + (
                f"{str(round(milliseconds))} {DATE_UNITS[units][0]}, "
                if milliseconds and milli
                else ""
            )
        )[:-2]
        result = result if days else result.replace(" ", "").replace(",", ":")
        return result or f"0 {DATE_UNITS[units][0]}"