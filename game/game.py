import pygame
import sys
import os
import random 
from player import Player
from enemy import BasicEnemy, StrongEnemy
from cloud import Cloud 
from satellite import Satellite

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Invasión Espacial")

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 64)

        self.current_level = 1
        self.max_levels = 3
        self.level_background = None
        self.load_level_background()

        self.player = Player(self.screen_width // 2, self.screen_height - 70)
        self.enemies = []
        self.create_enemies()

        self.score = 0
        self.game_over = False
        self.enemy_direction = 1
        self.enemy_speed_increase = 0.5
        self.enemy_move_timer = 0
        self.enemy_move_interval = 15

        self.clouds = []
        self.cloud_spawn_timer = 0
        self.cloud_spawn_interval = 60

        self.satellites = []
        self.satellite_spawn_timer = 0
        self.satellite_spawn_interval_min = 240
        self.satellite_spawn_interval_max = 480
        self.next_satellite_spawn_interval = random.randint(self.satellite_spawn_interval_min, self.satellite_spawn_interval_max)

        self.paused = False
        self.pause_menu_state = "main"  
        self.pause_buttons = []
        self.game_over_buttons = []

    def load_level_background(self):
        if 1 <= self.current_level <= self.max_levels:
            base_path = os.path.dirname(__file__)
            image_name = f'lvl{self.current_level}.png'
            image_path = os.path.join(base_path, '..', 'images', image_name)
            image_path = os.path.abspath(image_path)

            print(f"Cargando fondo del nivel {self.current_level} desde: {image_path}")

            try:
                self.level_background = pygame.image.load(image_path).convert()
                self.level_background = pygame.transform.scale(self.level_background, (self.screen_width, self.screen_height))
            except pygame.error as e:
                print(f"Error al cargar la imagen de fondo {image_name}: {e}")
                self.level_background = None
        else:
            self.level_background = None

    def create_enemies(self):
        self.enemies = []

        base_enemy_speed = 4 + (self.current_level - 1) * 2
        bullet_speed = 3 + (self.current_level - 1) * 2

        if self.current_level == 1:
            for i in range(12):
                x = 100 + (i % 6) * 90
                y = 50 + (i // 6) * 75
                enemy = BasicEnemy(x, y, bullet_speed, level=self.current_level)  # Nivel pasado correctamente
                enemy.speed = base_enemy_speed
                self.enemies.append(enemy)

        elif self.current_level == 2:
            for i in range(6):
                x = 100 + (i % 6) * 90
                y = 50
                enemy = BasicEnemy(x, y, bullet_speed, level=self.current_level)
                enemy.speed = base_enemy_speed
                self.enemies.append(enemy)

            for i in range(6):
                x = 100 + (i % 6) * 90
                y = 140
                enemy = StrongEnemy(x, y, bullet_speed, level=self.current_level)  # Nivel pasado correctamente
                enemy.speed = base_enemy_speed
                self.enemies.append(enemy)

        else:
            for row in range(5):
                for col in range(3):
                    enemy = BasicEnemy(100 + row * 90, 50 + col * 75, bullet_speed, level=self.current_level)
                    enemy.speed = base_enemy_speed
                    self.enemies.append(enemy)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                    self.player.shoot()
                if event.key == pygame.K_ESCAPE and not self.game_over:
                    if self.paused and self.pause_menu_state == "options":
                        self.pause_menu_state = "main"
                    else:
                        self.paused = not self.paused
                        self.pause_menu_state = "main"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.paused and not self.game_over:
                    for i, btn_rect in enumerate(self.pause_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if self.pause_menu_state == "main":
                                if i == 0:
                                    self.resume_game()
                                elif i == 1:
                                    self.show_options()
                                elif i == 2:
                                    self.go_to_menu()
                                elif i == 3:
                                    self.quit_game()
                            elif self.pause_menu_state == "options":
                                if i == 2:
                                    self.back_to_pause_main()
                elif self.game_over:
                    for i, btn_rect in enumerate(self.game_over_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if i == 0:
                                self.__init__()
                            elif i == 1:
                                self.go_to_menu()
                            elif i == 2:
                                self.quit_game()

    def update(self):
        if self.game_over or self.paused:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left", self.screen_width)
        if keys[pygame.K_RIGHT]:
            self.player.move("right", self.screen_width)

        self.player.update(self.screen_height)

        self.enemy_move_timer += 1
        if self.enemy_move_timer >= self.enemy_move_interval:
            self.enemy_move_timer = 0

            hit_edge = False
            for enemy in self.enemies:
                enemy.rect.x += enemy.speed * enemy.direction
                enemy.try_shoot()
                if enemy.rect.right >= self.screen_width or enemy.rect.left <= 0:
                    hit_edge = True

            if hit_edge:
                for enemy in self.enemies:
                    enemy.direction *= -1
                    enemy.rect.y += enemy.move_down_distance

        for enemy in self.enemies:
            enemy.update_bullets(self.screen_height)

        self.check_collisions()

        if self.current_level == 2:
            self.cloud_spawn_timer += 1
            if self.cloud_spawn_timer >= self.cloud_spawn_interval:
                self.clouds.append(Cloud(self.screen_width, self.screen_height))
                self.cloud_spawn_timer = 0
            for cloud in self.clouds[:]:
                cloud.update()
                if cloud.is_offscreen(self.screen_height):
                    self.clouds.remove(cloud)
        else:
            self.clouds = []

        if self.current_level == 3:
            self.satellite_spawn_timer += 1
            if self.satellite_spawn_timer >= self.next_satellite_spawn_interval:
                self.satellites.append(Satellite(self.screen_width, self.screen_height))
                self.satellite_spawn_timer = 0
                self.next_satellite_spawn_interval = random.randint(self.satellite_spawn_interval_min, self.satellite_spawn_interval_max)
            for satellite in self.satellites[:]:
                satellite.update()
                if satellite.is_offscreen(self.screen_width):
                    self.satellites.remove(satellite)
        else:
            self.satellites = []

        if not self.enemies:
            self.current_level += 1
            if self.current_level <= self.max_levels:
                print(f"¡Pasando al Nivel {self.current_level}!")
                self.load_level_background()
                self.create_enemies()
                for enemy in self.enemies:
                    enemy.speed += self.enemy_speed_increase
            else:
                print("¡Has completado todos los niveles!")
                self.game_over = True

        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break

    def check_collisions(self):
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.colliderect(enemy.rect):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy in self.enemies:
                        enemy.receive_damage()
                        if enemy.dead:
                            self.enemies.remove(enemy)
                            self.score += 10
                        else:
                            self.score += 5
                    break

        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if bullet.colliderect(self.player.rect):
                    enemy.bullets.remove(bullet)
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                    break

    def draw_button(self, text, x, y, w=250, h=60, 
                    bg_color=(0, 0, 255), text_color=(255, 255, 255), border_color=(0, 255, 0), 
                    hover_bg_color=(0, 100, 255), hover_text_color=(255, 255, 0)):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)

        mouse_pos = pygame.mouse.get_pos()

        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, hover_bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, hover_text_color)
        else:
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, text_color)

        text_rect = rendered_text.get_rect(center=rect.center)
        self.screen.blit(rendered_text, text_rect)

        return rect

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSA", True, (255, 255, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))

        if self.pause_menu_state == "main":
            continue_btn = self.draw_button("Continuar", self.screen_width//2, 250, 250, 60)
            options_btn = self.draw_button("Opciones", self.screen_width//2, 330, 250, 60)
            menu_btn = self.draw_button("Menú principal", self.screen_width//2, 410, 250, 60)
            quit_btn = self.draw_button("Salir", self.screen_width//2, 490, 250, 60)
            self.pause_buttons = [continue_btn, options_btn, menu_btn, quit_btn]

        elif self.pause_menu_state == "options":
            controls_btn = self.draw_button("Controles", self.screen_width//2, 270, 250, 60)
            sound_btn = self.draw_button("Sonido", self.screen_width//2, 350, 250, 60)
            back_btn = self.draw_button("Volver", self.screen_width//2, 430, 250, 60)
            self.pause_buttons = [controls_btn, sound_btn, back_btn]

    def resume_game(self):
        self.paused = False

    def show_options(self):
        self.pause_menu_state = "options"

    def back_to_pause_main(self):
        self.pause_menu_state = "main"

    def go_to_menu(self):
        from menu import Menu
        menu = Menu()
        menu.run()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def draw_game_over_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        score_text = self.font.render(f"Puntaje: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 180))

        restart_btn = self.draw_button("Reiniciar", self.screen_width // 2, 300)
        menu_btn = self.draw_button("Menú principal", self.screen_width // 2, 380)
        quit_btn = self.draw_button("Salir", self.screen_width // 2, 460)

        self.game_over_buttons = [restart_btn, menu_btn, quit_btn]

    def draw(self):
        if self.level_background:
            self.screen.blit(self.level_background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        if self.current_level == 2:
            for cloud in self.clouds:
                cloud.draw(self.screen)

        if self.current_level == 3:
            for satellite in self.satellites:
                satellite.draw(self.screen)

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.player.bullets:
            pygame.draw.rect(self.screen, (255, 255, 0), bullet)

        for enemy in self.enemies:
            for bullet in enemy.bullets:
                pygame.draw.rect(self.screen, (255, 0, 0), bullet)

        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, (255, 255, 255))
        score_text = self.font.render(f"Puntaje: {self.score}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, 10))

        if self.paused:
            self.draw_pause_menu()
        if self.game_over:
            self.draw_game_over_menu()

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
