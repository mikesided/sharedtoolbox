# System Imports
import os
import sys
import datetime
import traceback

# Third-Party Imports

# Local Imports
from sharedtoolbox import configs, event_handler

# ______________________________________________________________________________________________________________________

class CodeHandler:
    """
    Class that handles running user code from the editor
    """

    @staticmethod
    def run_code(code):
        """Runs a piece of code"""
        # Gather some data
        loc = len(code.split('\n'))
        start_timestamp = datetime.datetime.now()

        # Print "begin" statement
        with ColoredConsole('#14ebff'):  # Light blue
            print(' --- Start code execution ---')

        try:
            #os.environ['PYTHONPATH'] = r'C:\Users\Michael\Downloads\work\tmaopstoolTestRelease\tmaopstoolTestRelease' + os.pathsep + os.environ.get('PYTHONPATH')
            #print(os.environ.get('PYTHONPATH'))
            sys.path.append(r'C:\Users\Michael\Downloads\work\tmaopstoolTestRelease\tmaopstoolTestRelease')
            exec(code, {})

        except:
            with ColoredConsole('red'):
                stack = CodeHandler._format_stack_trace(code=code, stack=traceback.format_exc())
                print(stack)
        finally:
            end_timestamp = datetime.datetime.now()
            # Print "end" statement
            with ColoredConsole('#14ebff'):  # Light blue
                print('  --- Code execution completed in {} ---'.format(str(end_timestamp - start_timestamp)))

    @staticmethod
    def _format_stack_trace(code, stack):
        """Formats the stacktrace for the given code/stack
        
        Args:
            code (str): Code ran
            stack (str): stack trace
        
        Returns:
            str: Formatted stack trace
        """
        try:
            split_stack = stack.split('\n')
            # Try extracting the code line number
            error_line = int(split_stack[3].split(',')[1].lstrip('line '))
            error_code = code.split('\n')[error_line-1]
            if not split_stack[4].endswith(error_code):
                split_stack.insert(4, '    ' + error_code)

            # Extract this file's content from the stack
            stack = split_stack[0] + '\n' + '\n'.join(split_stack[3:])
            return stack
        except:
            # Something went wrong, simply return the regular stack
            return stack



class ColoredConsole():
    """Colors the console, and adds a heading and trailing <br>"""
    def __init__(self, color):
        self.color = color

    def __enter__(self, *args):
        event_handler.console_write_html.emit('<span style="color: {};"><br>'.format(self.color))

    def __exit__(self, *args):
        event_handler.console_write_html.emit('<br></span>')


# ______________________________________________________________________________________________________________________
