import os, sys, pygame, time, logging


BLACK = (0, 0, 0)


class RoomSprite(pygame.sprite.Sprite):
    def __init__(self, image_path, position, scale, enter_room=False, enter_position=(0, 0), phase_through=False, hitbox=None):
        super().__init__()
        self.original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.original_image, (self.original_image.get_width()*scale, self.original_image.get_height()*scale))
        self.rect = self.image.get_rect()
        self.rect.center = position
        if hitbox is None:
            self.hitbox = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        else:
            self.hitbox = pygame.Rect(0, 0, *hitbox)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom
        self.enter_room = enter_room
        self.phase_through = phase_through
        self.enter_position = enter_position


class Player(pygame.sprite.Sprite):
    def __init__(self, image_path, position, scale, vel, room_gen, hitbox=None):
        super().__init__()
        self.original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.original_image, (self.original_image.get_width()*scale, self.original_image.get_height()*scale))
        self.rect = self.image.get_rect()
        self.rect.center = position
        if hitbox is None:
            self.hitbox = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        else:
            self.hitbox = pygame.Rect(0, 0, hitbox[0], hitbox[1])
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom
        self.velocity = vel
        self.gen_next_room = room_gen()
        self.current_room = next(self.gen_next_room)
    def update(self, pressed_keys):
        if pressed_keys[pygame.K_w]:
            self.w()
        if pressed_keys[pygame.K_a]:
            self.a()
        if pressed_keys[pygame.K_s]:
            self.s()
        if pressed_keys[pygame.K_d]:
            self.d()
        
    def w(self):
        phase = True
        self.hitbox.y -= self.velocity
        for sprite in self.current_room.sprite_group.sprites():
            if pygame.Rect.colliderect(self.hitbox, sprite.hitbox):
                if sprite.enter_room:
                    self.current_room = self.gen_next_room.send('up')
                    self.rect.center = sprite.enter_position # teleport to a new destination, should be a tuple (0, 0)
                    self.hitbox.centerx = self.rect.centerx
                    self.hitbox.bottom = self.rect.bottom
                    return
                if not sprite.phase_through:
                    phase = False
        if not phase:
            self.hitbox.y += self.velocity
            return
        self.rect.y -= self.velocity
    def a(self):
        phase = True
        self.hitbox.x -= self.velocity
        for sprite in self.current_room.sprite_group.sprites():
            if pygame.Rect.colliderect(self.hitbox, sprite.hitbox):
                if sprite.enter_room:
                    self.current_room = self.gen_next_room.send('left')
                    self.rect.center = sprite.enter_position # teleport to a new destination, should be a tuple (0, 0)
                    self.hitbox.centerx = self.rect.centerx
                    self.hitbox.bottom = self.rect.bottom
                    return
                if not sprite.phase_through:
                    phase = False
        if not phase:
            self.hitbox.x += self.velocity
            return
        self.rect.x -= self.velocity
    def s(self):
        phase = True
        self.hitbox.y += self.velocity
        for sprite in self.current_room.sprite_group.sprites():
            if pygame.Rect.colliderect(self.hitbox, sprite.hitbox):
                if sprite.enter_room:
                    self.current_room = self.gen_next_room.send('down')
                    self.rect.center = sprite.enter_position # teleport to a new destination, should be a tuple (0, 0)
                    self.hitbox.centerx = self.rect.centerx
                    self.hitbox.bottom = self.rect.bottom
                    return
                if not sprite.phase_through:
                    phase = False
        if not phase:
            self.hitbox.y -= self.velocity
            return
        self.rect.y += self.velocity
    def d(self):
        phase = True
        self.hitbox.x += self.velocity
        for sprite in self.current_room.sprite_group.sprites():
            if pygame.Rect.colliderect(self.hitbox, sprite.hitbox):
                if sprite.enter_room:
                    self.current_room = self.gen_next_room.send('right')
                    self.rect.center = sprite.enter_position # teleport to a new destination, should be a tuple (0, 0)
                    self.hitbox.centerx = self.rect.centerx
                    self.hitbox.bottom = self.rect.bottom
                    return
                if not sprite.phase_through:
                    phase = False
        if not phase:
            self.hitbox.x -= self.velocity
            return
        self.rect.x += self.velocity

