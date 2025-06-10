import pygame
import os

class Player:
    def __init__(self, x, y):
        try:
            # Ruta absoluta a la imagen de la nave
            base_path = os.path.dirname(__file__)  # Carpeta game/
            image_path = os.path.join(base_path, '..', 'images', 'nave.png')
            image_path = os.path.abspath(image_path)

            print(f"Intentando cargar imagen desde: {image_path}")  # Debug
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 40))  # Escalar imagen
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            # Imagen fallback: rectángulo verde si falla carga
            self.image = pygame.Surface((50, 40))
            self.image.fill((0, 255, 0))

        # Rectángulo para posición y colisiones
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = 5  # Velocidad de movimiento
        self.lives = 3  # Vidas del jugador

        # Lista de balas activas disparadas
        self.bullets = []
        self.bullet_speed = 7

        # Tiempo de espera entre disparos (cooldown)
        self.cooldown = 0

    def move(self, direction, screen_width):
        """Mover jugador horizontalmente, sin salir de pantalla."""
        if direction == "left" and self.rect.left > 0:
            self.rect.x -= self.speed
        if direction == "right" and self.rect.right < screen_width:
            self.rect.x += self.speed

    def shoot(self):
        """Disparar una bala si cooldown es cero."""
        if self.cooldown == 0:
            # Crear bala como rectángulo pequeño arriba del centro de la nave
            bullet = pygame.Rect(self.rect.centerx - 2, self.rect.top, 4, 10)
            self.bullets.append(bullet)
            self.cooldown = 20  # Reiniciar cooldown (frames de espera)

    def update(self, screen_height):
        """Actualizar posición de balas y cooldown."""
        for bullet in self.bullets[:]:
            bullet.y -= self.bullet_speed
            # Remover balas que salen de pantalla
            if bullet.bottom < 0:
                self.bullets.remove(bullet)

        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, screen):
        """Dibujar jugador y balas en pantalla."""
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            pygame.draw.rect(screen, (255, 255, 0), bullet)  # Balas amarillas


