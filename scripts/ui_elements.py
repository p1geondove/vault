
import pygame
from pygame.locals import * # type: ignore
import string

from .const import Colors, Font, Size

class TextField:
    def __init__(self, rect:pygame.Rect|tuple, default_text:str = '', active=False, is_password:bool = False, no_border = False):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.font = Font.medium
        self.border_color = Colors.border
        self.text_default = default_text
        self.active = active
        self.text = ''
        self.hover = False
        self.draw_background = True
        self.draw_border = not no_border
        self.always_active = False
        self.is_password = is_password
        self.selection = None
        self.border_size = 1
        self.cursorspos = 0
        self.text_scroll = 0
        self.draw()

    def draw(self):
        color_background = Colors.hover if self.hover else Colors.input
        color_text = Colors.text_light if self.active else Colors.text_dark

        if self.draw_background:
            pygame.draw.rect(self.surface, color_background, ((0,0),self.rect.size), 0, 10)
        
        if self.draw_border:
            pygame.draw.rect(self.surface, self.border_color, ((0,0),self.rect.size), self.border_size, 10)
        
        if not self.text:
            text = self.font.render(self.text_default, True, Colors.text_dark, color_background)
            textpos = (Size.padding, (self.rect.height - text.height)/2)
            self.surface.blit(text, textpos)

        if self.is_password:
            text = self.font.render('*'*len(self.text), True, color_text, color_background)
        else:
            text = self.font.render(self.text, True, color_text, color_background)

        dist = (self.rect.width - Size.padding*2) - self.font.size('a')[0]*len(self.text)
        self.text_scroll = min(0,dist)
        cursor_x = self.font.size('a')[0] * self.cursorspos + self.text_scroll + Size.padding
        text_pos = (Size.padding + self.text_scroll, (self.rect.height - text.height)/2)
        self.surface.blit(text, text_pos)

        if self.active:
            pygame.draw.rect(self.surface, color_text, (cursor_x,text_pos[1]+2,1,text.height-4)) # cursror line

        if self.selection:
            if self.is_password:
                txt = '*'*(max(self.selection)-min(self.selection))
            else:
                txt = self.text[self.selection[0]:self.selection[1]]

            selected_text = self.font.render(txt, True, color_text, Colors.select)
            selected_pos = self.selection[0] * self.font.size('a')[0] + text_pos[0], text_pos[1]
            padding = pygame.Vector2(2, 2)
            selection_rect = selected_text.get_rect().move(-padding).move(selected_pos)
            selection_rect.size = pygame.Vector2(selection_rect.size) + padding*2
            pygame.draw.rect(self.surface, Colors.select, selection_rect, 0, 5) # selection
            self.surface.blit(selected_text, selected_pos)

    def handle_event(self, event:pygame.Event):
        special_events:list[str] = []

        if event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.hover = event.pos
                if not self.hover:
                    self.draw()
                    special_events.append('draw')
            else:
                self.hover = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.active = bool(self.hover)
                self.draw()
                special_events.append('draw')

        elif event.type == KEYDOWN and self.active:
            if event.key == K_BACKSPACE:
                if self.selection:
                    self.text = self.text[:self.selection[0]] + self.text[self.selection[1]:]
                    self.cursorspos = self.selection[0]
                    self.selection = None

                elif self.cursorspos > 0:
                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        next_pos = self.next_char(0)
                        self.text = self.text[:next_pos] + self.text[self.cursorspos:]
                        self.cursorspos = next_pos
                        
                    elif self.text:
                        self.text = self.text[:self.cursorspos-1] + self.text[self.cursorspos:]
                        self.cursorspos -= 1

                self.draw()
                special_events.append('draw')
                special_events.append('text_changed')
                
            elif event.key == K_DELETE:
                if self.selection:
                    self.text = self.text[:self.selection[0]] + self.text[self.selection[1]:]
                    self.cursorspos = self.selection[0]
                    self.selection = None
                elif pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.text = self.text[:self.cursorspos] + self.text[self.next_char(1):]
                else:
                    self.text = self.text[:self.cursorspos] + self.text[self.cursorspos + 1:]

                self.draw()
                special_events.append('draw')
                special_events.append('text_changed')

            elif event.key == K_RETURN:
                special_events.append('textfield_return')
                
            elif event.key == K_LEFT:
                start_pos = self.cursorspos
                if pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.cursorspos = self.next_char(0)
                else:
                    self.cursorspos -= 1

                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    if self.selection:
                        if start_pos == self.selection[1]:
                            self.selection[1] = self.cursorspos
                        else:
                            self.selection[0] = self.cursorspos
                    else:
                        self.selection = [self.cursorspos, start_pos]
                elif self.selection:
                    self.cursorspos = self.selection[0]
                    self.selection = None

                self.cursorspos = min(max(self.cursorspos, 0), len(self.text))
                if self.selection:
                    if self.selection[0] == self.selection[1]:
                        self.selection = None

                self.draw()
                special_events.append('draw')

            elif event.key == K_RIGHT: # literal copy of left with a bunch of bits flipped
                start_pos = self.cursorspos
                if pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.cursorspos = self.next_char(1)
                else:
                    self.cursorspos += 1

                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    if self.selection:
                        if start_pos == self.selection[0]:
                            self.selection[0] = self.cursorspos
                        else:
                            self.selection[1] = self.cursorspos
                    else:
                        self.selection = [start_pos, self.cursorspos]
                elif self.selection:
                    self.cursorspos = self.selection[1]
                    self.selection = None

                self.cursorspos = min(max(self.cursorspos, 0), len(self.text))
                if self.selection:
                    if self.selection[0] == self.selection[1]:
                        self.selection = None

                self.draw()
                special_events.append('draw')

            elif event.unicode == '\x01': # ctrl + a
                self.selection = [0, len(self.text)]
                self.draw()
                special_events.append('draw')

            elif event.unicode == '\x03': # ctrl + c
                if self.selection:
                    pygame.scrap.put_text(self.text[self.selection[0]:self.selection[1]])
                else:
                    pygame.scrap.put_text(self.text)

            elif event.unicode == '\x16': # ctrl + v
                if self.selection:
                    self.text = self.text[:self.selection[0]] + pygame.scrap.get_text() + self.text[self.selection[1]:]
                    self.cursorspos = self.selection[0]
                    self.selection = None
                else:
                    _text = pygame.scrap.get_text()
                    self.text = self.text[:self.cursorspos] + _text + self.text[self.cursorspos:]
                    self.cursorspos += len(_text)
                self.draw()
                special_events.append('draw')
                special_events.append('text_changed')

            elif event.unicode == '\x18': # ctrl + x
                if self.selection:
                    pygame.scrap.put_text(self.text[self.selection[0]:self.selection[1]])
                    self.text = self.text[:self.selection[0]] + self.text[self.selection[1]:]
                    self.cursorspos = self.selection[0]
                    self.selection = None
                else:
                    pygame.scrap.put_text(self.text)
                    self.text = ''
                    self.cursorspos = 0
                
                self.draw()
                special_events.append('draw')

            elif event.unicode and event.unicode in string.printable[:-5]:
                if self.selection:
                    self.text = self.text[:self.selection[0]] + event.unicode + self.text[self.selection[1]:]
                    self.cursorspos = self.selection[0]
                    self.selection = None
                else:
                    self.text = self.text[:self.cursorspos] + event.unicode + self.text[self.cursorspos:]

                self.cursorspos += 1
                self.draw()
                special_events.append('draw')
                special_events.append('text_changed')
        
        return special_events

    def resize(self, rect:pygame.Rect|tuple):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.draw()

    def next_char(self, direction:int):
        if direction > 0:
            next_pos = self.text.find(' ',self.cursorspos+1)
            return len(self.text) if next_pos == -1 else next_pos
        else:
            txt = self.text[self.cursorspos-1::-1]
            if not isinstance(txt,str): return 0
            dx = txt.find(' ',1)
            if dx == -1: return 0
            return self.cursorspos - dx

