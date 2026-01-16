import pygame
import random
from constants import *
from items import *


# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Space Highway")
clock = pygame.time.Clock()

# Fonts
try:
    FONT_HEAD = pygame.font.SysFont("Space Grotesk", 50, bold=True)
    FONT_BODY = pygame.font.SysFont("Verdana", 20)
    FONT_SCORE = pygame.font.SysFont("Verdana", 30, bold=True)
except:
    FONT_HEAD = pygame.font.Font(None, 50)
    FONT_BODY = pygame.font.Font(None, 20)
    FONT_SCORE = pygame.font.Font(None, 30)



# Background stars for parallax
bg_stars = [{'x': random.randint(0, SCREEN_WIDTH), 'y': random.randint(0, SCREEN_HEIGHT), 's': random.randint(1, 3)} for _ in range(100)]

# --- GAME ENGINE ---

def draw_text_centered(text, font, color, surface, y_offset=0):
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
    surface.blit(text_obj, rect)

def main():
    game_active = False
    score = 0
    scroll_speed = SCROLL_SPEED_BASE
    boost_timer = 0
    
    # Sprite Groups
    player_group = pygame.sprite.GroupSingle()
    player = Player()
    player_group.add(player)
    
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    boosts = pygame.sprite.Group()
    
    particles = []

    # Timers
    enemy_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(enemy_timer, 1500)
    
    asteroid_timer = pygame.USEREVENT + 2
    pygame.time.set_timer(asteroid_timer, 1000)
    
    item_timer = pygame.USEREVENT + 3
    pygame.time.set_timer(item_timer, 2000)

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # SHOOTING MECHANIC
                        bullets.add(Bullet(player.rect.centerx, player.rect.top))
                        
                if event.type == enemy_timer:
                    enemies.add(Enemy())
                if event.type == asteroid_timer:
                    asteroids.add(Asteroid())
                if event.type == item_timer:
                    if random.random() > 0.7:
                        boosts.add(BoostPad())
                    else:
                        stars.add(Star())
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset Game
                    game_active = True
                    score = 0
                    scroll_speed = SCROLL_SPEED_BASE
                    player.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
                    enemies.empty()
                    asteroids.empty()
                    stars.empty()
                    boosts.empty()
                    bullets.empty()
                    particles.clear()

        # 2. Logic Updates
        screen.fill(C_BG)
        
        # Background Animation
        for star in bg_stars:
            star['y'] += star['s'] + (scroll_speed * 0.1 if game_active else 1)
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, SCREEN_WIDTH)
            pygame.draw.circle(screen, (255, 255, 255), (star['x'], int(star['y'])), 1)

        if game_active:
            # Handle Boost
            if boost_timer > 0:
                boost_timer -= 1
                scroll_speed = BOOST_SPEED
                # Add trail particles
                particles.append(Particle(player.rect.centerx, player.rect.bottom, C_BOOST))
            else:
                scroll_speed = SCROLL_SPEED_BASE

            # Update Sprites
            player_group.update()
            bullets.update()
            enemies.update(player.rect.centerx, scroll_speed)
            asteroids.update(scroll_speed)
            stars.update(scroll_speed)
            boosts.update(scroll_speed)
            
            # Particle Physics
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

            # --- COLLISIONS ---
            
            # Bullet vs Asteroid (Rock Shoot)
            for bullet in bullets:
                hit_list = pygame.sprite.spritecollide(bullet, asteroids, True)
                for hit in hit_list:
                    score += 5
                    bullet.kill()
                    # Spawn Explosion
                    for _ in range(10):
                        particles.append(Particle(hit.rect.centerx, hit.rect.centery, C_ASTEROID))
            
            # Bullet vs Enemy
            for bullet in bullets:
                hit_list = pygame.sprite.spritecollide(bullet, enemies, True)
                for hit in hit_list:
                    score += 10
                    bullet.kill()
                    for _ in range(15):
                        particles.append(Particle(hit.rect.centerx, hit.rect.centery, C_ENEMY))

            # Player vs Collectibles
            if pygame.sprite.spritecollide(player, stars, True):
                score += 10
                for _ in range(5):
                    particles.append(Particle(player.rect.centerx, player.rect.centery, C_STAR))
            
            if pygame.sprite.spritecollide(player, boosts, True):
                boost_timer = BOOST_DURATION

            # Player vs Obstacles (Game Over)
            if pygame.sprite.spritecollide(player, enemies, False) or \
            pygame.sprite.spritecollide(player, asteroids, False):
                game_active = False
                # Explosion effect at player position
                for _ in range(30):
                    particles.append(Particle(player.rect.centerx, player.rect.centery, C_PLAYER))

            # Draw Game
            bullets.draw(screen)
            player_group.draw(screen)
            enemies.draw(screen)
            asteroids.draw(screen)
            stars.draw(screen)
            boosts.draw(screen)
            
            for p in particles:
                p.draw(screen)

            # UI HUD
            score_surf = FONT_SCORE.render(f"STARS: {score}", True, C_TEXT)
            screen.blit(score_surf, (20, 20))
            
            if boost_timer > 0:
                boost_text = FONT_BODY.render("SPEED BOOST!", True, C_BOOST)
                screen.blit(boost_text, (20, 60))

        else:
            # Main Menu / Game Over
            # Draw remaining particles for effect
            for p in particles:
                p.update()
                p.draw(screen)
                
            draw_text_centered("ENDLESS SPACE HIGHWAY", FONT_HEAD, C_PLAYER, screen, -60)
            draw_text_centered(f"TOTAL SCORE: {score}", FONT_SCORE, C_TEXT, screen, 10)
            draw_text_centered("Press SPACE to Start", FONT_BODY, C_STAR, screen, 60)
            
            # Instructions
            instr = [
                "ARROWS to Move",
                "SPACE to Shoot Rocks", 
                "Collect Stars & Boosts", 
                "Avoid Red Ships & Grey Rocks"
            ]
            for i, line in enumerate(instr):
                t = FONT_BODY.render(line, True, (100, 116, 139))
                screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, SCREEN_HEIGHT - 150 + i*30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
