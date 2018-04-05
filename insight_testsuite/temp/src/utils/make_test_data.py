import csv
import argparse


"""
Lightweight command line utility to trim large CSVs into a more managable size
"""

parser = argparse.ArgumentParser(description="Trim a large CSV.")
parser.add_argument("input_path", type=str, help="Path to the large CSV")
parser.add_argument("output_path", type=str, help="Destination for the smaller CSV")
parser.add_argument("n_rows", type=int, default=1e6)
args = parser.parse_args()

input_file = open(args.input_path, "r")
output_file = open(args.output_path, "w")
reader = csv.reader(input_file)
writer = csv.writer(output_file)

for _ in range(args.n_rows):
    try:
        row = next(reader)
        writer.writerow(row)
    except StopIteration:
        print("n_rows inputted greater than length of 'large' CSV!")
        break

input_file.close()
output_file.close()
