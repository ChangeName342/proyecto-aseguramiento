import pygame
import sys
import os # ### CAMBIOS APLICADOS ### Importar el módulo os
from player import Player
from enemy import Enemy

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

        # ### CAMBIOS APLICADOS ### Nuevas variables para el control de niveles y fondos
        self.current_level = 1 # Empieza en el nivel 1
        self.max_levels = 3 # Define el número máximo de niveles (lvl1, lvl2, lvl3)
        self.level_background = None # Variable para almacenar la imagen del fondo del nivel
        self.load_level_background() # Carga el fondo del nivel inicial

        # Instancia jugador y crea enemigos iniciales
        self.player = Player(self.screen_width // 2, self.screen_height - 70)
        self.enemies = []
        self.create_enemies() # Llama a la creación de enemigos para el nivel 1

        self.score = 0
        self.game_over = False
        self.enemy_direction = 1
        self.enemy_speed_increase = 0.5
        self.enemy_move_timer = 0
        self.enemy_move_interval = 15  # Controla frecuencia de movimiento de enemigos

        # Variables para pausa y estado de menús
        self.paused = False
        self.pause_menu_state = "main"  
        self.pause_buttons = []  # Rectángulos de botones en menú pausa
        self.game_over_buttons = []  # Rectángulos de botones en menú game over

    # ### CAMBIOS APLICADOS ### Nueva función para cargar el fondo del nivel
    def load_level_background(self):
        """Carga la imagen de fondo para el nivel actual."""
        if 1 <= self.current_level <= self.max_levels:
            # Construye la ruta de la imagen, subiendo una carpeta y entrando en 'images'
            base_path = os.path.dirname(__file__) # Esto es 'game/'
            image_name = f'lvl{self.current_level}.png'
            image_path = os.path.join(base_path, '..', 'images', image_name)
            image_path = os.path.abspath(image_path) # Asegurarse de tener la ruta absoluta

            print(f"Cargando fondo del nivel {self.current_level} desde: {image_path}") # Debug

            try:
                # Usa .convert() si las imágenes no tienen transparencia, .convert_alpha() si sí la tienen.
                self.level_background = pygame.image.load(image_path).convert()
                # Escalar la imagen al tamaño de la pantalla
                self.level_background = pygame.transform.scale(self.level_background, (self.screen_width, self.screen_height))
            except pygame.error as e:
                print(f"Error al cargar la imagen de fondo {image_name}: {e}")
                self.level_background = None # Establecer a None si falla la carga
        else:
            self.level_background = None # Si el nivel excede max_levels, no hay fondo específico

    def create_enemies(self):
        # Genera una cuadrícula de enemigos
        self.enemies = [] # ### CAMBIOS APLICADOS ### Limpia la lista de enemigos antes de crear nuevos
        for row in range(5):
            for col in range(3):
                enemy = Enemy(100 + row * 90, 50 + col * 75)
                self.enemies.append(enemy)

    def handle_events(self):
        # Procesa eventos del sistema y del usuario
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                    self.player.shoot()
                # Manejo de pausa y navegación en menú pausa
                if event.key == pygame.K_ESCAPE and not self.game_over:
                    if self.paused and self.pause_menu_state == "options":
                        self.pause_menu_state = "main"
                    else:
                        self.paused = not self.paused
                        self.pause_menu_state = "main"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Interacción con botones en menú pausa
                if self.paused and not self.game_over:
                    for i, btn_rect in enumerate(self.pause_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if self.pause_menu_state == "main":
                                if i == 0:  # Continuar juego
                                    self.resume_game()
                                elif i == 1:  # Mostrar opciones
                                    self.show_options()
                                elif i == 2:  # Ir al menú principal
                                    self.go_to_menu()
                                elif i == 3:  # Salir del juego
                                    self.quit_game()
                            elif self.pause_menu_state == "options":
                                if i == 2:  # Volver al menú pausa principal
                                    self.back_to_pause_main()

                # Interacción con botones en menú de game over
                elif self.game_over:
                    for i, btn_rect in enumerate(self.game_over_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if i == 0:  # Reiniciar juego
                                # ### CAMBIOS APLICADOS ### Asegurarse de re-inicializar el nivel y el fondo
                                self.__init__() # Reinicia el juego, lo que también carga el nivel 1 y su fondo
                            elif i == 1:  # Ir al menú principal
                                self.go_to_menu()
                            elif i == 2:  # Salir del juego
                                self.quit_game()

    def update(self):
        # Evita actualizar si el juego está pausado o terminado
        if self.game_over or self.paused:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left", self.screen_width)
        if keys[pygame.K_RIGHT]:
            self.player.move("right", self.screen_width)

        self.player.update(self.screen_height)

        # Controla el movimiento sincronizado de enemigos y su dirección
        self.enemy_move_timer += 1
        if self.enemy_move_timer >= self.enemy_move_interval:
            self.enemy_move_timer = 0
            any_enemy_hit_edge = False
            for enemy in self.enemies:
                # Pasa la dirección del enemigo para que pueda girar al llegar al borde
                if enemy.update(self.screen_width): # El update del enemigo ahora devuelve si tocó borde
                    any_enemy_hit_edge = True
                enemy.try_shoot()
            if any_enemy_hit_edge:
                for enemy in self.enemies:
                    enemy.move_down()

        # Actualiza balas disparadas por enemigos
        for enemy in self.enemies:
            enemy.update_bullets(self.screen_height)

        self.check_collisions()

        # ### CAMBIOS APLICADOS ### Lógica para avanzar al siguiente nivel
        if not self.enemies: # Si no quedan enemigos
            self.current_level += 1 # Avanza al siguiente nivel
            if self.current_level <= self.max_levels:
                print(f"¡Pasando al Nivel {self.current_level}!") # Debug
                self.load_level_background() # Carga el nuevo fondo del nivel
                self.create_enemies() # Crea nuevos enemigos para el nuevo nivel

                # Opcional: Aumentar velocidad general o dificultad aquí para el nuevo nivel
                for enemy in self.enemies:
                    enemy.speed += self.enemy_speed_increase
            else:
                # El jugador ha superado todos los niveles
                print("¡Has completado todos los niveles!")
                self.game_over = True # O podrías redirigir a una pantalla de "Victoria"

        # Verifica si un enemigo llegó a la altura del jugador, termina juego
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break

    def check_collisions(self):
        # Detecta colisiones entre balas del jugador y enemigos
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.colliderect(enemy.rect):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.score += 10
                    break

        # Detecta colisiones entre balas enemigas y jugador
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
        # Dibuja un botón con colores que cambian si el mouse está encima
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

        return rect  # Retorna el rect para detectar clics

    def draw_pause_menu(self):
        # Fondo semitransparente y título para menú pausa
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSA", True, (255, 255, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))

        # Dibuja botones según el estado actual del menú pausa
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
        # Importa y ejecuta el menú principal (externo)
        from menu import Menu
        menu = Menu()
        menu.run()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def draw_game_over_menu(self):
        # Fondo semitransparente y título para menú game over
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
        # ### CAMBIOS APLICADOS ### Dibujar el fondo del nivel primero
        if self.level_background:
            self.screen.blit(self.level_background, (0, 0))
        else:
            # Fallback a un color sólido si la imagen de fondo no se cargó
            self.screen.fill((0, 0, 0))

        # Dibuja jugador, enemigos y balas
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Dibuja balas del jugador
        for bullet in self.player.bullets:
            pygame.draw.rect(self.screen, (255, 255, 0), bullet)

        # Dibuja balas de enemigos
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                pygame.draw.rect(self.screen, (255, 0, 0), bullet)

        # Dibuja vidas y puntaje
        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, (255, 255, 255))
        score_text = self.font.render(f"Puntaje: {self.score}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, 10))

        # Menús
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