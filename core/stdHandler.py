# System Imports
import os
import sys

# Third-Party Imports

# Local Imports

# ______________________________________________________________________________________________________________________


class StdOutHandler(object):
    """
    Overrides the system stdout and stderr.
    Submits an eventhandler signal with the written std messages, to be pickedup by a console widget
    """

    def __init__(self, event_handler, *args, **kwargs):
        self.event_handler = event_handler
        self.stdout = sys.stdout
        sys.stdout = self

    def write(self, message):
        self.stdout.write(message)
        self.event_handler.std_out_write.emit(message)

    def flush(self):
        NotImplemented


class StdErrHandler(object):
    """
    Overrides the system stdout and stderr.
    Submits an eventhandler signal with the written std messages, to be pickedup by a console widget
    """

    def __init__(self, event_handler, *args, **kwargs):
        self.event_handler = event_handler
        self.stderr = sys.stderr
        sys.stderr = self

    def write(self, message):
        self.stderr.write(message)
        self.event_handler.std_err_write.emit(message)
        
    def flush(self):
        NotImplemented


# ______________________________________________________________________________________________________________________
