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
        
        # Posición inicial aleatoria en los laterales, fuera de pantalla
        if random.random() < 0.5: # 50% de probabilidad de aparecer por izquierda o derecha
            self.rect.x = -self.rect.width # Empieza fuera por izquierda
            self.direction = 1 # Se moverá hacia la derecha
        else:
            self.rect.x = screen_width # Empieza fuera por derecha
            self.direction = -1 # Se moverá hacia la izquierda
            
        self.rect.y = random.randint(0, screen_height - self.rect.height) # Altura aleatoria

        self.speed = random.randint(1, 3) # Velocidad de movimiento aleatoria

    def update(self):
        self.rect.x += self.speed * self.direction

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_offscreen(self, screen_width):
        # Comprobar si la nube ha salido completamente por izquierda o derecha
        return (self.rect.right < 0) or (self.rect.left > screen_width)