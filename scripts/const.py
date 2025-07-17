from __future__ import annotations

import os
import pygame

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS # type: ignore
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.font.init()
class Font:
    small = pygame.Font(resource_path('/home/p1geon/Documents/code/vault/assets/AgaveNerdFontMono-Regular.ttf'),12)
    medium = pygame.Font(resource_path('/home/p1geon/Documents/code/vault/assets/AgaveNerdFontMono-Regular.ttf'),20)

class Size:
    winsize_login = 200, 300
    winsize_manager = 400, 600
    search_bar_height = 40
    padding = 5

class Colors:
    background = pygame.Color('#171717')
    hover = pygame.Color('#292929')
    select = pygame.Color('#444444')
    input = pygame.Color('#242424')
    border = pygame.Color('#250c34')
    border_grey = pygame.Color('#4b4b4b')
    text_dark = pygame.Color('#4f4f4f')
    text_light = pygame.Color('#acacac')
    log_red = pygame.Color('#994c4c')
    log_green = pygame.Color('#3fa84d')
    log_blue = pygame.Color('#4c68ac')
    log_yellow = pygame.Color('#abac4c')
    table_highlite_colum = pygame.Color('#4b3318')
    table_highlite_word = pygame.Color('#755530')

class Misc:
    logo = pygame.image.load_sized_svg(resource_path('/home/p1geon/Documents/code/vault/assets/logo.svg'),(50,50))
    pepper = b'neaN\xf7\xb8\xf9\xe3M/w\xfd\x86{\xd06\x07\xd2\xb1\xbfD"I\xaf\xd0\xa8\xc5\xc9N\xba~\x88'
    seperator = b"\xb2]\x0f\xd9?\xbf^aI\xc3kb\x0bm\xa0\xf9\xa1{\x90\xfa\xbd'\xc2\x15\xa5c\x11\xde\xec\xd6\xd7\xaa"