class Button:
    def __init__(self, rect:pygame.Rect|tuple, text=''):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)

        if text:
            self.text = text
            self.font = Font.medium

        self.hover = False
        self.pressed = False
        self.draw()

    def draw(self):
        color_background = Colors.hover if self.hover else Colors.input
        pygame.draw.rect(self.surface, color_background, ((0,0),self.rect.size), 0, 10)
        pygame.draw.rect(self.surface, Colors.border, ((0,0),self.rect.size), 1, 10)

        if self.text:
            text = self.font.render(self.text, True, Colors.text_light, color_background)
            text_pos = (pygame.Vector2(self.rect.size)-text.size) / 2
            self.surface.blit(text,text_pos)

    def handle_event(self, event:pygame.Event):
        events = []

        if event.type == MOUSEMOTION:
            hover = self.rect.collidepoint(event.pos)
            if hover != self.hover:
                self.hover = hover
                self.draw()
                events.append('draw')
        
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.pressed = True
                    self.draw()
                    events.append('pressed')
        
        elif event.type == MOUSEBUTTONUP:
            self.pressed = False

        return events

    def resize(self, rect:pygame.Rect|tuple):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.draw()

class LogField:
    def __init__(self, rect:pygame.Rect|tuple):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.title = ''
        self.body = ''
        self.title_color = Colors.text_dark
        self.body_color = Colors.text_dark
        self.draw()

    def set(self, title:str, body:str|None, title_color:pygame.Color):
        self.title = title
        self.body = body
        self.title_color = title_color

    def draw(self):
        padding = 5
        fade_size = 10
        font_height = Font.small.size('I')[1]
        
        amt_x = int((self.surface.width - padding*2)/Font.small.size('I')[0])
        if self.body:
            amt_y = int((len(self.body) / amt_x) + 1)
        else:
            amt_y = 1

        self.surface.fill(Colors.background)

        if self.rect.height < font_height: # nothing fits in screen
            return
        
        elif self.surface.height < font_height * 2: # title only
            title = Font.small.render(self.title, True, self.title_color, Colors.background)
            self.surface.blit(title, (padding,self.surface.height - title.height))

        elif self.surface.height > font_height * (amt_y+1) and self.body: # full thing
            title = Font.small.render(self.title, True, self.title_color,Colors.background)
            if self.body:
                text_parts = [self.body[x:x+amt_x] for x in range(0, len(self.body), amt_x)]
                surfaces = [Font.small.render(part,True,self.body_color,Colors.background) for part in text_parts]
                positions = [(padding,self.surface.height-y*font_height) for y in range(1,amt_y+1)][::-1]
                title_pos = padding, positions[0][1] - title.height
                self.surface.blits(zip(surfaces,positions))
            else:
                title_pos = padding, self.surface.height - title.height
            self.surface.blit(title, title_pos)

        elif self.surface.height < font_height * (amt_y+1) and self.body: # botton cutt off
            amt_y = int(self.surface.height/font_height)
            title_pos = (padding,0)
            title = Font.small.render(self.title, True, self.title_color, Colors.background)
            text_parts = [self.body[x:x+amt_x] for x in range(0, len(self.body), amt_x)]
            positions = [(padding,title.height+y*font_height) for y in range(amt_y)]
            surfaces = [Font.small.render(part,True,self.body_color,Colors.background) for part in text_parts]
            self.surface.blit(title, title_pos)
            self.surface.blits(zip(surfaces,positions))
            fade_surf = pygame.Surface((self.surface.width, fade_size), pygame.SRCALPHA)
            # alpha_array = np.linspace(0, 255, fade_size, dtype=np.uint8)
            alpha_array = [int(x/fade_size*255) for x in range(fade_size)]
            for x in range(fade_size): fade_surf.fill((Colors.background.r, Colors.background.g, Colors.background.b, alpha_array[x]), (0, x, self.surface.width, 1))
            self.surface.blit(fade_surf, (0,self.surface.height-fade_size))     

        else:
            title = Font.small.render(self.title, True, self.title_color, Colors.background)
            self.surface.blit(title, (padding,self.surface.height - title.height))

    def resize(self, rect:pygame.Rect|tuple):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.draw()
    
    def handle_event(self, event:pygame.Event):
        return []

