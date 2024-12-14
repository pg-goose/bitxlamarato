import json
import os
import requests
import argparse
from requests import get, HTTPError

select_help ="""
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
argumentParser.add_argument("--year-start", required=True, type=int, help="Year to start fetching data")
argumentParser.add_argument("--year-end", required=True, type=int, help="Year to end fetching data")

class ParamsAtencioPrimaria:
    MIN_YEAR=2015
    MAX_YEAR=2024

    def __init__(self, select, yearStart, yearEnd, limit=50000, offset=0):
        self.valid = False
        self.select = select
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
            raise ValueError("invalid params")
        return f"?$limit={self.limit}&$offset={self.offset}&$select={self.select}&$where=any >= {self.yearStart} AND any <= {self.yearEnd}&$order=data DESC"

class ClientAtencioPrimaria():
    SOURCE_URL="https://analisi.transparenciacatalunya.cat/resource/fa7i-d8gc.json"

    def __init__(self, output, params: ParamsAtencioPrimaria):
        self.output = output
        self.params = params
        os.makedirs(os.path.dirname(self.output), exist_ok=True)

    def fetchBatch(self, limit=50000, offset=0):
        self.params.offset = offset
        self.params.limit = limit
        response = get(f"{ClientAtencioPrimaria.SOURCE_URL}{self.params.query}")
        response.raise_for_status()
        return response.json()

    def fetchAll(self):
        offset = 0
        limit = 50000

        # Check if the output path includes directories
        output_dir = os.path.dirname(self.output)
        # Create directories only if output_dir is not empty
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(self.output, "+w") as f:
            while True:
                batch = self.fetchBatch(limit, offset)
                if len(batch) == 0:
                    break
                for record in batch:
                    f.write(json.dumps(record) + "\n")  # Write each record as a new line
                offset += limit

if __name__ == "__main__":
    args = argumentParser.parse_args()
    try:
        apiParams = ParamsAtencioPrimaria("*", args.year_start, args.year_end)
    except ValueError as e:
        print(f"Invalid arguments: {e}")
        exit(1)

    client = ClientAtencioPrimaria(args.output, apiParams)
    try:
        data = client.fetchAll()
    except HTTPError as e:
        print(f"Error fetching data: {e}")
        exit(1)
    print("Data fetched successfully")