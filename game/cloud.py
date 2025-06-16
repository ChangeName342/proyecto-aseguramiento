# game/cloud.py
import pygame
import os
import random

class Cloud:
    def __init__(self, screen_width, screen_height):
        # Cargar imágenes de nubes
        base_path = os.path.dirname(__file__)
        cloud_images_paths = [
            os.path.join(base_path, '..', 'images', 'nube1.png'),
            os.path.join(base_path, '..', 'images', 'nube2.png')
        ]

        # Elegir una imagen de nube aleatoriamente
        selected_image_path = random.choice(cloud_images_paths)
        
        try:
            self.image = pygame.image.load(selected_image_path).convert_alpha()
            # Escalar las nubes a un tamaño razonable, puedes ajustar esto
            self.image = pygame.transform.scale(self.image, (random.randint(100, 200), random.randint(50, 100))) 
        except Exception as e:
            print(f"Error cargando imagen de nube: {selected_image_path} - {e}")
            self.image = pygame.Surface((150, 75)) # Fallback
            self.image.fill((200, 200, 200)) # Gris para la nube de fallback

        self.rect = self.image.get_rect()
        
        # Posición inicial aleatoria en la parte superior, fuera de pantalla
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(-self.rect.height, -20) # Empieza un poco fuera de la pantalla

        self.speed = random.randint(1, 3) # Velocidad de caída aleatoria

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_offscreen(self, screen_height):
        return self.rect.top > screen_height