class Table:
    def __init__(self, rect:pygame.Rect|tuple, content:list[list[str]]) -> None:
        self.rect = pygame.Rect(rect)
        self.content = content
        #print(self.content)
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.hover:tuple[int,int]|bool = False
        self.tmp_txt = None
        self.tmp_txt_index = None
        self.search_term = ''
        self.scroll_pos = 0
        self.velocity = 0
        self.draw()

    def draw(self):
        self.surface.fill(Colors.background)
        font_size = Font.medium.size('a')
        cell_size_x = self.rect.width / 3
        cell_size_y = font_size[1]

        for idx_y, line in enumerate(self.content):
            for idx_x, entry in enumerate(line):
                if entry is None:
                    entry = ''
                if idx_x == 2:
                    entry = '*' * len(entry)
                _entry = entry.lower()
                
                pos = idx_x * cell_size_x, idx_y * cell_size_y - self.scroll_pos

                if self.search_term in _entry and idx_x < 2:
                    term_rect = pygame.Rect(
                        pos[0] + Font.medium.size(_entry[:_entry.find(self.search_term)])[0],
                        pos[1],
                        Font.medium.size(self.search_term)[0],
                        cell_size_y
                    )
                    
                    if term_rect.left - idx_x*cell_size_x < cell_size_x:
                        pygame.draw.rect(self.surface, Colors.table_highlite_word, term_rect, 0, 5)
                        pygame.draw.rect(self.surface, Colors.table_highlite_colum, term_rect, 1, 5)
                text = Font.medium.render(entry,True,Colors.text_light)
                rect = pygame.Rect((0,0), (cell_size_x, cell_size_y))
                self.surface.blit(text,pos,rect)

        if self.hover:
            txt, rect, idx = self.translate(self.hover) # type: ignore
            pygame.draw.line(self.surface, Colors.table_highlite_colum, (0,rect.top), (self.rect.width, rect.top))
            pygame.draw.line(self.surface, Colors.table_highlite_colum, (0,rect.bottom), (self.rect.width, rect.bottom))

        if self.tmp_txt:
            self.tmp_txt.draw()
            self.surface.blit(self.tmp_txt.surface, self.tmp_txt.rect.topleft)

    def translate(self, global_pos:tuple[int,int]):
        font_size = Font.medium.size('a')
        idx_x = int((global_pos[0]-self.rect.x) / (self.rect.width/3))
        idx_y = int((global_pos[1] - self.rect.y + self.scroll_pos) / font_size[1])
        
        if all((0 <= idx_x < 3, 0 <= idx_y < len(self.content))):
            text = self.content[idx_y][idx_x]
        else:
            text = None

        rect =  pygame.Rect(
            int(idx_x * (self.rect.width/3)),
            int(idx_y * font_size[1] - self.scroll_pos),
            self.rect.width//3,
            font_size[1]
        )

        index = idx_y, idx_x

        return text, rect, index

    def handle_event(self, event:pygame.Event):
        events = []

        if self.tmp_txt:
            for e in self.tmp_txt.handle_event(event):
                if e == 'textfield_return':
                    if self.tmp_txt_index[0] >= len(self.content): # make new entry
                        newline = ['','','']
                        newline[self.tmp_txt_index[1]] = self.tmp_txt.text
                        self.content.append(newline)
                    else: # update existing entry
                        self.content[self.tmp_txt_index[0]][self.tmp_txt_index[1]] = self.tmp_txt.text if self.tmp_txt.text else self.tmp_txt.text_default
                
                    self.tmp_txt = None
                    self.tmp_txt_index = None
                    events.append('update_file')

        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.hover = event.pos
            else:
                self.hover = False

            if self.hover:
                self.draw()
                events.append('draw')

        elif event.type == pygame.MOUSEWHEEL:
            self.velocity -= event.y * 5
            self.tmp_txt = None
            self.tmp_txt_index = None

        elif event.type == pygame.MOUSEBUTTONDOWN and self.hover and self.velocity==0:
            if event.button == 1: # left mouse button
                txt, rect, idx = self.translate(event.pos)
                rect.move_ip(-Size.padding,0)
                self.tmp_txt = TextField(rect, txt, True, False, True)
                self.tmp_txt_index = idx

            if event.button == 3: # right mouse button
                txt, rect, idx = self.translate(event.pos)
                pygame.scrap.put_text(txt)
                print('copied to clipboard')

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB and self.tmp_txt:
                self.content[self.tmp_txt_index[0]][self.tmp_txt_index[1]] = self.tmp_txt.text if self.tmp_txt.text else self.tmp_txt.text_default
                self.tmp_txt_index = self.tmp_txt_index[0], (self.tmp_txt_index[1]+1) % 3
                #print(self.tmp_txt_index)
                txt = self.content[self.tmp_txt_index[0]][self.tmp_txt_index[1]]
                rect = self.tmp_txt.rect
                rect.x = int(self.rect.width / 3 * self.tmp_txt_index[1]) - Size.padding
                self.tmp_txt = TextField(rect, txt, True, False, True)
                #self.draw()
                events.append('update_file')

        return events
    
    def scroll_to_search(self):
        index = None
        for idx_y, line in enumerate(self.content):
            for entry in line:
                if self.search_term in entry:
                    index = idx_y
                    break
            if index: break

        font_height = Font.medium.size('a')[1]
        self.scroll_pos = index * font_height

    def update(self):
        self.scroll_pos += self.velocity
        self.velocity *= .9
        if abs(self.velocity) <= 0.01: self.velocity = 0
        self.scroll_pos = min(max(0, self.scroll_pos), (len(self.content)+1)*Font.medium.size('a')[1] - self.rect.height)
        self.draw()

