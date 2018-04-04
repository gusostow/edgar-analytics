from datetime import datetime
from collections import OrderedDict


def read_inactivity_period(inactivity_file):
    line = inactivity_file.read()
    value = int(line[0])
    return value


def process_row(row, header):
    row_dict = dict(zip(header, row))
    time_combined_str = row_dict["date"] + " " + row_dict["time"]
    time_combined_datetime = datetime.strptime(
        time_combined_str, "%Y-%m-%d %X")

    keep_cols = [
        "ip",
    ]
    filtered_row_dict = {key: val for key,
                         val in row_dict.items() if key in keep_cols}
    filtered_row_dict["datetime"] = time_combined_datetime
    return filtered_row_dict


def to_list_of_dicts(input_dict):
    output_list = []
    for key, val_dict in input_dict.items():
        val_dict["ip"] = key
        output_list.append(val_dict)
    return output_list


def seconds_delta(datetime_end, datetime_start):
    return (datetime_end - datetime_start).seconds


def post_process_row(session_dict):
    ip = session_dict["ip"]
    first_datetime = datetime.strftime(
        session_dict["first_request"], "%Y-%m-%d %T")
    last_datetime = datetime.strftime(
        session_dict["last_request"], "%Y-%m-%d %T")
    duration = seconds_delta(
        session_dict["last_request"], session_dict["first_request"]) + 1
    count = session_dict["request_count"]

    output_list = [
        ip,
        first_datetime,
        last_datetime,
        duration,
        count
    ]
    return output_list


class ActiveSessions(OrderedDict):

    def __init__(self, inactivity_period=2):
        OrderedDict.__init__(self)
        self.inactivity_period = inactivity_period

    def __missing__(self, key):
        return {
            "first_request": self.current_datetime,
            "last_request": self.current_datetime,
            "request_count": 0,
            "ip": key
        }

    def _isinactive(self, session):
        seconds_old = seconds_delta(
            self.current_datetime, session["last_request"])
        return seconds_old > self.inactivity_period

    def _close_sessions(self, close_all=False):

        if close_all:
            self.closed_sessions = list(self.values())
        else:
            self.closed_sessions = []
            for _, session in self.items():
                if self._isinactive(session):
                    self.closed_sessions.append(session)
        # Clear closed sessions
        # import ipdb; ipdb.set_trace()
        for closed_session in self.closed_sessions:
            closed_ip = closed_session["ip"]
            self.pop(closed_ip)

    def _update_session(self, request_row):
        self.current_datetime = request_row["datetime"]
        session = self[request_row["ip"]].copy()
        session["last_request"] = request_row["datetime"]
        session["request_count"] += 1
        self[request_row["ip"]] = session

    def step(self, request_row):
        self._update_session(request_row)
        self._close_sessions()

        return self.closed_sessions

    def final_step(self):
        self._close_sessions(close_all=True)
        return self.closed_sessions
