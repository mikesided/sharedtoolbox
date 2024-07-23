# System Imports
import os
import sys

# Third-Party Imports

# Local Imports

# ______________________________________________________________________________________________________________________

class Singleton(type):
    __instances__ = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances__:
            cls.__instances__[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instances__[cls]    


class EventHandler(object, metaclass=Singleton):
    """
    Class that holds events
    
    Events can be emitted or listened to
    """

    def __init__(self):
        """Constructor
        
        Args:
            singleton (bool): Construct as a singleton? Defaults to False
        """
        self.file_clicked = Event(str) # File path
        

class Event():
    """
    A base class for an event
    
    Events can be fired or listened to
    """

    def __init__(self, *args):
        """Constructor
        
        Args:
            *args (type): Number of arguments and their types that emitting this function will send
        """
        self._listeners = []
        self._args = args


    def emit(self, *args):
        """Emits an event. Loops through listeners and calls them"""
        if not len(args) == len(self._args):
            self._raise_invalid_args(*args)
        for i, arg in enumerate(args):
            if not issubclass(type(arg), self._args[i]):
                self._raise_invalid_args(*args)

        cleanup_listeners = []
        for listener in self._listeners:
            try:
                listener(*args)
            except RuntimeError:
                cleanup_listeners.append(listener)

        if cleanup_listeners:
            self._listeners = [listener for listener in self._listeners if listener not in cleanup_listeners]
            cleanup_listeners = []


    def connect(self, func):
        """Adds a listening function to the event
        
        Args:
            func: Listening function
        """
        if func not in self._listeners:
            self._listeners.append(func)


    def disconnect(self, func):
        """Disconnects a listener from the event
        
        Args:
            func: Function to disconnect
        """
        if func in self._listeners:
            self._listeners.remove(func)
            
            
    def _raise_invalid_args(self, *args):
        """Raises an invalid arguments exception"""
        raise ValueError('Invalid event args. \nExpected: "{}" \nReceived: "{}"'
                         .format(', '.join(list([str(x) for x in self._args])), ', '.join([str(type(x)) for x in args]))
                         )

# ______________________________________________________________________________________________________________________
# __init__.py
