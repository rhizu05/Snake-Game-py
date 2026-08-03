import pygame
import time
import random

pygame.init()
pygame.mixer.init()

# Image Background
bg_over = pygame.image.load('resource/bg-over.png')
bg_start = pygame.image.load('resource/bg-start.png')
bg_intro = pygame.image.load('resource/bg-intro.png')
icon_image = pygame.image.load('resource/logo-putih-ITG.png')
itg_logo = pygame.transform.scale(icon_image, (100, 100)) 

# Efek Suara
sfx_food = pygame.mixer.Sound('resource/eat_food.ogg')
sfx_trap = pygame.mixer.Sound('resource/eat_trap.ogg')
sfx_over = pygame.mixer.Sound('resource/gameover.ogg')

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
loading_image = pygame.image.load('resource/loading.png')

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

# Memulai permainan dengan animasi loading
def start_game():
    loading_screen()
    gameLoop()

# Fungsi untuk keluar dari permainan
def quit_game():
    pygame.quit()
    quit()

# Membuat animasi loading bar
def loading_screen():
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
        time.sleep(0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loading = False
                quit_game()
    time.sleep(0.5)

def gameLoop():
    # Fungsi utama yang menjalankan game loop.
    game_over = False
    game_close = False

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1 # Panjang blok ular saat awal permainan

    def reset_food_and_traps():
        # Fungsi untuk mengatur ulang posisi makanan dan jebakan.
        food_positions.clear()
        trap_positions.clear()
        for _ in range(3):  # Jumlah makanan 3
            foodx = round(random.randrange(border_thickness + snake_block, dis_width - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            foody = round(random.randrange(border_thickness + snake_block, dis_height - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            food_positions.append([foodx, foody])
    
        for _ in range(15):  # Jumlah jebakan 15
            trapx = round(random.randrange(border_thickness + snake_block, dis_width - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            trapy = round(random.randrange(border_thickness + snake_block, dis_height - snake_block - border_thickness - snake_block) / 20.0) * 20.0
            trap_positions.append([trapx, trapy])


    food_positions = []
    trap_positions = []
    reset_food_and_traps()

    direction = None
    level = 1 # Level awal permainan
    score = 0 # Skor awal permainan
    snake_speed = initial_speed

    while not game_over:

        # Tampilan pada Game over
        while game_close:  
            dis.blit(bg_over, (0, 0))

            button("Try Again", 193, 392, 100, 35, yellow, yellow, start_game)
            button("Exit", 515, 392, 100, 35, yellow, yellow, quit_game)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

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

        # Memastikan snake mati jika menabrak bingkai
        if x1 < border_thickness or x1 >= dis_width - snake_block - border_thickness or y1 < border_thickness or y1 >= dis_height - snake_block - border_thickness:
            sfx_over.play()
            game_close = True

        
        x1 += x1_change
        y1 += y1_change
        dis.fill(green_bg)

        # Gambar bingkai
        pygame.draw.rect(dis, black, [0, 0, dis_width, dis_height], border_thickness)

        
        # Gambar makanan
        for pos in food_positions:
            pygame.draw.rect(dis, green, [pos[0], pos[1], snake_block, snake_block])
        
        # Gambar jebakan
        for pos in trap_positions:
            pygame.draw.rect(dis, red, [pos[0], pos[1], snake_block, snake_block])
        
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Ular mati ketika menabrak badannya
        for x in snake_List[:-1]:
            if x == snake_Head:
                sfx_over.play()
                game_close = True

        draw_snake(snake_block, snake_List)
        display_score(score)
        level_display(level)

        pygame.display.update()

        # Bagian ini yang menambah panjang ular ketika memakan makanan
        for pos in food_positions:
            
            if x1 == pos[0] and y1 == pos[1]:
                # push ke stack (tambah panjang ular)
                Length_of_snake += 1 # Tambah panjang ular
                score += 1 # Tambah skor
                sfx_food.play() # Menambah sfx
                reset_food_and_traps()  # Perbarui posisi makanan dan jebakan

                if score % 5 == 0:
                    level += 1 # Tambahkan level ketika skor kelipatan 5
                    snake_speed += 3  # Tambahkan kecepatan snake setiap kali level naik

        # Bagian ini yang mengurangi panjang ular ketika memakan jebakan
        for pos in trap_positions:
            
            if x1 == pos[0] and y1 == pos[1]:
                # pop dari stack (kurangi panjang ular)
                Length_of_snake -= 1 # Kurang panjang ular
                if Length_of_snake < 1: # Jika ular memakan trap ketika panjang ular kurang dari 1
                    sfx_over.play() # Menambah sfx
                    game_close = True
                else:
                    snake_List.pop(0) # Hapus elemen pertama dari stack (ular)
                    sfx_trap.play() # Menambah sfx
                reset_food_and_traps()  # Perbarui posisi makanan dan jebakan

        clock.tick(snake_speed)

    pygame.quit()
    quit()

def start_menu():
    # Fungsi untuk menampilkan menu start.
    menu = True
    while menu:
        dis.blit(bg_start, (0, 0))
        dis.blit(itg_logo, (0, 0))


        button("Start", 217, 388, 100, 35, yellow, yellow, start_game)
        button("Exit", 491, 388, 100, 35, yellow, yellow, quit_game)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                quit_game()

start_menu()  # Menampilkan menu start
