import os, pygame, time, logging


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


class BattleUserInterface():
    def __init__(self):
        self.tab_bar = pygame.Rect(0, 0, WINDOW_WIDTH//12, WINDOW_HEIGHT-WINDOW_WIDTH//12)
        self.option_bar = pygame.Rect(self.tab_bar.w, WINDOW_HEIGHT-WINDOW_HEIGHT//12, WINDOW_WIDTH-self.tab_bar.w, WINDOW_HEIGHT//12)
        self.health_square =pygame.Rect(0, WINDOW_HEIGHT-self.tab_bar.w, self.tab_bar.w, self.tab_bar.w)
        self.tab_index = 0
        self.tab_names = ['attack', 'potion', 'heal']
        self.tab_images = []
        self.heart_images = [pygame.image.load(os.path.join('assets', 'battleUI', 'hearts', '{}-heart.png'.format(num))) for num in [100, 70, 50, 20, 5, 0]]
        self.heart_images = [pygame.transform.scale(image, (self.health_square.w, self.health_square.h)) for image in self.heart_images]
        self.health = 100
        for i in range(len(self.tab_names)):
            image = pygame.image.load(os.path.join('assets', 'battleUI', '{}.png'.format(self.tab_names[i])))
            new_image = pygame.transform.scale(image, (self.tab_bar.w, self.tab_bar.w))
            self.tab_images.append(new_image)
        self.tab_image_y_increment = (self.tab_bar.h - len(self.tab_images)*self.tab_bar.w) // len(self.tab_images) + self.tab_bar.w
    def add_to_tab_index(self, num):
        self.tab_index += num if self.tab_index < len(self.tab_names) and self.tab_index > 0 else 0
    def draw(self):
        pygame.draw.rect(window, (255, 0, 0), self.tab_bar)
        pygame.draw.rect(window, (0, 255, 0), self.health_square)
        pygame.draw.rect(window, (0, 0, 255), self.option_bar)
        y = 0
        for i in range(len(self.tab_images)):
            window.blit(self.tab_images[i], (0, y))
            y += self.tab_image_y_increment
        window.blit(self.get_health_image(), (0, self.tab_bar.h))
    def get_health_image(self):
        if self.health == 100:
            return self.heart_images[0]
        if self.health == 0:
            return self.heart_images[-1]
        return self.heart_images[2]

def center_player():
    original_distance = yield None
    logger.debug('original_distance = {}'.format(original_distance))
    distance_covered = (0, 0)
    for i in range(5, 100, 2):
        to_move = (original_distance[0]//i, original_distance[1]//i)
        logger.debug('to_move = {}'.format(to_move))
        distance_covered = (distance_covered[0]+abs(to_move[0]), distance_covered[1]+abs(to_move[1]))
        if distance_covered[0] >= abs(original_distance[0]) and distance_covered[1] >= abs(original_distance[1]):
            break
        yield to_move
    yield False

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
        self.in_battle_mode = False
        self.battle_ui = BattleUserInterface()
        self.centered = False
        self.sent = False
        self.center_gen = None
    def interpret_event_for_battle_mode(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.battle_ui.add_to_tab_index(event.y)
    def update(self, pressed_keys):
        if pressed_keys[pygame.K_w]:
            self.w()
        if pressed_keys[pygame.K_a]:
            self.a()
        if pressed_keys[pygame.K_s]:
            self.s()
        if pressed_keys[pygame.K_d]:
            self.d()
        if self.in_battle_mode and self.centered == False: # center the "camera" an the player
            if self.sent:
                to_move = next(self.center_gen)
                if to_move == False:
                    self.centered = True
                    self.sent = False
                else:
                    self.rect.center = (self.rect.center[0]+to_move[0], self.rect.center[1]+to_move[1])
                    self.hitbox.center = (self.hitbox.center[0]+to_move[0], self.hitbox.center[1]+to_move[1])
                    self.current_room.background_image_position = (self.current_room.background_image_position[0]+to_move[0], self.current_room.background_image_position[1]+to_move[1])
                    for sprite in self.current_room.sprite_group.sprites():
                        sprite.rect.center = (sprite.rect.center[0]+to_move[0], self.rect.center[1]+to_move[1])
                        sprite.hitbox.center = (sprite.hitbox.center[0]+to_move[0], self.rect.center[1]+to_move[1])
            else:
                self.center_gen = center_player()
                center = (WINDOW_WIDTH//2+self.battle_ui.tab_bar.w//2, WINDOW_HEIGHT//2-self.battle_ui.option_bar.h//2)
                current_position = self.rect.center
                distance = (center[0]-current_position[0], center[1]-current_position[1])
                self.center_gen.__next__()
                to_move = self.center_gen.send(distance)
                self.sent = True
                if to_move == False:
                    self.centered = True
                    self.sent = False
                else:
                    self.rect.center = (self.rect.center[0]+to_move[0], self.rect.center[1]+to_move[1])
                    self.hitbox.center = (self.hitbox.center[0]+to_move[0], self.hitbox.center[1]+to_move[1])
                    self.current_room.background_image_position = (self.current_room.background_image_position[0]+to_move[0], self.current_room.background_image_position[1]+to_move[1])
                    for sprite in self.current_room.sprite_group.sprites():
                        sprite.rect.center = (sprite.rect.center[0]+to_move[0], self.rect.center[1]+to_move[1])
                        sprite.hitbox.center = (sprite.hitbox.center[0]+to_move[0], self.rect.center[1]+to_move[1])
        if not self.in_battle_mode:
            self.centered = False
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
        if self.in_battle_mode:
            self.hitbox.y += self.velocity
            for sprite in self.current_room.sprite_group.sprites():
                sprite.rect.y += self.velocity
                sprite.hitbox.y += self.velocity
            self.current_room.background_image_position = (self.current_room.background_image_position[0], self.current_room.background_image_position[1] + self.velocity)
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
        if self.in_battle_mode:
            self.hitbox.x += self.velocity
            for sprite in self.current_room.sprite_group.sprites():
                sprite.rect.x += self.velocity
                sprite.hitbox.x += self.velocity
            self.current_room.background_image_position = (self.current_room.background_image_position[0] + self.velocity, self.current_room.background_image_position[1])
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
        if self.in_battle_mode:
            self.hitbox.y -= self.velocity
            for sprite in self.current_room.sprite_group.sprites():
                sprite.rect.y -= self.velocity
                sprite.hitbox.y -= self.velocity
            self.current_room.background_image_position = (self.current_room.background_image_position[0], self.current_room.background_image_position[1] - self.velocity)
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
        if self.in_battle_mode:
            self.hitbox.x -= self.velocity
            for sprite in self.current_room.sprite_group.sprites():
                sprite.rect.x -= self.velocity
                sprite.hitbox.x -= self.velocity
            self.current_room.background_image_position = (self.current_room.background_image_position[0] - self.velocity, self.current_room.background_image_position[1])
            return
        self.rect.x += self.velocity

class Room:
    def __init__(self, name, compass, bg_image_path, sprite_group):
        self.name = name
        self.adjacent_rooms = compass
        self.background_image = pygame.transform.scale(pygame.image.load(bg_image_path), (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background_image_position = (0, 0)
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
        CLOCK.tick(FPS)
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
    debug_tool_names = [debug_font.render(key, True, (47, 203, 104) if debug_catalog[key] else (206, 52, 45)) for key in debug_catalog]
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
                        logger.debug('{key} is now {bool}'.format(key=key, bool=debug_catalog[key]))
                        y_level =  1 + (index // 3)
                        tool_name_flipped_color_text = debug_font.render(key, True, (47, 203, 104) if debug_catalog[key] else (206, 52, 45))
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
    if debug_catalog['SHOW_CURSOR_LOCATION']:
        cursor_location = pygame.mouse.get_pos()
        cursor_location_text = debug_font.render(str(cursor_location), True, (206, 52, 45))
        window.blit(cursor_location_text, (WINDOW_WIDTH-cursor_location_text.get_width(), 0))
    player.in_battle_mode = debug_catalog['BATTLE_MODE']
    

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
    window.blit(player.current_room.background_image, player.current_room.background_image_position)
    for sprite in sprites_sorted_by_z_index_increasing:
        window.blit(sprite.image, sprite.rect)
    if player.in_battle_mode:
        player.battle_ui.draw()


    
def main():
    pygame.init()
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    catalog_file_handler = logging.FileHandler('cata.log')
    catalog_file_handler.setLevel(logging.DEBUG)
    catalog_file_formatter = logging.Formatter('%(levelname)s: [%(asctime)s]: %(name)s: %(lineno)d - %(message)s')
    catalog_file_handler.setFormatter(catalog_file_formatter)
    logger.addHandler(catalog_file_handler)
    DEBUG_MODE = True # this is the ONLY value that should CHANGE
    if DEBUG_MODE:
        global debug_font
        debug_font = pygame.font.Font(os.path.join('assets', 'fonts', 'VT323.ttf'), 32)
        debug_catalog = {
            'SHOW_CURSOR_LOCATION': False,
            'ROOM_JUMP': DEBUG_MODE, # automatically set ROOM_JUMP on if DEBUG_MODE is on
            'SHOW_HITBOXES': False,
            'BATTLE_MODE': False
            }
    logger.debug('DEBUG_MODE[{}]'.format(DEBUG_MODE))
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    global CLOCK, FPS
    CLOCK = pygame.time.Clock()
    FPS = 60 # GAME SETTING
    global window
    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_surface().get_size()
    pygame.display.set_caption('project Talico')
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
                    debug_menu(debug_catalog) # opens an overlay with clickable text that turns specific items in debug_catalog on/off
                debug_actions(debug_catalog, player, event) # keyboard events are interpreted here to produce an outcome
            if player.in_battle_mode:
                player.interpret_event_for_battle_mode(event)

        pressed_keys = pygame.key.get_pressed()
        player_group.update(pressed_keys)
        window.fill((0, 0, 0))
        draw(player)
        debug_effects(debug_catalog, player)
        pygame.display.update()
        CLOCK.tick(FPS)
    

if __name__ == '__main__':
    main()
    pygame.quit()
    logger.debug('EOF')