class Room:
    def __init__(self, name, compass, bg_image_path, sprite_group):
        self.name = name
        self.adjacent_rooms = compass
        self.background_image = pygame.transform.scale(pygame.image.load(bg_image_path), (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.sprite_group = sprite_group
    def __str__(self):
        return '"{name}": {adjacent_rooms}'.format(name=self.name, adjacent_rooms=self.adjacent_rooms)


def room_gen():
    room_1_group = pygame.sprite.Group()
    door = RoomSprite(os.path.join('assets', 'images', 'sprites', 'door.png'), (WINDOW_WIDTH-32, WINDOW_HEIGHT//2), 1.8, enter_room=True, enter_position=(150, WINDOW_HEIGHT//2))
    room_1_group.add(door)
    while True:
        direction = yield Room('starting-room', 'right', os.path.join('assets', 'images', 'scenery', 'bg.jpg'), room_1_group)
        if direction == 'right':
            room_2_group = pygame.sprite.Group()
            left_door = RoomSprite(os.path.join('assets', 'images', 'sprites', 'door.png'), (32, WINDOW_HEIGHT//2), 1.8, enter_room=True, enter_position=(WINDOW_WIDTH-150, WINDOW_HEIGHT//2))
            right_door = RoomSprite(os.path.join('assets', 'images', 'sprites', 'door.png'), (WINDOW_WIDTH-32, WINDOW_HEIGHT//2), 1.8, enter_room=True, enter_position=(150, WINDOW_HEIGHT//2))
            cone = RoomSprite(os.path.join('assets', 'images', 'sprites', 'cone.png'), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), 1, phase_through=False, hitbox=(400, 190))
            room_2_group.add(left_door, right_door, cone)
            while True:
                direction = yield Room('room-2', 'left&right', os.path.join('assets', 'images', 'scenery', 'bg2.jpg'), room_2_group)
                if direction == 'right':
                    room_3_group = pygame.sprite.Group()
                    left_door = RoomSprite(os.path.join('assets', 'images', 'sprites', 'door.png'), (32, WINDOW_HEIGHT//2), 1.8, enter_room=True, enter_position=(WINDOW_WIDTH-150, WINDOW_HEIGHT//2))
                    room_3_group.add(left_door)
                    while True:
                        direction = yield Room('room-3', 'left', os.path.join('assets', 'images', 'scenery', 'bg3.png'), room_3_group)
                        if direction == 'left':
                            break
                    continue
                if direction == 'left':
                    break
            continue


def start_screen():
    start_screen_image = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'images', 'scenery', 'start-screen.png')), (WINDOW_WIDTH, WINDOW_HEIGHT))
    window.blit(start_screen_image, (0, 0))
    start_screen_music = pygame.mixer.Sound(os.path.join('assets', 'audio', 'music', 'frosty.wav'))
    start_screen_music.play(-1)
    pygame.display.update()
    pressed_space = False
    while not pressed_space:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pressed_space = True
            elif event.type == pygame.QUIT:
                return pygame.QUIT
    start_screen_music.fadeout(3000)
    fade_out = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_out = fade_out.convert()
    fade_out.fill(BLACK)
    for i in range(255):
        fade_out.set_alpha(i)
        window.blit(fade_out, (0, 0))
        pygame.display.update()
        CLOCK.tick(FPS)
    return None
    

def confirm_escape_game():
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay = overlay.convert()
    overlay.fill(BLACK)
    overlay.set_alpha(100)
    window.blit(overlay, (0, 0))
    font = pygame.font.SysFont('comicsans', 52)
    text = font.render('Are you sure? Press the ESC key again to terminate this script', True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
    window.blit(text, text_rect)
    pygame.display.flip()
    pressed_a_key = False
    while not pressed_a_key:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminated_png = pygame.image.load(os.path.join('assets', 'images', 'terminated.png'))
                    terminated_wav = pygame.mixer.Sound(os.path.join('assets', 'audio', 'sfx', 'terminated.wav'))
                    png_rect = terminated_png.get_rect()
                    png_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
                    window.fill(BLACK)
                    window.blit(terminated_png, png_rect)
                    pygame.display.flip()
                    terminated_wav.play()
                    time.sleep(1.2) # give time for the sound to play
                    return pygame.QUIT
                else:
                    pressed_a_key = True
                    break
        CLOCK.tick(FPS)

class Cursor(pygame.sprite.Sprite):
    def __init__(self, image_path, scale):
        super().__init__()
        self.original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.original_image, (self.original_image.get_width()*scale, self.original_image.get_height()*scale))
        self.rect = self.image.get_rect()
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
            


def debug_menu(debug_catalog):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(180)
    window.blit(overlay, (0, 0))
    debug_tool_name_font = pygame.font.Font(os.path.join('assets', 'fonts', 'VT323.ttf'), 32)
    debug_tool_names = [debug_tool_name_font.render(key, True, (47, 203, 104) if debug_catalog[key] else (206, 52, 45)) for key in debug_catalog]
    left_x = WINDOW_WIDTH // 4
    middle_x = left_x * 2
    right_x = left_x + middle_x
    STARTING_Y = 100
    y = 100
    for count, debug_tool_name in enumerate(debug_tool_names):
        if count % 3 == 0:
            window.blit(debug_tool_name, (left_x - debug_tool_name.get_width()//2, y))
        if count % 3 == 1:
            window.blit(debug_tool_name, (middle_x - debug_tool_name.get_width()//2, y))
        if count % 3 == 2:
            window.blit(debug_tool_name, (right_x - debug_tool_name.get_width()//2, y))
            y += 100
    pygame.display.flip()
    cursor = Cursor(os.path.join('assets', 'images', 'sprites', 'nothing.png'), 2) # i need to somehow draw the background everytime the cursor is drawn, for now I'll use a png of nothing
    cursor_group = pygame.sprite.Group()
    cursor_group.add(cursor)
    while True:
        cursor_group.update()
        # cursor_group.draw(window) # irrelevant for a blank image
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SLASH:                    
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for index, debug_tool_name in enumerate(debug_tool_names):
                    name_rect = debug_tool_name.get_rect()
                    y_times = 1 + (index // 3)
                    if index % 3 == 0:
                        name_rect.center = (left_x, y_times*STARTING_Y)
                    elif index % 3 == 1:
                        name_rect.center = (middle_x, y_times*STARTING_Y)
                    elif index % 3 == 2:
                        name_rect.center = (right_x, y_times*STARTING_Y)
                    if pygame.Rect.colliderect(cursor.rect, name_rect):
                        key = list(debug_catalog.keys())[index]
                        debug_catalog[key] = not debug_catalog[key]
                        y_level =  1 + (index // 3)
                        tool_name_flipped_color_text = debug_tool_name_font.render(key, True, (47, 203, 104) if debug_catalog[key] else (206, 52, 45))
                        if index % 3 == 0:
                            window.blit(tool_name_flipped_color_text, (left_x - tool_name_flipped_color_text.get_width()//2, STARTING_Y*y_level))
                        elif index % 3 == 1:
                            window.blit(tool_name_flipped_color_text, (middle_x - tool_name_flipped_color_text.get_width()//2, STARTING_Y*y_level))
                        elif index % 3 == 2:
                            window.blit(tool_name_flipped_color_text, (right_x - tool_name_flipped_color_text.get_width()//2, STARTING_Y*y_level))
                        pygame.display.update(tool_name_flipped_color_text.get_rect())
        pygame.display.update()
        CLOCK.tick(FPS)

def debug_effects(debug_catalog, player):
    if debug_catalog['SHOW_HITBOXES']:
        for sprite in player.current_room.sprite_group.sprites():
            pygame.draw.rect(window, (255, 0, 0), sprite.hitbox)
        pygame.draw.rect(window, (0, 0, 255), player.hitbox)

def debug_actions(debug_catalog, player, event):
    if debug_catalog['ROOM_JUMP']:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.current_room = player.gen_next_room.send('up')
            elif event.key == pygame.K_DOWN:
                player.current_room = player.gen_next_room.send('down')
            elif event.key == pygame.K_LEFT:
                player.current_room = player.gen_next_room.send('left')
            elif event.key == pygame.K_RIGHT:
                player.current_room = player.gen_next_room.send('right')
        
def draw(player):
    player_and_others = player.current_room.sprite_group.sprites() + [player]
    sprites_sorted_by_z_index_increasing = sorted(player_and_others, key=lambda sprite: sprite.hitbox.top)
    window.blit(player.current_room.background_image, (0, 0))
    for sprite in sprites_sorted_by_z_index_increasing:
        window.blit(sprite.image, sprite.rect)


    
def main():
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    whole_log_handler = logging.FileHandler('cata.log')
    whole_log_handler.setLevel(logging.DEBUG)
    whole_log_formatter = logging.Formatter('%(levelname)s: [%(asctime)s]: %(name)s: %(lineno)d - %(message)s')
    whole_log_handler.setFormatter(whole_log_formatter)
    logger.addHandler(whole_log_handler)
    DEBUG_MODE = True # this is the ONLY value that should CHANGE
    logger.debug('Ran with DEBUG_MODE = {DEBUG_MODE}'.format(DEBUG_MODE))
    debug_catalog = {
        'SHOW_CURSOR_LOCATION': False,
        'ROOM_JUMP': DEBUG_MODE, # automatically set ROOM_JUMP on if DEBUG_MODE is on
        'SHOW_HITBOXES': False
        }
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    pygame.init()
    global CLOCK, FPS
    CLOCK = pygame.time.Clock()
    FPS = 60 # GAME SETTING
    global window
    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_surface().get_size()
    pygame.display.set_caption('Talico')
    if start_screen() == pygame.QUIT: return
    player = Player(os.path.join('assets', 'images', 'sprites', 'calico.png'), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), 0.7, 10, room_gen, (100, 50))
    player_group = pygame.sprite.Group()
    player_group.add(player)
    pygame.display.flip()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if confirm_escape_game() == pygame.QUIT: return
            if DEBUG_MODE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SLASH:
                    debug_menu(debug_catalog) # switch debug tools on/off
                debug_actions(debug_catalog, player, event) # debug tools actions

        pressed_keys = pygame.key.get_pressed()
        player_group.update(pressed_keys)
        draw(player)
        debug_effects(debug_catalog, player)
        pygame.display.update()
        CLOCK.tick(FPS)
    

if __name__ == '__main__':
    main()
    pygame.quit()
    logger.debug('EOF')
 