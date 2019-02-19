# stdlib
import csv
import argparse
import pathlib

# first party
import lib

parser = argparse.ArgumentParser(description="Sessionalize Edgar logs!")
parser.add_argument("log_path", type=pathlib.Path, help="Path to raw logs")
parser.add_argument(
    "inactivity_path",
    type=pathlib.Path,
    help="Length of inactivity period in seconds, specified as a single integer in a text file.",
)
parser.add_argument(
    "output_path", type=pathlib.Path, help="Path for where to save output"
)

if __name__ == "__main__":

    args = parser.parse_args()

    log_file = args.log_path.open("r")
    inactivity_file = args.inactivity_path.open("r")
    output_file = args.output_path.open("w")

    log_reader = csv.reader(log_file)
    sessionization_writer = csv.writer(output_file)

    inactivity_period = lib.read_inactivity_period(inactivity_file)
    active_sessions = lib.ActiveSessions(inactivity_period)
    header = next(log_reader)

    for row in log_reader:
        row_dict = lib.process_row(row, header)
        for session_dict in active_sessions.step(row_dict):
            session_list = lib.post_process_row(session_dict)
            sessionization_writer.writerow(session_list)

    final_sessions = active_sessions.final_step()
    for session_dict in final_sessions:
        session_list = lib.post_process_row(session_dict)
        sessionization_writer.writerow(session_list)

    log_file.close()
    inactivity_file.close()
    output_file.close()
