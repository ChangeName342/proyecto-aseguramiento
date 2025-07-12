import pygame
import random
import os

class EnemyBullet:
    def __init__(self, x, y, speed=3, color=(255, 0, 0), width=4, height=16, shape="rect"):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.color = color
        self.shape = shape 
        

    def update(self, screen_height):
        self.rect.y += self.speed
        return self.rect.top <= screen_height

    def draw(self, screen):
        if self.shape == "laser":
            # Línea fina láser brillante
            start_pos = (self.rect.centerx, self.rect.top)
            end_pos = (self.rect.centerx, self.rect.bottom)
            pygame.draw.line(screen, self.color, start_pos, end_pos, 3)
            glow_color = (min(255, self.color[0]+80), min(255, self.color[1]+80), min(255, self.color[2]+80))
            pygame.draw.line(screen, glow_color, start_pos, end_pos, 1)  # brillo suave
        else:
            # Bala rectangular normal
            pygame.draw.rect(screen, self.color, self.rect)

class Enemy:
    def __init__(self, x, y, bullet_speed=3, lives=1, image_name='cat.png'):
        try:
            base_path = os.path.dirname(__file__)
            image_path = os.path.join(base_path, '..', 'images', image_name)
            image_path = os.path.abspath(image_path)

            print(f"Intentando cargar imagen del enemigo desde: {image_path}")
            self.image_original = pygame.image.load(image_path).convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (90, 80))
        except Exception as e:
            print(f"Error cargando imagen del enemigo: {e}")
            self.image_original = pygame.Surface((90, 80))
            self.image_original.fill((255, 0, 0))

        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 4
        self.direction = 1
        self.move_down_distance = 20
        self.bullets = []
        self.bullet_speed = bullet_speed
        self.lives = lives
        self.dead = False
        self.shoot_probability = 0.0
        self.bullet_color = (255, 0, 0)  # Default red bullet
        

    def update(self, screen_width):
        if self.dead:
            return False
        self.rect.x += self.speed * self.direction
        if self.rect.right >= screen_width or self.rect.left <= 0:
            return True
        return False

    def move_down(self):
        if not self.dead:
            self.rect.y += self.move_down_distance

    def try_shoot(self):
        if not self.dead and random.random() < self.shoot_probability:
            bullet = EnemyBullet(
                self.rect.centerx - 2,
                self.rect.bottom,
                speed=self.bullet_speed,
                color=self.bullet_color,
                shape=getattr(self, 'bullet_shape', 'rect')  # por defecto rect si no está definido
            )
            self.bullets.append(bullet)

    def update_bullets(self, screen_height):
        for bullet in self.bullets[:]:
            if not bullet.update(screen_height):
                self.bullets.remove(bullet)

    def draw(self, screen):
        if not self.dead:
            screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)

    def receive_damage(self):
        if self.dead:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.dead = True
            self.bullets.clear()

class BasicEnemy(Enemy):
    def __init__(self, x, y, bullet_speed=3, level=1):
        super().__init__(x, y, bullet_speed=bullet_speed, lives=1, image_name='cat.png')
        self.shoot_probability = 0.06 * (3 ** (level - 1))
        self.bullet_color = (255, 0, 0)
        self.bullet_shape = "rect"


class StrongEnemy(Enemy):
    def __init__(self, x, y, bullet_speed=3, level=1):
        super().__init__(x, y, bullet_speed=bullet_speed, lives=2, image_name='ship.png')
        self.shoot_probability = 0.12 * (3 ** (level - 1))
        self.bullet_color = (255, 0, 255)  # magenta
        self.bullet_shape = "laser"

class FinalBoss(Enemy):
    def __init__(self, x, y, bullet_speed=4):
        super().__init__(x, y, bullet_speed=bullet_speed, lives=10, image_name='final_boss.png')
        try:
            base_path = os.path.dirname(__file__)
            image_path = os.path.join(base_path, '..', 'images', 'final_boss.png')
            image_path = os.path.abspath(image_path)
            self.image_original = pygame.image.load(image_path).convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (180, 160))  # nave más grande
        except Exception as e:
            print(f"Error cargando imagen del jefe final: {e}")
            self.image_original = pygame.Surface((180, 160))
            self.image_original.fill((255, 0, 0))

        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 20
        self.direction = 1
        self.move_down_distance = 10
        self.shoot_probability = 0.5
        self.bullet_color = (255, 0, 255)
        self.bullet_shape = "laser"
        self.lives = 20  # más vida
        self.dead = False