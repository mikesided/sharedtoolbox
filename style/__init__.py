import os
from os.path import dirname, join

STYLE_PATH = dirname(os.path.abspath(__file__))
RESRC_PATH = join(dirname(dirname(__file__)), 'resources')
IMG_PATH = join(RESRC_PATH, 'images')

FONT = 'Exo'
STYLE = {
    'white': '#D1D1D1',
    'white_disabled': '#999494',
    'black': '#000000',
    'black_disabled': '#303030',
    'primary': '#80DDFF',
    'primary_active': '#2C818E',
    'primary_hover': '#226C78',
    'primary_disabled': '#2E5664',
    'secondary': '#4D87E0',
    'tertiary': '#78290f',
    'dark': '#171516',
    'dark_1': '#211A1D',
    'dark_2': '#373233',
    'dark_3': '#4C4949',
    'red': '#ba2c13',
    'downarrow': 'downarrow.png'
}

def get_stylesheet():
    """Return the stylesheet"""
    style_file = os.path.join(STYLE_PATH, 'style.qss')
    stylesheet = None

    with open(style_file) as stream:
        stylesheet = stream.read()

    for code, value in reversed(STYLE.items()):
        file_path = os.path.join(IMG_PATH, value).replace('\\', '/')
        stylesheet = stylesheet.replace('@{}'.format(code), value)
        stylesheet = stylesheet.replace('${}'.format(code), file_path)

    return stylesheet
