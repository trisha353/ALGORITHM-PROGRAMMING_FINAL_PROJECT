import pygame
from constants import *
import random
import math


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
        # Draw geometric ship
        pygame.draw.polygon(self.image, C_PLAYER, [(20, 0), (40, 50), (20, 40), (0, 50)])
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
        self.vel_x = 0

    def update(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
        
        self.rect.x += self.vel_x
        # Clamp to screen
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
        # Draw aggressive enemy shape
        pygame.draw.polygon(self.image, C_ENEMY, [(0, 0), (40, 0), (20, 50)])
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH-50), -50))
        self.speed = ENEMY_SPEED + random.uniform(0, 2)

    def update(self, player_x, scroll_speed):
        self.rect.y += self.speed + (scroll_speed * 0.5)
        
        # Simple AI: Chase player on X axis slowly
        if self.rect.y < SCREEN_HEIGHT - 200: # Only chase if above player
            if self.rect.centerx < player_x:
                self.rect.x += 1
            elif self.rect.centerx > player_x:
                self.rect.x -= 1
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(30, 60)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # Draw rough rock shape
        points = []
        for i in range(8):
            angle = math.radians(i * 45)
            r = (size//2) * random.uniform(0.7, 1.0)
            points.append((size//2 + r*math.cos(angle), size//2 + r*math.sin(angle)))
        pygame.draw.polygon(self.image, C_ASTEROID, points)
        self.rect = self.image.get_rect(center=(random.randint(30, SCREEN_WIDTH-30), -60))
        self.speed_y = random.uniform(2, 5)

    def update(self, scroll_speed):
        self.rect.y += self.speed_y + scroll_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(C_BULLET)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        # Geometric diamond star
        pygame.draw.polygon(self.image, C_STAR, [(10, 0), (20, 10), (10, 20), (0, 10)])
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH-20), -20))

    def update(self, scroll_speed):
        self.rect.y += scroll_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class BoostPad(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        # Chevron shape
        pygame.draw.lines(self.image, C_BOOST, False, [(5, 20), (15, 5), (25, 20)], 4)
        pygame.draw.lines(self.image, C_BOOST, False, [(5, 25), (15, 10), (25, 25)], 4)
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH-20), -30))

    def update(self, scroll_speed):
        self.rect.y += scroll_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        angle = random.uniform(0, 6.28)
        speed = random.uniform(1, 4)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        self.life = random.randint(20, 40)
        self.decay = 255 / self.life

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1
        self.size -= 0.1

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            alpha = int(self.life * self.decay)
            if alpha > 255: alpha = 255
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))
