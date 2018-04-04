from datetime import datetime
from collections import OrderedDict


def read_inactivity_period(inactivity_file):
    line = inactivity_file.read()
    value = int(line[0])
    return value


def process_row(row, header):
    """Convert a row from a csv into a filtered and processed
    dictionary

    Arguments:
        row {list} -- Must include fields 'date' and 'time'
        header {list} -- 1:1 matching strings with row

    Returns:
        [dict] -- Dictionary with keys: 'ip' and 'datetime'
    """
    row_dict = dict(zip(header, row))

    # Combine 'date' and 'time' into single Datetime object
    time_combined_str = row_dict["date"] + " " + row_dict["time"]
    time_combined_datetime = datetime.strptime(
        time_combined_str, "%Y-%m-%d %X")

    processed_row_dict = {
        "ip": row_dict["ip"],
        "datetime": time_combined_datetime}
    return processed_row_dict


def seconds_delta(datetime_end, datetime_start):
    """Seconds between two Datetimes

    Arguments:
        datetime_end {Datetime}
        datetime_start {Datetime}

    Returns:
        [int] -- gap between datetime_end and datetime_start
    """
    return (datetime_end - datetime_start).seconds


def post_process_row(session_dict):
    """Convert session dictionary outputed by ActiveSession
    to row ready to be written to sessionization.txt

    Arguments:
        session_dict {dict} -- Has fields: 'ip', 'first_request', 
        'last_request', and 'request_count'

    Returns:
        [list] -- in the proper order for sessionization.txt
    """
    ip = session_dict["ip"]
    first_datetime = datetime.strftime(
        session_dict["first_request"], "%Y-%m-%d %T")
    last_datetime = datetime.strftime(
        session_dict["last_request"], "%Y-%m-%d %T")
    duration = seconds_delta(
        session_dict["last_request"], session_dict["first_request"]) + 1
    count = session_dict["request_count"]

    session_list = [
        ip,
        first_datetime,
        last_datetime,
        duration,
        count
    ]
    return session_list


class ActiveSessions(OrderedDict):
    """
    Core data structure for EDGAR sessionization.

    Records the evolving set of active sessions, clearing
    inactive sessions.
    """

    def __init__(self, inactivity_period):
        """
        Keyword Arguments:
            inactivity_period {int} -- Number of seconds a session
            can remain active without requests
        """

        OrderedDict.__init__(self)
        self.inactivity_period = inactivity_period

    def __missing__(self, key):
        """
        Implements DefaultDict-like functionality to automatically return
        a new session dict object when an ip for a request is not currently
        active
        """
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

    def _update_session(self, processed_row_dict):
        """Update active session's 'count' and 'last_request'.
        If session does not exist that matches 'ip' creates a new one.

        Private method called by self.step
 
        Arguments:
            processed_row_dict {dict} -- corresponds to single row
            from input log.csv, after pre-processing by process_row function
        """

        self.current_datetime = processed_row_dict["datetime"]
        session = self[processed_row_dict["ip"]].copy()
        session["last_request"] = processed_row_dict["datetime"]
        session["request_count"] += 1
        self[processed_row_dict["ip"]] = session

    def _close_sessions(self, close_all=False):
        """
        Close inactive sessions, if close_all=True then close all
        sessions.

        Private method called by self.step and self.final_step
        """
        if close_all:
            self.closed_sessions = list(self.values())
        else:
            self.closed_sessions = []
            for _, session in self.items():
                if self._isinactive(session):
                    self.closed_sessions.append(session)

        # Clear closed sessions
        for closed_session in self.closed_sessions:
            closed_ip = closed_session["ip"]
            del self[closed_ip]

    def step(self, processed_row_dict):
        """Evolve state by one timestep: update an active sessions /
        create a new one. Close inactive sessions.

        Arguments:
            processed_row_dict {dict} -- corresponds to single row
            from input log.csv, after pre-processing by process_row function

        Returns:
            [list] -- List of session dictionaries
        """
        self._update_session(processed_row_dict)
        self._close_sessions()
        return self.closed_sessions

    def final_step(self):
        """
        Close all sessions. Called at the end of input log.csv
        """
        self._close_sessions(close_all=True)
        return self.closed_sessions
