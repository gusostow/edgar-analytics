# Edgar-Analytics main Readme

## Requirements

- Python (written and tested in 3.6.3)

## Files:

- `dev_utils` - Utilites for preparing data for testing. Not a requirement at runtime.
- `lib.py` - Definition for `ActiveSessions` class and other helper functions.
- `sessionization.py` - Script that streams rows from `log.csv`, evolves the state of an `ActiveSessions` instance, and finally writes post-processed rows to `sessionization.txt`.

## Core data structure
The `ActiveSessions` class is the heart of my solution. It is an `OrderedDict` with `DefaultDict`-like functionality. 

Motivation: 

- I chose a hash-based data structure its constant time lookups, which if poor, would bottleneck my serial streaming approach. 

- `OrderedDict` features is necessary to meet the order condition in the problem requirements for sessions closed simultaneously. Despite imposing an additional memory cost compared to a standard `dict` or an array, I weighed lookup and order preservation much higher than memory constraints for the tasks at hand. It would take a lot of active sessions to cause memory issues.

- I chose to overload the `__missing_` method for `ActiveSessions` just as a coding convenience. `DefaultDict`-like objects are great for conditional "insert" or "mutate" operations.