import argparse
import sys
from requests import get, HTTPError
from django.core.management.base import BaseCommand
from myapp.models import AtencioPrimaria

select_help = """
Columns to select from the dataset, options are:
    *,
    data,
    setmana_epidemiologica,
    any,
    codi_regio,
    nom_regio,
    codi_ambit,
    nom_ambit,
    codi_abs,
    nom_abs,
    diagnostic,
    sexe,
    grup_edat,
    index_socioeconomic,
    casos,
    poblacio
"""

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--output", required=False, default="./atencio_primaria.json")
argumentParser.add_argument("--select", required=False, default="*", help=select_help)
argumentParser.add_argument("--region", required=True, type=int, help="Region code to filter data")
argumentParser.add_argument("--year-start", required=True, type=int, help="Year to start fetching data")
argumentParser.add_argument("--year-end", required=True, type=int, help="Year to end fetching data")

class ParamsAtencioPrimaria:
    MIN_YEAR = 2015
    MAX_YEAR = 2024

    def __init__(self, select, region, yearStart, yearEnd, limit=50000, offset=0):
        self.valid = False
        self.select = select
        self.region = region
        self.yearStart = yearStart
        self.yearEnd = yearEnd
        self.limit = limit
        self.offset = offset
        self.validate()

    def validate(self):
        if self.yearStart < self.MIN_YEAR or self.yearEnd > self.MAX_YEAR:
            raise ValueError(f"Year must be between {self.MIN_YEAR} and {self.MAX_YEAR}")
        if self.yearStart > self.yearEnd:
            raise ValueError("Year start must be less than year end")
        self.valid = True

    @property
    def query(self):
        if not self.valid:
            raise ValueError("Invalid parameters")
        return f"?$limit={self.limit}&$offset={self.offset}&$select={self.select}&codi_regio={self.region}&$where=any >= {self.yearStart} AND any <= {self.yearEnd}&$order=data DESC"

class ClientAtencioPrimaria:
    SOURCE_URL = "https://analisi.transparenciacatalunya.cat/resource/fa7i-d8gc.json"

    def __init__(self, params: ParamsAtencioPrimaria):
        self.params = params

    def fetchBatch(self, limit=50000, offset=0):
        self.params.offset = offset
        self.params.limit = limit
        response = get(f"{ClientAtencioPrimaria.SOURCE_URL}{self.params.query}", timeout=10)
        response.raise_for_status()
        print(f"Fetching data batch: offset={offset}, limit={limit}")
        return response.json()

    def fetchAll(self):
        offset = 0
        limit = 50000

        while True:
            batch = self.fetchBatch(limit, offset)
            if len(batch) == 0:
                print("No more data to fetch, exiting loop")
                break
            for record in batch:
                AtencioPrimaria.objects.create(**record)
            offset += limit
        print("Data fetching and writing complete")

class Command(BaseCommand):
    help = 'Seed the database with AtencioPrimaria data'

    def add_arguments(self, parser):
        parser.add_argument("--output", required=False, default="./atencio_primaria.json")
        parser.add_argument("--select", required=False, default="*", help=select_help)
        parser.add_argument("--region", required=True, type=int, help="Region code to filter data")
        parser.add_argument("--year-start", required=True, type=int, help="Year to start fetching data")
        parser.add_argument("--year-end", required=True, type=int, help="Year to end fetching data")

    def handle(self, *args, **options):
        try:
            apiParams = ParamsAtencioPrimaria(options['select'], options['region'], options['year_start'], options['year_end'])
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Invalid arguments: {e}"))
            return

        client = ClientAtencioPrimaria(apiParams)
        try:
            self.stdout.write("Starting to fetch data...")
            client.fetchAll()
        except HTTPError as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data: {e}"))
            return
        self.stdout.write(self.style.SUCCESS("Data fetched successfully"))

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)