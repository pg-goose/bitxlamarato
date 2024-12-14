import argparse
import csv
from datetime import datetime
import os

import requests


class ClientQualitatAire():
    """ Client for the Qualitat de l'aire API """
    SOURCE_URL = "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json"
    DAY_TIMES = ['h19', 'h15', 'h18', 'h17', 'h06', 'h23', 'h05', 'h16', 'h24', 'h11', 'h12', 'h13',
                 'h20', 'h21', 'h10', 'h22', 'h09', 'h08', 'h07', 'h14', 'h04', 'h03', 'h02', 'h01']

    def __init__(self, year, output_path):
        self.params = {}
        self.year = year
        self.output_path = output_path

    def get_date_range(self):
        """
        Get the date range from today to the end of the specified year.
        Args:
            year (int): The year for which the end date is calculated.
        Returns:
            tuple: A tuple containing two strings:
                - The current date and time in the format '%Y-%m-%dT%H:%M:%S'.
                - The end date of the specified year in the format '%Y-%m-%dT%H:%M:%S'.
        """

        today = datetime.today()
        end_date = datetime(self.year, 12, 31)
        return today.strftime('%Y-%m-%dT%H:%M:%S'), end_date.strftime('%Y-%m-%dT%H:%M:%S')

    def download_and_save(self, limit=1000):
        """
        Downloads data from the source URL and saves it to the specified path.
        Args:
            path (str): The file path where the data will be saved.
            year (int): The year for which the data is to be downloaded.
            limit (int, optional): The maximum number of records to fetch per request. Defaults to 1000.
        Returns:
            None
        Raises:
            requests.exceptions.RequestException: If there is an issue with the HTTP request.
            Exception: For any other exceptions that occur during the data fetching process.
        """

        start_date, end_date = self.get_date_range()
        offset = 0
        is_first_batch = True
        while True:
            try:
                print(f"Fetching data: offset={offset}")
                url = f"{self.SOURCE_URL}?$limit={limit}&$offset={
                    offset}&$where=data>='{end_date}' AND data<='{start_date}'"
                print(f"Request URL: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                print(f"Response data length: {len(data)}")
                if not data:
                    break
                self.save(data, self.output_path, is_first_batch)
                is_first_batch = False
                offset += limit
            except Exception as e:
                print("Error fetching data:", e)
                break

    def save(self, output_data, path, is_first_batch):
        """
        Saves the data to a csv file.
        Args:
            output_data (list): The data to save.
            path (str): The path to save the data.
            is_first_batch (bool): Whether this is the first batch of data.
        Returns:
            None
        """

        if not output_data:
            raise ValueError("No data to save")

        # Extract the header from the first dictionary
        header = list(output_data[0].keys()) + self.DAY_TIMES

        with open(path, "a", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            if is_first_batch:
                writer.writeheader()
            for row in output_data:
                # Fill missing values with "NA"
                for field in header:
                    if field not in row:
                        row[field] = "NA"
                writer.writerow(row)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-y", "--year", help="Year to download till", type=int, required=True)
    arg_parser.add_argument("-o", "--output", help="Output file path", default="./qualitat_aire.csv")
    args = arg_parser.parse_args()

    try:
        client = ClientQualitatAire(args.year, args.output)
        client.download_and_save()
    except Exception as e:
        print(e)
