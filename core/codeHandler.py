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
            print('  --- [{}]: Start code execution ---  '.format(datetime.datetime.now().strftime('%H:%M:%S')))

        # Inject environment override
        original_env, original_path = CodeHandler._inject_environment()

        try:
            exec(code, {})

        except:
            with ColoredConsole('red'):
                stack = CodeHandler._format_stack_trace(code=code, stack=traceback.format_exc())
                print(stack)
        finally:
            end_timestamp = datetime.datetime.now()
            # Print "end" statement
            with ColoredConsole('#14ebff'):  # Light blue
                print('  --- Code execution completed in {} ---  '.format(str(end_timestamp - start_timestamp)))

            # Extract environment
            os.environ = original_env
            sys.path = original_path

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
        
    @staticmethod
    def _inject_environment():
        """Inject the profile's environment.
        Update all keys in os.environ to what the user defined in its profile (retaining original values when 
        {{{ENVIRONMENT}}} is found)
        Also update sys.path when interacting with PYTHONPATH
        
        Returns:
            dict, list: Original os.environ, Original sys.path
        """
        app_env = os.environ.copy()
        app_path = sys.path.copy()
        built_ins_path = [x for x in sys.path if x not in os.environ.get('PYTHONPATH', '').split(os.pathsep)]

        for key in configs.Prefs.env_vars.keys():
            os.environ[key] = ''
            if key == 'PYTHONPATH':
                sys.path = built_ins_path

        for key, values in configs.Prefs.env_vars.items():
            for value in values:
                os.environ[key] += os.pathsep if os.environ.get(key) else ''
                if value == '{{{ENVIRONMENT}}}':
                    os.environ[key] += app_env.get(key)
                else:
                    os.environ[key] += value
            if key == 'PYTHONPATH':
                for value in values:
                    if value == '{{{ENVIRONMENT}}}':
                        sys.path.append(app_env.get(key))
                    else:
                        sys.path.append(value)
                sys.path.append(built_ins_path)

        return app_env, app_path




class ColoredConsole():
    """Colors the console, and adds a heading and trailing <br>"""
    def __init__(self, color):
        self.color = color

    def __enter__(self, *args):
        #event_handler.console_write_html.emit('<span style="color: {};"><br>'.format(self.color))
        event_handler.console_write_html.emit('<span style="color: {};"><br>'.format(self.color))

    def __exit__(self, *args):
        event_handler.console_write_html.emit('<br></span>')


# ______________________________________________________________________________________________________________________
