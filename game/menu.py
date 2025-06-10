import pygame
import sys
import os
import gif_pygame

class Menu:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Menú Principal - Invasión Espacial")

        # Ruta base para cargar recursos (GIF y título)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        gif_path = os.path.join(BASE_DIR, 'images', 'fondo_menu.gif')
        self.background_gif = gif_pygame.load(gif_path)
        self.title = pygame.image.load(os.path.join(BASE_DIR, 'images', 'titulo.png')).convert_alpha()

        # Fuentes para textos y botones
        self.font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 30)

        self.clock = pygame.time.Clock()

        # Estado actual del menú ("menu", "options", "sound", "controls")
        self.state = "menu"

        # Control de volumen (pendiente implementación)
        self.volume = 0.5
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)

    def draw_button(self, text, x, y, font, mouse_pos, w=250, h=60,
                    bg_color=(0, 0, 255), text_color=(255, 255, 255), border_color=(0, 255, 0),
                    hover_bg_color=(0, 100, 255), hover_text_color=(255, 255, 0)):
        """Dibuja un botón con efecto hover y retorna su rect para detectar clics."""
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)

        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, hover_bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = font.render(text, True, hover_text_color)
        else:
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            rendered_text = font.render(text, True, text_color)

        text_rect = rendered_text.get_rect(center=rect.center)
        self.screen.blit(rendered_text, text_rect)
        return rect

    def draw_text(self, text, x, y, font, color=(255, 255, 255)):
        """Dibuja texto centrado en la pantalla."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_menu(self):
        """Dibuja el fondo animado y los botones según el estado actual."""
        # Fondo animado GIF escalado a la ventana
        frame_surface = self.background_gif.blit_ready()
        frame_surface = pygame.transform.scale(frame_surface, (self.screen_width, self.screen_height))
        self.screen.blit(frame_surface, (0, 0))

        # Título centrado horizontalmente
        self.screen.blit(self.title, (self.screen_width // 2 - self.title.get_width() // 2, 80))

        mouse_pos = pygame.mouse.get_pos()

        if self.state == "menu":
            play_button = self.draw_button("Iniciar Juego", 400, 250, self.font, mouse_pos)
            options_button = self.draw_button("Opciones", 400, 330, self.font, mouse_pos)
            quit_button = self.draw_button("Salir", 400, 410, self.font, mouse_pos)
            return play_button, options_button, quit_button

        elif self.state == "options":
            self.draw_text("Opciones", 400, 180, self.font)
            sound_button = self.draw_button("Sonido", 400, 260, self.small_font, mouse_pos, w=200, h=50)
            controls_button = self.draw_button("Controles", 400, 330, self.small_font, mouse_pos, w=200, h=50)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return sound_button, controls_button, back_button

        elif self.state == "sound":
            self.draw_text("Ajustes de Sonido (pendiente)", 400, 250, self.small_font)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return (back_button,)

        elif self.state == "controls":
            self.draw_text("Controles (pendiente)", 400, 250, self.small_font)
            back_button = self.draw_button("Volver", 400, 500, self.small_font, mouse_pos, w=200, h=40)
            return (back_button,)

    def run(self):
        """Bucle principal del menú que maneja eventos y cambia de estado."""
        while True:
            self.clock.tick(60)
            buttons = self.draw_menu()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == "menu":
                        if buttons[0].collidepoint(mouse_pos):  # Iniciar juego
                            from game import Game
                            game = Game()
                            game.run()
                        elif buttons[1].collidepoint(mouse_pos):  # Opciones
                            self.state = "options"
                        elif buttons[2].collidepoint(mouse_pos):  # Salir
                            pygame.quit()
                            sys.exit()

                    elif self.state == "options":
                        if buttons[0].collidepoint(mouse_pos):  # Sonido
                            self.state = "sound"
                        elif buttons[1].collidepoint(mouse_pos):  # Controles
                            self.state = "controls"
                        elif buttons[2].collidepoint(mouse_pos):  # Volver
                            self.state = "menu"

                    elif self.state in ("sound", "controls"):
                        if buttons[0].collidepoint(mouse_pos):  # Volver desde submenú
                            self.state = "options"


