import os
import random
import sys
import pygame
import requests

# Inicializējam Pygame
pygame.init()

# Servera adrese
SERVER_URL = "http://127.0.0.1:8000"

# Ekrāna iestatījumi
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nebula Strike - Mārcis")
clock = pygame.time.Clock()

# Krāsas (RGB)
BG_COLOR = (15, 15, 30)
PLAYER_COLOR = (50, 150, 255)
BULLET_COLOR = (255, 255, 100)
ENEMY_BULLET_COLOR = (255, 100, 100)
ASTEROID_COLOR = (120, 120, 120)
HEAL_COLOR = (50, 230, 50)
SHIELD_COLOR = (0, 200, 255)
FAST_SHOOT_COLOR = (255, 165, 0)
SPECIAL_COLOR = (180, 50, 230)
LASER_COLOR = (0, 255, 255)
TEXT_COLOR = (255, 255, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Šrifti
font_small = pygame.font.SysFont("Arial", 22)
font_large = pygame.font.SysFont("Arial", 48)


def send_score_to_server(player_token, final_score):
    """Nosūta rezultātu uz FastAPI serveri un atjaunina leaderboard.html, iztīrot vecās rindas"""
    try:
        if player_token:
            headers = {"token": player_token}
            requests.post(f"{SERVER_URL}/scores", json={"score": final_score}, headers=headers)

        # Iegūstam top rezultātus no servera
        response = requests.get(f"{SERVER_URL}/scores/top")
        if response.status_code == 200:
            top_data = response.json()
            
            rows_html = ""
            for i, entry in enumerate(top_data[:10], 1):
                row_class = ' class="first"' if i == 1 else ""
                rows_html += f'        <tr{row_class}><td>{i}</td><td>{entry["player"]}</td><td>{entry["score"]}</td></tr>\n'

            # Atjaunojam leaderboard.html failu, saglabājot sākotnējo HTML struktūru
            if os.path.exists("web/leaderboard.html"):
                with open("web/leaderboard.html", "r", encoding="utf-8") as html_file:
                    content = html_file.read()

                start_tag = "<table>\n        <tr><th>#</th><th>Spēlētājs</th><th>Punkti</th></tr>"
                end_tag = "    </table>"

                if start_tag in content and end_tag in content:
                    before_table = content.split(start_tag)[0]
                    after_table = content.split(end_tag)[1]

                    # Uzbūvējam tabulu no jauna, aizvietojot visu, kas bija iekšpusē, ar jaunajām rindām
                    new_table = f"{start_tag}\n        <!-- TABLE_ROWS -->\n{rows_html}{end_tag}"
                    final_html = before_table + new_table + after_table

                    with open("web/leaderboard.html", "w", encoding="utf-8") as html_file:
                        html_file.write(final_html)

    except Exception as e:
        print(f"Kļūda saziņā ar serveri: {e}")

# --- SPĒLĒTĀJA UN OBJEKTU KLASES ---

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("ship_blue.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (45, 40))
        except Exception:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.rect(self.image, PLAYER_COLOR, (0, 0, 40, 40), border_radius=5)
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        self.hp = 3

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_w] and self.rect.y > 340:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
        if keys_pressed[pygame.K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BULLET_COLOR, (0, 0, 8, 16), border_radius=3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, ENEMY_BULLET_COLOR, (0, 0, 6, 12), border_radius=2)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y, level):
        super().__init__()
        self.width = 40
        self.height = 30
        self.max_hp = min(5, 1 + (level - 1) // 2)
        self.hp = self.max_hp

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.update_design()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dx = random.choice([-2, 2]) * (1 + level * 0.2)
        self.shoot_timer = random.randint(30, 100)

    def update_design(self):
        self.image.fill((0, 0, 0, 0))
        colors = {
            1: (230, 50, 50),
            2: (230, 130, 50),
            3: (230, 230, 50),
            4: (50, 200, 200),
            5: (180, 50, 230)
        }
        color = colors.get(self.max_hp, (180, 50, 230))
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height), border_radius=4)

    def update(self):
        self.rect.x += self.dx
        if self.rect.left <= 10 or self.rect.right >= SCREEN_WIDTH - 10:
            self.dx *= -1

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(60, 140)
            return True
        return False


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, level):
        super().__init__()
        side = random.choice(["left", "right"])
        self.size = random.randint(35, 55)
        start_x = -40 if side == "left" else SCREEN_WIDTH + 40
        self.dx = random.randint(2, 4) if side == "left" else -random.randint(2, 4)
        self.dy = random.randint(1, 3)

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ASTEROID_COLOR, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect(topleft=(start_x, random.randint(50, 250)))

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top > SCREEN_HEIGHT or self.rect.right < -100 or self.rect.left > SCREEN_WIDTH + 100:
            self.kill()


