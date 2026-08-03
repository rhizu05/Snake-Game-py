import pygame
import asyncio
import random

pygame.init()
pygame.mixer.init()

# Image Background
bg_over = pygame.image.load('resource/images/bg-over.png')
bg_start = pygame.image.load('resource/images/bg-start.png')
bg_intro = pygame.image.load('resource/images/bg-intro.png')
icon_image = pygame.image.load('resource/images/logo-putih-ITG.png')
itg_logo = pygame.transform.scale(icon_image, (100, 100))

# Efek Suara
sfx_food = pygame.mixer.Sound('resource/audio/eat_food.ogg')
sfx_trap = pygame.mixer.Sound('resource/audio/eat_trap.ogg')
sfx_over = pygame.mixer.Sound('resource/audio/gameover.ogg')

# Warna-warna
white = (255, 255, 255)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
brown = (158, 111, 75, 1)
yellow = (223, 177, 82, 255)
green_bg = (21, 105, 10, 255)

# Ukuran display
dis_width = 800
dis_height = 600
border_thickness = 10

# Membuat display game
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Snake Game')

# Mengatur clock untuk mengontrol kecepatan permainan
clock = pygame.time.Clock()

# Ukuran blok snake dan kecepatan permainan
snake_block = 20
initial_speed = 10

# Mendefinisikan font untuk teks dalam permainan
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 20)

# Memuat gambar loading bar
loading_image = pygame.image.load('resource/images/loading.png')

# Menampilkan score saat ini
def display_score(score):
    value = score_font.render("Your Score: " + str(score), True, white)
    dis.blit(value, [20, 10])

# Menampilkan level saat ini
def level_display(level):
    value = score_font.render("Level " + str(level), True, white)
    dis.blit(value, [dis_width - 110, 10])

# Menampilkan gambar snake
def draw_snake(snake_block, snake_List):
    for x in snake_List:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block])

# Membuat button yang dapat diklik
def button(msg, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(dis, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(dis, inactive_color, (x, y, w, h))

    small_text = pygame.font.SysFont("bahnschrift", 20)
    text_surf = small_text.render(msg, True, black)
    text_rect = text_surf.get_rect(center=((x + (w / 2)), (y + (h / 2))))
    dis.blit(text_surf, text_rect)

# Fungsi untuk keluar dari permainan
def quit_game():
    pygame.quit()

# Membuat animasi loading bar
async def loading_screen():
    loading = True
    load_width = 0
    load_speed = 10
    max_width = 523
    while loading and load_width <= max_width:
        dis.fill(green_bg)
        dis.blit(loading_image, (dis_width // 2 - 261, dis_height // 2 - 56.5))
        pygame.draw.rect(dis, green, (dis_width // 2 - 261, dis_height // 2 - 56.5, load_width, 113))

        percent = (load_width / max_width) * 100
        percent_text = font_style.render(f"{int(percent)}%", True, white)
        dis.blit(percent_text, (dis_width // 2 - 20, dis_height // 2 + 70))

        load_width += load_speed
        pygame.display.update()
        await asyncio.sleep(0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loading = False
                quit_game()
                return
    await asyncio.sleep(0.5)

async def gameLoop():
    game_over = False
    game_close = False

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    food_positions = []
    trap_positions = []

    def reset_food_and_traps():
        food_positions.clear()
        trap_positions.clear()
        for _ in range(3):
            foodx = round(random.randrange(border_thickness + snake_block, dis_width - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            foody = round(random.randrange(border_thickness + snake_block, dis_height - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            food_positions.append([foodx, foody])

        for _ in range(15):
            trapx = round(random.randrange(border_thickness + snake_block, dis_width - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            trapy = round(random.randrange(border_thickness + snake_block, dis_height - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            trap_positions.append([trapx, trapy])

    reset_food_and_traps()

    direction = None
    level = 1
    score = 0
    snake_speed = initial_speed

    restart_requested = False

    while not game_over:

        while game_close:
            dis.blit(bg_over, (0, 0))

            button("Try Again", 193, 392, 100, 35, yellow, yellow, lambda: None)
            button("Exit", 515, 392, 100, 35, yellow, yellow, lambda: None)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if 193 < mx < 293 and 392 < my < 427:
                        restart_requested = True
                        game_close = False
                        game_over = True
                    elif 515 < mx < 615 and 392 < my < 427:
                        quit_game()
                        return

            await asyncio.sleep(0)

        if restart_requested:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != 'RIGHT':
                    x1_change = -snake_block
                    y1_change = 0
                    direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                    x1_change = snake_block
                    y1_change = 0
                    direction = 'RIGHT'
                elif event.key == pygame.K_UP and direction != 'DOWN':
                    y1_change = -snake_block
                    x1_change = 0
                    direction = 'UP'
                elif event.key == pygame.K_DOWN and direction != 'UP':
                    y1_change = snake_block
                    x1_change = 0
                    direction = 'DOWN'

        if x1 < border_thickness or x1 >= dis_width - snake_block - border_thickness or y1 < border_thickness or y1 >= dis_height - snake_block - border_thickness:
            sfx_over.play()
            game_close = True

        x1 += x1_change
        y1 += y1_change
        dis.fill(green_bg)

        pygame.draw.rect(dis, black, [0, 0, dis_width, dis_height], border_thickness)

        for pos in food_positions:
            pygame.draw.rect(dis, green, [pos[0], pos[1], snake_block, snake_block])

        for pos in trap_positions:
            pygame.draw.rect(dis, red, [pos[0], pos[1], snake_block, snake_block])

        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                sfx_over.play()
                game_close = True

        draw_snake(snake_block, snake_List)
        display_score(score)
        level_display(level)

        pygame.display.update()

        for pos in food_positions:
            if x1 == pos[0] and y1 == pos[1]:
                Length_of_snake += 1
                score += 1
                sfx_food.play()
                reset_food_and_traps()

                if score % 5 == 0:
                    level += 1
                    snake_speed += 3

        for pos in trap_positions:
            if x1 == pos[0] and y1 == pos[1]:
                Length_of_snake -= 1
                if Length_of_snake < 1:
                    sfx_over.play()
                    game_close = True
                else:
                    snake_List.pop(0)
                    sfx_trap.play()
                reset_food_and_traps()

        clock.tick(snake_speed)
        await asyncio.sleep(0)

    if restart_requested:
        await start_game()

# Memulai permainan dengan animasi loading
async def start_game():
    await loading_screen()
    await gameLoop()

async def main():
    menu = True
    while menu:
        dis.blit(bg_start, (0, 0))
        dis.blit(itg_logo, (0, 0))

        button("Start", 217, 388, 100, 35, yellow, yellow, lambda: None)
        button("Exit", 491, 388, 100, 35, yellow, yellow, lambda: None)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                quit_game()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if 217 < mx < 317 and 388 < my < 423:
                    menu = False
                    await start_game()
                    return
                elif 491 < mx < 591 and 388 < my < 423:
                    menu = False
                    quit_game()
                    return

        await asyncio.sleep(0)

asyncio.run(main())
