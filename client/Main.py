import sys
import pygame
import random
from game.models import Player, Bullet, EnemyBullet, Enemy, Asteroid, PowerUp, check_collision
from client.api_client import register_and_login, send_score_to_server

# Inicializējam Pygame
pygame.init()

# Ekrāna iestatījumi
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nebula Strike")
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

def main():
    player_name = ""
    player_token = ""
    game_state = "MENU"

    player = Player(SCREEN_WIDTH // 2 - 20, 500)
    score = 0
    level = 1
    
    total_enemies_in_wave = 20 + ((level - 1) // 2) * 5
    enemies_spawned_in_wave = 0
    enemies_defeated_in_wave = 0

    special_charge = 0
    special_ready = False
    laser_timer = 0
    shield_timer = 0
    fast_shoot_timer = 0

    bullets = []
    enemy_bullets = []
    enemies = []
    asteroids = []
    powerups = []

    enemy_spawn_timer = 0
    asteroid_spawn_timer = 0
    shoot_cooldown = 0

    # Attēlu ielāde (ar fallback uz krāsainiem laukumiem, ja bildes nav)
    try:
        player_image = pygame.image.load("ship_blue.png").convert_alpha()
        player_image = pygame.transform.scale(player_image, (45, 40))
    except Exception:
        player_image = None

    enemy_images = {}
    ship_files = {
        1: "ship_green.png", 
        2: "ship_red.png", 
        3: "ship_yellow.png", 
        4: "ship_cyan.png", 
        5: "ship_purple.png"
    }
    for sid, sfile in ship_files.items():
        try:
            img = pygame.image.load(sfile).convert_alpha()
            enemy_images[sid] = pygame.transform.scale(img, (45, 40))
        except Exception:
            enemy_images[sid] = None

    running = True
    while running:
        keys_dict = {}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip() != "":
                            player_token = register_and_login(player_name.strip())
                            game_state = "PLAYING"
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 15:
                            player_name += event.unicode

            elif game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game_state = "PAUSED"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and fast_shoot_timer <= 0:
                        if shoot_cooldown <= 0:
                            bullets.append(Bullet(player.x + player.width // 2, player.y))
                            shoot_cooldown = 12
                    elif event.button == 3:
                        if special_ready and laser_timer <= 0:
                            laser_timer = 120  
                            special_charge = 0
                            special_ready = False

            elif game_state == "PAUSED":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game_state = "PLAYING"
                    elif event.key == pygame.K_l:
                        running = False

            elif game_state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        player.x = SCREEN_WIDTH // 2 - 20
                        player.y = 500
                        player.hp = 3
                        score = 0
                        level = 1
                        total_enemies_in_wave = 20 + ((level - 1) // 2) * 5
                        enemies_spawned_in_wave = 0
                        enemies_defeated_in_wave = 0
                        special_charge = 0
                        special_ready = False
                        laser_timer = 0
                        shield_timer = 0
                        fast_shoot_timer = 0
                        bullets.clear()
                        enemy_bullets.clear()
                        enemies.clear()
                        asteroids.clear()
                        powerups.clear()
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

            if fast_shoot_timer > 0 and pygame.mouse.get_pressed()[0]:
                if shoot_cooldown <= 0:
                    bullets.append(Bullet(player.x + player.width // 2, player.y))
                    shoot_cooldown = 8

            pressed = pygame.key.get_pressed()
            keys_dict["w"] = pressed[pygame.K_w]
            keys_dict["s"] = pressed[pygame.K_s]
            keys_dict["a"] = pressed[pygame.K_a]
            keys_dict["d"] = pressed[pygame.K_d]

            player.update(keys_dict, SCREEN_WIDTH, SCREEN_HEIGHT)

            # --- VIĻŅU UN LĪMEŅU LOĢIKA ---
            if enemies_defeated_in_wave >= total_enemies_in_wave and len(enemies) == 0:
                level += 1
                enemies_spawned_in_wave = 0
                enemies_defeated_in_wave = 0
                total_enemies_in_wave = 20 + ((level - 1) // 2) * 5

            enemy_spawn_timer += 1
            spawn_threshold = max(35, 80 - level * 5)
            if enemies_spawned_in_wave < total_enemies_in_wave and len(enemies) < 6:
                if enemy_spawn_timer > spawn_threshold:
                    enemies.append(Enemy(random.randint(50, SCREEN_WIDTH - 90), random.randint(50, 220), level))
                    enemies_spawned_in_wave += 1
                    enemy_spawn_timer = 0

            asteroid_spawn_timer += 1
            max_asteroids = min(12, 2 + (level - 1) * 2)
            spawn_threshold_ast = max(40, 160 - level * 20)
            if asteroid_spawn_timer > spawn_threshold_ast and len(asteroids) < max_asteroids:
                asteroids.append(Asteroid(level, SCREEN_WIDTH))
                asteroid_spawn_timer = 0

            for b in bullets[:]:
                b.update()
                if not b.active:
                    bullets.remove(b)

            for eb in enemy_bullets[:]:
                eb.update(SCREEN_HEIGHT)
                if not eb.active:
                    enemy_bullets.remove(eb)

            for ast in asteroids[:]:
                ast.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                if not ast.active:
                    asteroids.remove(ast)

            for p in powerups[:]:
                p.update(SCREEN_HEIGHT)
                if not p.active:
                    powerups.remove(p)

            for e in enemies[:]:
                if e.update(SCREEN_WIDTH):
                    enemy_bullets.append(EnemyBullet(e.x + e.width // 2 - 3, e.y + e.height, level))

            # --- KOLĪZIJAS ---
            ast_hits = [ast for ast in asteroids if check_collision(player.rect, ast.rect)]
            for ast in ast_hits:
                asteroids.remove(ast)
                if shield_timer <= 0:
                    player.hp -= 3
                    if player.hp <= 0:
                        game_state = "GAMEOVER"
                        send_score_to_server(player_token, score)

            pw_hits = [pw for pw in powerups if check_collision(player.rect, pw.rect)]
            for p in pw_hits:
                powerups.remove(p)
                if p.type == "heal":
                    player.hp += 1
                elif p.type == "shield":
                    shield_timer = 300
                elif p.type == "fast_shoot":
                    fast_shoot_timer = 300

            if laser_timer > 0:
                laser_rect = (player.x + player.width // 2 - 15, 0, 30, player.y)
                for e in enemies[:]:
                    if check_collision(laser_rect, e.rect):
                        enemies.remove(e)
                        score += 10
                        enemies_defeated_in_wave += 1
                for eb in enemy_bullets[:]:
                    if check_collision(laser_rect, eb.rect):
                        enemy_bullets.remove(eb)

            for b in bullets[:]:
                hit_enemies = [e for e in enemies if check_collision(b.rect, e.rect)]
                if hit_enemies:
                    if b in bullets:
                        bullets.remove(b)
                    for e in hit_enemies:
                        e.hp -= 1
                        if e.hp <= 0:
                            if e in enemies:
                                enemies.remove(e)
                            score += 10
                            enemies_defeated_in_wave += 1
                            if not special_ready and laser_timer <= 0:
                                special_charge += 1
                                if special_charge >= 5:
                                    special_ready = True
                            if random.random() < 0.3:
                                powerups.append(PowerUp(e.x, e.y))

            # Lodes pret ienaidnieku lodēm
            for b in bullets[:]:
                hit_eb = [eb for eb in enemy_bullets if check_collision(b.rect, eb.rect)]
                if hit_eb:
                    if b in bullets:
                        bullets.remove(b)
                    for eb in hit_eb:
                        if eb in enemy_bullets:
                            enemy_bullets.remove(eb)

            eb_hits = [eb for eb in enemy_bullets if check_collision(player.rect, eb.rect)]
            if eb_hits:
                for eb in eb_hits:
                    if eb in enemy_bullets:
                        enemy_bullets.remove(eb)
                if shield_timer <= 0:
                    player.hp -= len(eb_hits)
                    if player.hp <= 0:
                        game_state = "GAMEOVER"
                        send_score_to_server(player_token, score)

        # --- ZĪMĒŠANA ---
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

        elif game_state in ("PLAYING", "PAUSED"):
            pygame.draw.line(screen, (40, 40, 70), (0, 310), (SCREEN_WIDTH, 310), 2)

            if shield_timer > 0:
                pygame.draw.circle(screen, SHIELD_COLOR, (player.x + player.width // 2, player.y + player.height // 2), 32, 2)

            if player_image:
                screen.blit(player_image, (player.x, player.y))
            else:
                pygame.draw.rect(screen, PLAYER_COLOR, (player.x, player.y, player.width, player.height), border_radius=5)

            for b in bullets:
                pygame.draw.rect(screen, BULLET_COLOR, (b.x, b.y, b.width, b.height), border_radius=3)

            for eb in enemy_bullets:
                pygame.draw.rect(screen, ENEMY_BULLET_COLOR, (eb.x, eb.y, eb.width, eb.height), border_radius=2)

            for e in enemies:
                img = enemy_images.get(e.design_id)
                if img:
                    screen.blit(img, (e.x, e.y))
                else:
                    colors = {
                        1: (230, 50, 50),
                        2: (230, 130, 50),
                        3: (230, 230, 50),
                        4: (50, 200, 200),
                        5: (180, 50, 230)
                    }
                    color = colors.get(e.design_id, (180, 50, 230))
                    pygame.draw.rect(screen, color, (e.x, e.y, e.width, e.height), border_radius=4)

            for ast in asteroids:
                pygame.draw.circle(screen, ASTEROID_COLOR, (int(ast.x + ast.size // 2), int(ast.y + ast.size // 2)), ast.size // 2)

            for p in powerups:
                p_color = HEAL_COLOR if p.type == "heal" else (SHIELD_COLOR if p.type == "shield" else FAST_SHOOT_COLOR)
                pygame.draw.circle(screen, p_color, (int(p.x + 10), int(p.y + 10)), 10)

            if laser_timer > 0:
                pygame.draw.rect(screen, LASER_COLOR, (player.x + player.width // 2 - 12, 0, 24, player.y))

            score_text = font_small.render(f"Punkti: {score} | Līmenis: {level}", True, TEXT_COLOR)
            hp_text = font_small.render(f"Dzīvības: {max(0, player.hp)}", True, TEXT_COLOR)
            
            enemies_left_in_wave = max(0, total_enemies_in_wave - enemies_defeated_in_wave)
            wave_text = font_small.render(f"Atlikušie kuģi: {enemies_left_in_wave}/{total_enemies_in_wave}", True, YELLOW)

            screen.blit(score_text, (20, 20))
            screen.blit(hp_text, (20, 50))
            screen.blit(wave_text, (20, 80))

            y_offset = 115
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

            if game_state == "PAUSED":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))

                pause_surf = font_large.render("PAUZE", True, WHITE)
                resume_surf = font_small.render("Spied 'P', lai turpinātu spēli", True, YELLOW)
                exit_surf = font_small.render("Spied 'L', lai izietu no spēles", True, (230, 50, 50))

                screen.blit(pause_surf, (SCREEN_WIDTH // 2 - pause_surf.get_width() // 2, 200))
                screen.blit(resume_surf, (SCREEN_WIDTH // 2 - resume_surf.get_width() // 2, 280))
                screen.blit(exit_surf, (SCREEN_WIDTH // 2 - exit_surf.get_width() // 2, 330))

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