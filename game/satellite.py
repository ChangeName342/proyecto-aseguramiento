import pygame
import os
import random

class Satellite:
    def __init__(self, screen_width, screen_height):
        base_path = os.path.dirname(__file__)
        image_path = os.path.join(base_path, '..', 'images', 'satelite1.png')
        image_path = os.path.abspath(image_path)

        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            # Escalar el satélite a un tamaño razonable, puedes ajustar esto
            self.image = pygame.transform.scale(self.image, (random.randint(60, 100), random.randint(40, 70)))
            # Opcional: Voltear horizontalmente algunas veces para más variedad
            if random.random() < 0.5:
                self.image = pygame.transform.flip(self.image, True, False)
        except Exception as e:
            print(f"Error cargando imagen de satélite: {image_path} - {e}")
            self.image = pygame.Surface((80, 50)) # Fallback
            self.image.fill((150, 150, 150)) # Gris oscuro para el satélite de fallback

        self.rect = self.image.get_rect()
        
        # Posición inicial aleatoria en el lado izquierdo, fuera de pantalla
        # y a una altura aleatoria en la mitad superior de la pantalla
        self.rect.x = random.randint(-self.rect.width, -20)
        self.rect.y = random.randint(50, screen_height // 2 - self.rect.height) # Ajusta el rango Y según prefieras

        self.speed = random.randint(2, 4) # Velocidad de movimiento aleatoria

    def update(self):
        self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_offscreen(self, screen_width):
        return self.rect.left > screen_width