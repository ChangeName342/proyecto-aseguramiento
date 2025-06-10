import pygame
import random
import os

class Enemy:
    def __init__(self, x, y):
        try:
            base_path = os.path.dirname(__file__)  # Ruta relativa para cargar imagen del enemigo
            image_path = os.path.join(base_path, '..', 'images', 'cat.png')
            image_path = os.path.abspath(image_path)

            print(f"Intentando cargar imagen del enemigo desde: {image_path}")  # Debug de ruta
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (90, 80))  # Escala imagen al tamaño deseado
        except Exception as e:
            # Fallback visual en caso de fallo al cargar imagen
            print(f"Error cargando imagen del enemigo: {e}")
            self.image = pygame.Surface((90, 80))
            self.image.fill((255, 0, 0))  # Color rojo para indicar error

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 4
        self.direction = 1  # Dirección horizontal (1: derecha, -1: izquierda)
        self.move_down_distance = 20  # Distancia para bajar cuando cambia de dirección
        self.bullets = []
        self.shoot_probability = 0.009  # Probabilidad de disparar cada frame
        self.should_move_down = False  # Flag para indicar movimiento vertical

    def update(self, screen_width):
        self.rect.x += self.speed * self.direction
        
        # Cambia dirección y avisa para bajar si toca un borde de pantalla
        if self.rect.right >= screen_width or self.rect.left <= 0:
            self.direction *= -1
            return True
        return False

    def move_down(self):
        self.rect.y += 15  # Movimiento vertical al bajar

    def try_shoot(self):
        # Dispara con cierta probabilidad aleatoria
        if random.random() < self.shoot_probability:
            bullet = pygame.Rect(self.rect.centerx - 2, self.rect.bottom, 4, 10)
            self.bullets.append(bullet)

    def update_bullets(self, screen_height):
        # Actualiza posición de balas y elimina las que salen de pantalla
        for bullet in self.bullets[:]:
            bullet.y += 3
            if bullet.top > screen_height:
                self.bullets.remove(bullet)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Dibuja las balas del enemigo en rojo claro
        for bullet in self.bullets:
            pygame.draw.rect(screen, (255, 100, 100), bullet)