import sys
import csv
import lib

log_path = sys.argv[1]
inactivity_path = sys.argv[2]
sessionization_path = sys.argv[3]

log_file = open(log_path, "r")
inactivity_file = open(inactivity_path, "r")
sessionization_file = open(sessionization_path, "w")

log_reader = csv.reader(log_file)
sessionization_writer = csv.writer(sessionization_file)

inactivity_period = lib.read_inactivity_period(inactivity_file)
active_sessions = lib.ActiveSessions(inactivity_period=inactivity_period)
header = next(log_reader)

for row in log_reader:
    row_dict = lib.process_row(row, header)
    for session_dict in active_sessions.step(row_dict):
        session_list = lib.post_process_row(session_dict)
        sessionization_writer.writerow(session_list)

final_sessions = active_sessions.close_all_sessions()
for session_dict in final_sessions:
    session_list = lib.post_process_row(session_dict)
    sessionization_writer.writerow(session_list)

log_file.close()
inactivity_file.close()
sessionization_file.close()
