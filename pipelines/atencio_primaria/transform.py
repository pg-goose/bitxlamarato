import argparse
import pandas as pd

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--input", required=False, default="./atencio_primaria.json")
argumentParser.add_argument("--output", required=False, default="./atencio_primaria.csv")

if __name__ == "__main__":
    args = argumentParser.parse_args()

    dataFrame = pd.read_json(args.input, lines=True)
    dataFrame.to_csv(args.output, index=False)
    
