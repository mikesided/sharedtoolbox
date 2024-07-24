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
        self.file_clicked = Event(str) # File path. Triggered from the navigation
        self.file_opened = Event(str) # File path. Triggered from the FilesWidget. This is the current editor displayed
        self.file_state_changed = Event(bool) # True: Saved. False: Unsaved.  Only the current file emits this signal.
        self.file_saved = Event(str) # File path.
        self.move_filebtn_left = Event()  # Triggered from the EditorControls.
        self.move_filebtn_right = Event()  # Triggered from the EditorControls.
        self.select_previous_filebtn = Event()  # Triggered from the EditorControls.
        self.select_next_filebtn = Event()  # Triggered from the EditorControls.
        self.theme_changed = Event(str) # Theme.
        self.font_changed = Event(str) # Font.
        
        # Keyboard shortcuts
        self.shortcut_save = Event()
        self.shortcut_move_filebtn_left = Event()
        self.shortcut_previous_filebtn = Event()
        self.shortcut_next_filebtn = Event()
        self.shortcut_move_filebtn_right = Event()
        self.shortcut_indent = Event()
        self.shortcut_run_selection = Event()
        self.shortcut_run_all = Event()

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
