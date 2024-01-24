import pygame
import os
import sys

pygame.init()
size = WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
FPS = 60
clock = pygame.time.Clock()
player_move_speed = 50
GRAVITY = 0


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = os.path.join('data', filename)
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    return level_map


def game_over_screen():
    game_over_text = ['Вы проиграли', '',
                      'Не растраивайтесь!!!',
                      'И попробуйте ещё раз']
    screen.fill('#000000')

    font = pygame.font.Font(None, 30)
    main_font = pygame.font.Font(None, 100)
    text_coord = 50
    main_text = main_font.render(game_over_text[0], 1, pygame.Color('red'))
    text_rect = main_text.get_rect()
    text_rect.top = 20
    text_rect.right = 600
    screen.blit(main_text, text_rect)
    for line in game_over_text[1::]:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(10)


tile_image = {'sky': load_image('fon.jpg'),
              'ground': load_image('grass.png'),
              'box': load_image('box.png'),
              'enemy': load_image('mar.png'),
              'trap': load_image('bomb.png')}

player_image = load_image('mar.png')
tile_width = tile_height = 50
tile_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_group, all_sprites)
        self.image = tile_image[tile_type]
        if tile_type == 'box':
            wall_group.add(self)
        if tile_type == 'ground':
            ground_group.add(self)
        if tile_type == 'enemy':
            enemy_group.add(self)
        if tile_type == 'trap':
            trap_group.add(self)

        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


player_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 3)

    def update(self):
        if pygame.sprite.spritecollideany(self, ground_group) is None:
            self.rect = self.rect.move(0, GRAVITY)

    def jump(self):
        pass  # здесь должна быть функция прыжка


player = None


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('sky', x, y)
            elif level[y][x] == '#':
                Tile('ground', x, y)
            elif level[y][x] == '%':
                Tile('box', x, y)
            elif level[y][x] == '@':
                Tile('ground', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'E':
                Tile('ground', x, y)
                Tile('enemy', x, y)
            elif level[y][x] == '*':
                Tile('ground', x, y)
                Tile('trap', x, y)
    return new_player, x, y


def defeat_enemy(enemy):
    global enemies
    if enemy is None:
        return False
    Tile('ground', (player.rect.x - 15) // tile_width, (player.rect.y - 3) // tile_height)
    enemy.kill()
    enemies -= 1



def main():
    global player
    global enemies

    player, level_x, level_y = generate_level(load_level('fight.txt'))

    running = True
    enemies = 3

    tile_group.draw(screen)
    vector = -1
    while running:
        if enemies == 0:
            player.kill()
            return 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if player is not None:
            keys = pygame.key.get_pressed()

            if pygame.sprite.spritecollideany(player, wall_group) is None:

                if keys[pygame.K_LEFT]:
                    if vector == 1:
                        vector *= -1
                        player.image = pygame.transform.flip(player.image, True, False)
                    while pygame.sprite.spritecollideany(player, wall_group) is None:
                        player.rect.right -= player_move_speed
                        defeat_enemy(pygame.sprite.spritecollideany(player, enemy_group))
                    player.rect.right += player_move_speed
                elif keys[pygame.K_RIGHT]:
                    if vector == -1:
                        vector *= -1
                        player.image = pygame.transform.flip(player.image, True, False)
                    while pygame.sprite.spritecollideany(player, wall_group) is None:
                        player.rect.right += player_move_speed
                        defeat_enemy(pygame.sprite.spritecollideany(player, enemy_group))
                    player.rect.right -= player_move_speed
                elif keys[pygame.K_UP]:
                    while pygame.sprite.spritecollideany(player, wall_group) is None:
                        player.rect.top -= player_move_speed
                        defeat_enemy(pygame.sprite.spritecollideany(player, enemy_group))
                    player.rect.top += player_move_speed
                elif keys[pygame.K_DOWN]:
                    while pygame.sprite.spritecollideany(player, wall_group) is None:
                        player.rect.top += player_move_speed
                        defeat_enemy(pygame.sprite.spritecollideany(player, enemy_group))
                    player.rect.top -= player_move_speed
            if pygame.sprite.spritecollideany(player, trap_group):
                player.kill()
                return 1

        screen.fill('#0ec3ff')
        all_sprites.draw(screen)
        all_sprites.update()
        tile_group.draw(screen)
        player_group.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
