import sys
import os
import pygame
import json

from pathlib import Path
from tkinter.filedialog import askopenfilename

from .ui_elements import TextField, Button, LogField, Table
from .const import Size, Colors, Misc
from .file_handler import FileInterface

class Login:
    def __init__(self) -> None:
        self.surface = pygame.display.set_mode(Size.winsize_login, pygame.SRCALPHA, vsync=1)
        pygame.display.set_icon(Misc.logo)
        pygame.display.set_caption('vault login')
        pygame.scrap.init()

        self.password_box = TextField((30,100,140,40),'Password', True, True)
        self.button_select = Button((30,150,140,40), 'select file')
        self.button_login = Button((30,200,140,40),'Login')
        self.log_field = LogField((0,250,200,50))
        self.logo = Misc.logo

        # automatically select password.vault file if avaibalble
        if os.path.exists('password.vault'):
            self.selected_file = 'password.vault'
            self.log_field.title = 'vault file'
            self.log_field.title_color = Colors.log_green
            self.log_field.body = self.selected_file
            self.button_login.text = 'login'
        else:
            self.selected_file = None
            self.log_field.title = 'no file selected'

        self.ui_elements = [self.password_box, self.button_login, self.log_field, self.button_select]
        self.draw()

    def handle_event(self, event:pygame.Event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(1)

        for e in self.password_box.handle_event(event):
            if e == 'draw':
                self.surface.blit(self.password_box.surface, self.password_box.rect.topleft)
            elif e == 'textfield_return' and self.selected_file:
                return self.handle_file()

        for e in self.button_login.handle_event(event):
            if e == 'draw':
                self.surface.blit(self.button_login.surface, self.button_login.rect.topleft)
            elif e == 'pressed' and self.selected_file:
                return self.handle_file()

        for e in self.button_select.handle_event(event):
            if e == 'draw':
                self.surface.blit(self.button_select.surface, self.button_select.rect.topleft)

            elif e == 'pressed':
                file = askopenfilename()
                if not isinstance(file, str): return
                self.selected_file = file
                self.log_field.body = file

                if self.selected_file.endswith('.vault'):
                    self.log_field.set('vault file', self.selected_file, Colors.log_green)
                    self.button_login.text = 'login'
                elif self.selected_file.endswith('.lock'):
                    self.log_field.set('lock file', self.selected_file, Colors.log_blue)
                    self.button_login.text = 'decrypt'

                elif self.selected_file.endswith('.json'):
                    self.log_field.set('json -> vault', self.selected_file, Colors.log_yellow)
                    self.button_login.text = 'convert'

                elif self.selected_file:
                    self.log_field.set('regular file', self.selected_file, Colors.log_red)
                    self.button_login.text = 'encrypt'

                else:
                    self.log_field.set('no file selected', None, Colors.text_light)

                self.draw()

    def draw(self):
        self.surface.fill(Colors.background)
        self.surface.blit(self.logo,(75,25))

        for e in self.ui_elements:
            e.draw()
            self.surface.blit(e.surface, e.rect.topleft)

    def handle_file(self):
        try:
            match self.button_login.text:
                case 'login':
                    return self.open_manager()
                case 'encrypt':
                    FileInterface(self.selected_file).lock(self.password_box.text)
                case 'decrypt':
                    FileInterface(self.selected_file).unlock(self.password_box.text)
                case 'convert':
                    FileInterface(self.selected_file).lock(self.password_box.text)
                    os.rename(self.selected_file+'.lock', 'password.vault')

        except ValueError:
            self.password_box.border_color = Colors.log_red
            self.password_box.draw()
            self.draw()

    def open_manager(self):
        password_list = FileInterface(self.selected_file).get_passwords(self.password_box.text)

        # Several checks to see if the input file is good
        if all([
            isinstance(password_list, list),
            isinstance(password_list[0], list),
            isinstance(password_list[0][0], str)
        ]):
            return Manager(Path(self.selected_file),self.password_box.text)
        else:
            self.log_field.title = 'Not a vault file'
            self.log_field.title_color = Colors.log_red
            self.log_field.body = "File successfully encrypted, but isn't the proper layout"

    def update(self):
        ...

class Manager:
    def __init__(self, vault_file_path:Path, password_cleartext:str) -> None:
        self.surface = pygame.display.set_mode(Size.winsize_manager, pygame.SRCALPHA, vsync=1)
        self.vault_file_path = vault_file_path
        self.password_cleartext = password_cleartext
        self.password_list = FileInterface(self.vault_file_path).get_passwords(self.password_cleartext)
        
        self.search_bar = TextField((
                Size.padding,
                Size.padding,
                Size.winsize_manager[0] - Size.padding*2,
                Size.search_bar_height
            ),'search',True)
        
        self.table = Table((
                0,
                Size.search_bar_height + Size.padding*2,
                Size.winsize_manager[0],
                Size.winsize_manager[1] - Size.search_bar_height - Size.padding*2
            ), self.password_list)

        self.ui_elements = [self.table, self.search_bar]
        self.draw()

    def handle_event(self, event:pygame.Event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(1)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.table.tmp_txt:
                    self.table.tmp_txt = None
                    self.table.tmp_txt_index = None
                else:
                    return Login()

        for e in self.search_bar.handle_event(event):
            if e == 'draw':
                self.surface.blit(self.search_bar.surface, self.search_bar.rect.topleft)
            elif e == 'text_changed':
                self.table.search_term = self.search_bar.text.lower()
                self.table.scroll_to_search()
                self.table.draw()
                self.surface.blit(self.table.surface, self.table.rect.topleft)

        for e in self.table.handle_event(event):
            if e == 'draw':
                self.surface.blit(self.table.surface, self.table.rect.topleft)
            elif e == 'update_file':
                content = json.dumps(self.table.content).encode()
                FileInterface(self.vault_file_path).update(self.password_cleartext, content)

    def draw(self):
        self.surface.fill(Colors.background)

        for element in self.ui_elements:
            self.surface.blit(element.surface, element.rect.topleft)

    def update(self):
        self.table.update()
        self.draw()

