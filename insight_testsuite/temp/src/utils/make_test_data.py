import csv

"""
Lightweight command line utility to trim large CSVs into a more managable size
"""

# TODO: Use better path parsing
RAW_DATA_PATH = "/Users/augustusostow/python/edgar-analytics/input/raw_data/log20170320.csv"

OUTPUT_PATH = "/Users/augustusostow/python/edgar-analytics/input/sample_data_0.csv"

OUTPUT_ROW_COUNT = 100000

input_file = open(RAW_DATA_PATH, "r")
output_file = open(OUTPUT_PATH, "w")

reader = csv.reader(input_file)
writer = csv.writer(output_file)
for _ in range(OUTPUT_ROW_COUNT):
    row = next(reader)
    writer.writerow(row)

input_file.close()
output_file.close()
