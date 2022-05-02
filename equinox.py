from datetime import date, timedelta
from astral.sun import sun
from astral import moon
import json
from os.path import realpath, join, dirname
from pymeeus import base
import os
import astral
import argparse
import sys
import pytz

default_location = {
    "place": astral.LocationInfo('Brno', 'Europe', 'Europe/Brno', 49.19, 16.60),
    "tz": pytz.timezone('Europe/Prague')
}

week_days_en = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

__location__ = realpath(join(os.getcwd(), dirname(__file__)))
moon_phase_names = json.load(
    open(join(
        __location__,
        'moon-phase-names.json'), encoding='utf8'))  # pylint:disable=consider-using-with
moon_phase_symbols = ('🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘')

# capitalized header values for day, phase, symbol, name and title
header = json.load(
    open(
        join(__location__, 'headers.json'), encoding='utf8'))  # pylint:disable=consider-using-with


class CliCommand:

    def __init__(self):

        main_parser = argparse.ArgumentParser(
            description="Equinox calendar, welcome ...",
            add_help=True
        )
        main_parser.add_argument(
            "command",
            help="command to execute",
        )
        date_parser = argparse.ArgumentParser(
            description="a date in format DD MM YYYY",
            add_help=False,
            parents=[main_parser]
        )
        date_parser.add_argument(
            "day",
            help="a valid day of month in format DD",
            type=int,
            nargs="?"
        )
        date_parser.add_argument(
            "month",
            help="a valid month in format MM",
            type=int,
            nargs="?"
        )
        date_parser.add_argument(
            "year",
            help="a year in format YYYY",
            type=int,
            nargs="?"
        )

        try:
            self.args = date_parser.parse_args()
            self._date_parser = date_parser
        except SystemExit as err:
            print("error during command line arguments parsing")
            print("error message: {}".format(err))
            date_parser.print_help()
            sys.exit(err)

    def get_name(self):
        '''gets the name of a command, supported are 'date' and 'diary' '''
        return self.args.command

    def get_date(self):
        return date(
            day=self.args.day if self.args.day else date.today().day,
            month=self.args.month if self.args.month else date.today().month,
            year=self.args.year if self.args.year else date.today().year,
        )

    def printDateHelp(self):
        self._date_parser.print_help()


class Day:

    def __init__(self, day, location):
        self.day = day

        loc = location["place"]
        self.sun = sun(loc.observer, date=day, tzinfo=location["tz"])

        self.moon_phase = moon.phase(day)

    def moon_phase_code_to_name(self, code, lang='en'):
        '''Converts moon phase code to name.'''
        return moon_phase_names[lang][code]

    def moon_phase_code_to_symbol(self, code):
        '''Converts moon phase code to symbol.'''
        return moon_phase_symbols[code]

    def moon_phase_to_inacurate_code(self, phase):
        '''Converts moon phase code to inacurate code.'''
        phase = int(phase)
        value = None
        if phase == 0:
            value = 0
        elif 0 < phase < 7:
            value = 1
        elif phase == 7:
            value = 2
        elif 7 < phase < 14:
            value = 3
        elif phase == 14:
            value = 4
        elif 14 < phase < 21:
            value = 5
        elif phase == 21:
            value = 6
        else:
            value = 7
        return value

    def day_to_moon_phase_and_accurate_code(self, day):
        '''Converts day to moon phase and accurate code.'''
        phase_today = moon.phase(day)
        code_today = self.moon_phase_to_inacurate_code(phase_today)

        if code_today % 2 != 0:
            return phase_today, code_today

        phase_yesterday = moon.phase(day - timedelta(days=1))
        code_yesterday = self.moon_phase_to_inacurate_code(phase_yesterday)

        if code_today == code_yesterday:
            return phase_today, code_today + 1

        return phase_today, code_today

    def printSun(self):
        print((
            f'Sunrise and sunset:\n'
            f'Dawn:    {self.sun["dawn"]}\n'
            f'Sunrise: {self.sun["sunrise"]}\n'
            f'Noon:    {self.sun["noon"]}\n'
            f'Sunset:  {self.sun["sunset"]}\n'
            f'Dusk:    {self.sun["dusk"]}\n'
        ))

    def printWeekDay(self):

        print("Date: {}, {}\n".format(
            week_days_en[self.day.weekday()],
            self.day
        ))

    def printDayDuration(self):

        day_duration = self.sun["sunset"] - self.sun["sunrise"]
        sunset_duration = self.sun["dusk"] - self.sun["sunset"]
        sunrise_duration = self.sun["sunrise"] - self.sun["dawn"]
        print("Day light duration: {}".format(day_duration))
        print("Sunrise complete in: {}".format(sunrise_duration))
        print("Sunset complete in: {}\n".format(sunset_duration))

    def printMoon(self):

        inaccurate_code = self.moon_phase_to_inacurate_code(moon.phase(self.day))
        print("Moon phase: {} {}\n".format(
            self.moon_phase_code_to_name(inaccurate_code),
            self.moon_phase_code_to_symbol(inaccurate_code))
        )

    def printSeason(self):
        pass


def main():
    cli = CliCommand()

    if cli.get_name() == "date":
        day = Day(cli.get_date(), default_location)
        day.printWeekDay()
        day.printSun()
        day.printDayDuration()
        day.printMoon()
        day.printSeason()

    else:
        print("command {} unrecognized".format(cli.get_name()))


if __name__ == '__main__':
    sys.exit(main())
