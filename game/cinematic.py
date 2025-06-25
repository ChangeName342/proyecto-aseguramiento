import sys
import pygame
import os
import time

class Cinematics:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.get_surface()
        self.images = []
        self.current_image = None
        self.alpha = 255  # Para efectos de desvanecimiento
        self.fade_speed = 5  # Velocidad del desvanecimiento
        
        # Cargar imágenes de cinemáticas
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.intro_images = [
            os.path.join(BASE_DIR, 'images', 'cinematic_1.png'),
            os.path.join(BASE_DIR, 'images', 'cinematic_2.png')
        ]
        self.loser_image = os.path.join(BASE_DIR, 'images', 'cinematic_loser.png')
        self.win_image = os.path.join(BASE_DIR, 'images', 'cinematic_win.png')
        
        # Precargar imágenes de introducción
        self.loaded_intro_images = []
        for path in self.intro_images:
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                self.loaded_intro_images.append(img)
            except Exception as e:
                print(f"Error cargando imagen de cinemática: {path} - {e}")
                # Crear una imagen de relleno si falta alguna
                placeholder = pygame.Surface((self.screen_width, self.screen_height))
                placeholder.fill((0, 0, 0))
                self.loaded_intro_images.append(placeholder)
        
        # Precargar imágenes de final
        self.loaded_loser_image = self._load_final_image(self.loser_image, (255, 0, 0))  # Rojo para derrota
        self.loaded_win_image = self._load_final_image(self.win_image, (0, 255, 0))     # Verde para victoria

    def _load_final_image(self, path, fill_color):
        """Carga una imagen de final con manejo de errores"""
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (self.screen_width, self.screen_height))
        except Exception as e:
            print(f"Error cargando imagen de final {path}: {e}")
            placeholder = pygame.Surface((self.screen_width, self.screen_height))
            placeholder.fill(fill_color)
            return placeholder

    def show_intro(self):
        """Muestra solo las 2 primeras imágenes antes del primer nivel"""
        for img in self.loaded_intro_images[:2]:  # Solo las primeras dos imágenes
            self.current_image = img
            self.alpha = 0  # Comenzar transparente
            
            # Efecto de aparición (2 segundos)
            for _ in range(0, 255, self.fade_speed):
                if self._handle_events():  # Si devuelve True, el usuario quiere saltar
                    return
                self.current_image.set_alpha(self.alpha)
                self.screen.fill((0, 0, 0))
                self.screen.blit(self.current_image, (0, 0))
                pygame.display.flip()
                self.alpha += self.fade_speed
                pygame.time.delay(30)
            
            # Mostrar imagen por 2 segundos
            start_time = time.time()
            while time.time() - start_time < 2:
                if self._handle_events():  # Permitir saltar
                    return
                self.screen.blit(self.current_image, (0, 0))
                pygame.display.flip()
                pygame.time.delay(30)
            
            # Efecto de desvanecimiento (2 segundos)
            for _ in range(255, 0, -self.fade_speed):
                if self._handle_events():  # Permitir saltar
                    return
                self.current_image.set_alpha(self.alpha)
                self.screen.fill((0, 0, 0))
                self.screen.blit(self.current_image, (0, 0))
                pygame.display.flip()
                self.alpha -= self.fade_speed
                pygame.time.delay(30)

    def show_ending(self, victory=False):
        """Muestra la cinemática final correspondiente"""
        self.current_image = self.loaded_win_image if victory else self.loaded_loser_image
        self.alpha = 0
        
        # Efecto de aparición (3 segundos)
        for _ in range(0, 255, self.fade_speed):
            if self._handle_events():  # Permitir saltar
                return
            self.current_image.set_alpha(self.alpha)
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.current_image, (0, 0))
            pygame.display.flip()
            self.alpha += self.fade_speed
            pygame.time.delay(30)
        
        # Mostrar imagen por 3 segundos
        start_time = time.time()
        while time.time() - start_time < 3:
            if self._handle_events():  # Permitir saltar
                return
            self.screen.blit(self.current_image, (0, 0))
            pygame.display.flip()
            pygame.time.delay(30)
        
        # Efecto de desvanecimiento (3 segundos)
        for _ in range(255, 0, -self.fade_speed):
            if self._handle_events():  # Permitir saltar
                return
            self.current_image.set_alpha(self.alpha)
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.current_image, (0, 0))
            pygame.display.flip()
            self.alpha -= self.fade_speed
            pygame.time.delay(30)

    def _handle_events(self):
        """Maneja eventos durante las cinemáticas"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return True  # Permite saltar la cinemática
        return False