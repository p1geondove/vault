#!/home/p1geon/Documents/code/vault/.venv/bin/python

import pygame
from scripts import Login

def main():
    screen = Login()
    clock = pygame.Clock()

    while True:
        for event in pygame.event.get():
            if (new_screen := screen.handle_event(event)):
                screen = new_screen

        screen.update()
        pygame.display.flip()
        clock.tick()

if __name__ == '__main__':
    main()

"""
TODO
when a tmp textfield is open and you press tab, update entry, close that tmp_textfield and open a new tmp field right next to it. basically cycle idx_x 0 -> 1 -> 2 -> 0 ...
"""