class PowerUp(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.type = random.choices(["heal", "shield", "fast_shoot"], weights=[60, 30, 10])[0]
        p_color = HEAL_COLOR if self.type == "heal" else (SHIELD_COLOR if self.type == "shield" else FAST_SHOOT_COLOR)

        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, p_color, (10, 10), 10)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.y += 3
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# --- GALVENĀ SPĒLES FUNKCIJA ---

def main():
    player_name = ""
    player_token = ""
    game_state = "MENU"

    player = Player(SCREEN_WIDTH // 2 - 20, 500)
    score = 0
    level = 1
    enemies_defeated = 0

    special_charge = 0
    special_ready = False
    laser_timer = 0
    shield_timer = 0
    fast_shoot_timer = 0

    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    enemy_spawn_timer = 0
    asteroid_spawn_timer = 0
    shoot_cooldown = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip() != "":
                            # Mēģinām reģistrēt un pieteikt lietotāju serverī
                            try:
                                requests.post(f"{SERVER_URL}/register", json={"name": player_name.strip(), "password": "123"})
                            except Exception:
                                pass
                            
                            try:
                                login_resp = requests.post(f"{SERVER_URL}/login", json={"name": player_name.strip(), "password": "123"})
                                if login_resp.status_code == 200:
                                    player_token = login_resp.json().get("token", "")
                            except Exception:
                                player_token = ""

                            game_state = "PLAYING"
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 15:
                            player_name += event.unicode

            elif game_state == "PLAYING":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if shoot_cooldown <= 0:
                            b = Bullet(player.rect.centerx, player.rect.top)
                            bullets.add(b)
                            shoot_cooldown = 6 if fast_shoot_timer > 0 else 12
                    elif event.button == 3:
                        if special_ready and laser_timer <= 0:
                            laser_timer = 180
                            special_charge = 0
                            special_ready = False

            elif game_state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        player.rect.x = SCREEN_WIDTH // 2 - 20
                        player.rect.y = 500
                        player.hp = 3
                        score = 0
                        level = 1
                        enemies_defeated = 0
                        special_charge = 0
                        special_ready = False
                        laser_timer = 0
                        shield_timer = 0
                        fast_shoot_timer = 0
                        for group in [bullets, enemy_bullets, enemies, asteroids, powerups]:
                            group.empty()
                        game_state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if game_state == "PLAYING":
            if shoot_cooldown > 0:
                shoot_cooldown -= 1
            if laser_timer > 0:
                laser_timer -= 1
            if shield_timer > 0:
                shield_timer -= 1
            if fast_shoot_timer > 0:
                fast_shoot_timer -= 1

            keys_pressed = pygame.key.get_pressed()
            player.update(keys_pressed)

            level = 1 + score // 50

            enemy_spawn_timer += 1
            if enemy_spawn_timer > max(30, 70 - level * 10) and len(enemies) < 7:
                e = Enemy(random.randint(50, SCREEN_WIDTH - 90), random.randint(50, 220), level)
                enemies.add(e)
                enemy_spawn_timer = 0

            if level >= 3:
                asteroid_spawn_timer += 1
                level_steps = (level - 3) // 3
                spawn_threshold = max(40, 160 - level_steps * 30)
                if asteroid_spawn_timer > spawn_threshold and len(asteroids) < 7:
                    asteroids.add(Asteroid(level))
                    asteroid_spawn_timer = 0

            bullets.update()
            enemy_bullets.update()
            asteroids.update()
            powerups.update()

            for e in enemies:
                if e.update():
                    enemy_bullets.add(EnemyBullet(e.rect.centerx - 3, e.rect.bottom))

            # Kolīzijas
            ast_hits = pygame.sprite.spritecollide(player, asteroids, True)
            if ast_hits and shield_timer <= 0:
                player.hp -= 3
                if player.hp <= 0:
                    game_state = "GAMEOVER"
                    send_score_to_server(player_token, score)

            pw_hits = pygame.sprite.spritecollide(player, powerups, True)
            for p in pw_hits:
                if p.type == "heal":
                    player.hp += 1
                elif p.type == "shield":
                    shield_timer = 300
                elif p.type == "fast_shoot":
                    fast_shoot_timer = 300

            if laser_timer > 0:
                laser_rect = pygame.Rect(player.rect.centerx - 15, 0, 30, player.rect.y)
                for e in enemies:
                    if laser_rect.colliderect(e.rect):
                        e.kill()
                        score += 10
                for eb in enemy_bullets:
                    if laser_rect.colliderect(eb.rect):
                        eb.kill()

            bullet_hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in bullet_hits.items():
                for e in hit_enemies:
                    e.hp -= 1
                    if e.hp <= 0:
                        e.kill()
                        score += 10
                        enemies_defeated += 1
                        if not special_ready and laser_timer <= 0:
                            special_charge += 1
                            if special_charge >= 5:
                                special_ready = True
                        if random.random() < 0.3:
                            powerups.add(PowerUp(e.rect.x, e.rect.y))

            pygame.sprite.groupcollide(bullets, enemy_bullets, True, True)

            eb_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            if eb_hits and shield_timer <= 0:
                player.hp -= len(eb_hits)
                if player.hp <= 0:
                    game_state = "GAMEOVER"
                    send_score_to_server(player_token, score)

        # Zīmēšana
        screen.fill(BG_COLOR)

        if game_state == "MENU":
            title_surf = font_large.render("NEBULA STRIKE", True, PLAYER_COLOR)
            screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 150))
            prompt_surf = font_small.render("Ievadi savu vārdu un spied ENTER:", True, TEXT_COLOR)
            screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 260))
            name_surf = font_large.render(
                player_name + ("_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""),
                True,
                YELLOW,
            )
            screen.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, 320))

        elif game_state == "PLAYING":
            pygame.draw.line(screen, (40, 40, 70), (0, 310), (SCREEN_WIDTH, 310), 2)

            if shield_timer > 0:
                pygame.draw.circle(screen, SHIELD_COLOR, player.rect.center, 32, 2)

            screen.blit(player.image, player.rect)
            bullets.draw(screen)
            enemy_bullets.draw(screen)
            enemies.draw(screen)
            asteroids.draw(screen)
            powerups.draw(screen)

            if laser_timer > 0:
                pygame.draw.rect(screen, LASER_COLOR, (player.rect.centerx - 12, 0, 24, player.rect.y))

            score_text = font_small.render(f"Punkti: {score} | Līmenis: {level}", True, TEXT_COLOR)
            hp_text = font_small.render(f"Dzīvības: {max(0, player.hp)}", True, TEXT_COLOR)

            screen.blit(score_text, (20, 20))
            screen.blit(hp_text, (20, 50))

            y_offset = 85
            if laser_timer > 0:
                special_text = font_small.render(f"LĀZERS AKTĪVS! ({laser_timer // 60 + 1}s)", True, LASER_COLOR)
                screen.blit(special_text, (20, y_offset))
                y_offset += 30
            elif special_ready:
                special_text = font_small.render("Special (Labais klikšķis): GATAVS!", True, SPECIAL_COLOR)
                screen.blit(special_text, (20, y_offset))
                y_offset += 30
            else:
                special_text = font_small.render(f"Special (Labais klikšķis): {special_charge}/5", True, TEXT_COLOR)
                screen.blit(special_text, (20, y_offset))
                y_offset += 30

            if shield_timer > 0:
                shield_text = font_small.render(f"Vairogs: {shield_timer // 60 + 1}s", True, SHIELD_COLOR)
                screen.blit(shield_text, (20, y_offset))
                y_offset += 30

            if fast_shoot_timer > 0:
                fast_text = font_small.render(f"Ātrā šaušana: {fast_shoot_timer // 60 + 1}s", True, FAST_SHOOT_COLOR)
                screen.blit(fast_text, (20, y_offset))

        elif game_state == "GAMEOVER":
            go_surf = font_large.render("SPĒLE BEIGUSIES", True, (230, 50, 50))
            final_score_surf = font_large.render(f"Tavs rezultāts: {score}", True, TEXT_COLOR)
            restart_surf = font_small.render("Spied 'R', lai sāktu no jauna, vai 'ESC', lai izietu.", True, YELLOW)

            screen.blit(go_surf, (SCREEN_WIDTH // 2 - go_surf.get_width() // 2, 180))
            screen.blit(final_score_surf, (SCREEN_WIDTH // 2 - final_score_surf.get_width() // 2, 260))
            screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, 340))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()