import pygame
import sys
import os
import random 
from player import Player
from enemy import BasicEnemy, StrongEnemy, FinalBoss
from cloud import Cloud 
from satellite import Satellite
from shield import Shield

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
        self.shields = []
        self.paused = False
        self.pause_menu_state = "main"  
        self.pause_buttons = []
        self.game_over_buttons = []

        # Para menú de victoria
        self.victory = False
        self.victory_buttons = []

        # Ruta para archivo de guardado
        base_path = os.path.dirname(__file__)
        self.save_path = os.path.join(base_path, '..', 'savegame.txt')

         # Inicializar mixer y cargar sonido de clic
        try:
            pygame.mixer.init()
            click_sound_path = os.path.join(base_path, '..', 'sounds', 'eleccion_menu.mp3')
            self.click_sound = pygame.mixer.Sound(click_sound_path)
            self.click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error cargando sonido de elección de menú: {e}")
            self.click_sound = None

        # Sonido de pasar mouse sobre botones del menú de pausa
        self.hover_sound = None
        self.hovered_pause_buttons = set()
        try:
            base_path = os.path.dirname(__file__)
            hover_sound_path = os.path.join(base_path, '..', 'sounds', 'seleccionar_menu.mp3')
            self.hover_sound = pygame.mixer.Sound(hover_sound_path)
            self.hover_sound.set_volume(0.5)
        except Exception as e:  
            print(f"Error cargando sonido de selección de pausa: {e}")

        # Reproducir la música del nivel actual al iniciar
        self.play_level_music()

    def play_level_music(self):
        base_path = os.path.dirname(__file__)
        try:
            pygame.mixer.music.stop()  # Detener música anterior
            if self.current_level == 1:
                music_path = os.path.join(base_path, '..', 'sounds', 'musica_nivel1.mp3')
            elif self.current_level == 2:
                music_path = os.path.join(base_path, '..', 'sounds', 'musica_nivel2.mp3')
            elif self.current_level == 3:
                music_path = os.path.join(base_path, '..', 'sounds', 'musica_jefe_final.mp3')
            else:
                return  # No reproducir música para otros niveles

            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # Loop infinito
        except Exception as e:
            print(f"Error cargando música de nivel: {e}")

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
                enemy = BasicEnemy(x, y, bullet_speed, level=self.current_level)
                enemy.speed = base_enemy_speed
                self.enemies.append(enemy)

        elif self.current_level == 2:
            positions = []

            y1 = 60
            count1 = random.randint(4, 8)
            spacing1 = (self.screen_width - 100) // (count1 + 1)
            for i in range(count1):
                x = 50 + (i + 1) * spacing1
                positions.append((x, y1))

            y2 = 150
            count2 = 12 - count1
            spacing2 = (self.screen_width - 100) // (count2 + 1)
            for i in range(count2):
                x = 50 + (i + 1) * spacing2
                positions.append((x, y2))

            random.shuffle(positions) 

            for i, (x, y) in enumerate(positions):
                if i < 6:
                    enemy = BasicEnemy(x, y, bullet_speed, level=self.current_level)
                else:
                    enemy = StrongEnemy(x, y, bullet_speed, level=self.current_level)
                enemy.speed = base_enemy_speed
                self.enemies.append(enemy)

        elif self.current_level == 3:
            x = self.screen_width // 2 - 45  
            y = 50
            boss = FinalBoss(x, y, bullet_speed)
            self.enemies.append(boss)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.delete_save()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused and not self.victory:
                    self.player.shoot()
                if event.key == pygame.K_ESCAPE and not self.game_over and not self.victory:
                    if self.paused and self.pause_menu_state == "options":
                        self.pause_menu_state = "main"
                    else:
                        self.paused = not self.paused
                        self.pause_menu_state = "main"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.paused and not self.game_over and not self.victory:
                    for i, btn_rect in enumerate(self.pause_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()  # <-- Aquí suena al click
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
                            if self.click_sound:
                                self.click_sound.play()  # <-- Aquí también suena al click
                            if i == 0:
                                self.delete_save()
                                self.__init__()
                            elif i == 1:
                                self.delete_save()
                                self.go_to_menu()
                            elif i == 2:
                                self.delete_save()
                                self.quit_game()
                elif self.victory:
                    for i, btn_rect in enumerate(self.victory_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()  # <-- Aquí también suena al click
                            if i == 0:
                                self.delete_save()
                                self.go_to_menu()
                            elif i == 1:
                                self.delete_save()
                                self.quit_game()

    def update(self):
        if self.game_over or self.paused or self.victory:
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

        # Revisar si se eliminaron todos los enemigos para pasar de nivel
        if not self.enemies:
            self.current_level += 1
            if self.current_level <= self.max_levels:
                print(f"¡Pasando al Nivel {self.current_level}!")
                self.save_progress()  # Guardar progreso al pasar nivel
                self.load_level_background()
                self.create_enemies()
                if self.current_level in [2, 3]:
                    self.create_shields()
                for enemy in self.enemies:
                    enemy.speed += self.enemy_speed_increase

                # Reproducir música del nuevo nivel
                self.play_level_music()
            else:
                print("¡Has completado todos los niveles!")
                self.delete_save()  # Borrar progreso al ganar
                self.victory = True

        # Si algún enemigo toca al jugador, fin del juego
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                self.delete_save()  # Borrar progreso al perder
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
                for shield in self.shields:
                    if bullet.rect.colliderect(shield.rect):
                        enemy.bullets.remove(bullet)
                        shield.take_damage()
                        if shield.is_destroyed():
                            self.shields.remove(shield)
                        break

        # Colisión balas enemigas con jugador
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if bullet.rect.colliderect(self.player.rect) and self.player.damage_timer == 0:
                    enemy.bullets.remove(bullet)
                    self.player.take_damage()
                    if self.player.lives <= 0:
                        self.game_over = True
                        self.delete_save()
                    break

    def draw_button(self, text, x, y, w=250, h=60, 
                    bg_color=(0, 0, 255), text_color=(255, 255, 255), border_color=(0, 255, 0), 
                    hover_bg_color=(0, 100, 255), hover_text_color=(255, 255, 0)):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)

        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        # Sonido de hover
        if hovered and text not in self.hovered_pause_buttons:
            self.hovered_pause_buttons.add(text)
            if self.hover_sound:
                self.hover_sound.play()
        elif not hovered:
            self.hovered_pause_buttons.discard(text)

        if hovered:
            pygame.draw.rect(self.screen, hover_bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, hover_text_color)
        else:
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = self.font.render(text, True, text_color)

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

    def create_shields(self):
        self.shields = []
        shield_y = self.screen_height - 150
        spacing = self.screen_width // 4
        for i in range(3):
            shield_x = spacing * i + spacing // 2 - 30
            self.shields.append(Shield(shield_x, shield_y))

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

    def draw_victory_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("¡VICTORIA!", True, (0, 255, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        msg_text = self.font.render("¡Salvaste el planeta!", True, (255, 255, 255))
        self.screen.blit(msg_text, (self.screen_width // 2 - msg_text.get_width() // 2, 180))

        menu_btn = self.draw_button("Menú principal", self.screen_width // 2, 300)
        quit_btn = self.draw_button("Salir", self.screen_width // 2, 380)

        self.victory_buttons = [menu_btn, quit_btn]

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

        # Barra de vida para el jefe final en nivel 3
        for enemy in self.enemies:
            if isinstance(enemy, FinalBoss):
                health_bar_width = enemy.rect.width
                health_bar_height = 10
                health_ratio = max(enemy.lives / 15, 0)  # 15 es vida total del jefe
                pygame.draw.rect(self.screen, (255, 0, 0), (enemy.rect.x, enemy.rect.y - 15, health_bar_width, health_bar_height))
                health_bar = pygame.Rect(enemy.rect.x, enemy.rect.y - 15, int(health_bar_width * health_ratio), health_bar_height)
                pygame.draw.rect(self.screen, (0, 255, 0), health_bar)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.player.bullets:
            pygame.draw.rect(self.screen, (255, 255, 0), bullet)

        for enemy in self.enemies:
            for bullet in enemy.bullets:
                if hasattr(bullet, "draw"):
                    bullet.draw(self.screen)
                else:
                    pygame.draw.rect(self.screen, (255, 0, 0), bullet)

        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, (255, 255, 255))
        score_text = self.font.render(f"Puntaje: {self.score}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, 10))

        for shield in self.shields:
            shield.draw(self.screen)

        if self.paused:
            self.draw_pause_menu()
        if self.game_over:
            self.draw_game_over_menu()
        if self.victory:
            self.draw_victory_menu()

    def save_progress(self):
        try:
            with open(self.save_path, 'w') as f:
                f.write(str(self.current_level))
            print(f"Progreso guardado: Nivel {self.current_level}")
        except Exception as e:
            print(f"Error guardando progreso: {e}")

    def delete_save(self):
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
                print("Progreso eliminado")
        except Exception as e:
            print(f"Error eliminando progreso: {e}")

    def run(self):
        while True:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()


