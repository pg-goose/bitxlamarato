import argparse
import csv
import requests


class QualitatAire():
    MIN_YEAR = 1991
    MAX_YEAR = 2024


class ClientQualitatAire():
    """ Client for the Qualitat de l'aire API """
    SOURCE_URL = "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json"
    DAY_TIMES = ['h19', 'h15', 'h18', 'h17', 'h06', 'h23', 'h05', 'h16', 'h24', 'h11', 'h12', 'h13', 'h20', 'h21', 'h10', 'h22', 'h09', 'h08', 'h07', 'h14', 'h04', 'h03', 'h02', 'h01', 'h00']

    def __init__(self):
        self.params = {}

    
    def download_and_save(self, path, limit=1000):
        """
        Downloads data from the source URL in batches and saves it to the specified path.
        Args:
            path (str): The file path where the data should be saved.
            limit (int, optional): The maximum number of records to fetch per batch. Defaults to 1000.
        Raises:
            requests.exceptions.RequestException: If there is an issue with the HTTP request.
            Exception: For any other exceptions that occur during the data fetching process.
        """

        offset = 0
        is_first_batch = True
        while True:
            try:
                print(f"Fetching data: offset={offset}")
                response = requests.get(f"{self.SOURCE_URL}?$limit={limit}&$offset={offset}", timeout=10)
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                self.save(data, path, is_first_batch)
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
    arg_parser.add_argument("-y", "--year", help="Year to download", type=int, default=None)
    args = arg_parser.parse_args()

    try:
        client = ClientQualitatAire()
        client.download_and_save("./qualitat_aire.csv")
    except Exception as e:
        print(e)