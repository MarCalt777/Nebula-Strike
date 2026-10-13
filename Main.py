import os
import random
import sys
import pygame

# Inicializējam Pygame
pygame.init()

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


def save_score(player_name, final_score):
  """Saglabā rezultātu un automātiski atjaunina web/leaderboard.html lapu"""
  try:
    # 1. Saglabā scores.txt failā
    with open("scores.txt", "a", encoding="utf-8") as file:
      file.write(f"Spēlētājs: {player_name} | Punkti: {final_score}\n")

    # 2. Nolasām un atrodam katra spēlētāja labāko rezultātu
    player_best_scores = {}
    if os.path.exists("scores.txt"):
      with open("scores.txt", "r", encoding="utf-8") as file:
        for line in file:
          try:
            parts = line.strip().split("|")
            name_part = parts[0].replace("Spēlētājs:", "").strip()
            score_part = int(parts[1].replace("Punkti:", "").strip())

            if (
                name_part not in player_best_scores
                or score_part > player_best_scores[name_part]
            ):
              player_best_scores[name_part] = score_part
          except Exception:
            continue

    # 3. Sakārtojam dilstošā secībā
    sorted_scores = sorted(
        player_best_scores.items(), key=lambda x: x[1], reverse=True
    )

    # 4. Nodrošinām, ka web mape eksistē
    os.makedirs("web", exist_ok=True)

    # 5. Izveidojam HTML saturu
    html_content = """<!DOCTYPE html>
<html lang="lv">
<head>
    <meta charset="UTF-8">
    <title>Nebula Strike - Līderu tabula</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav>
        <a href="leaderboard.html">TOP</a>
        <a href="rules.html">Noteikumi</a>
    </nav>

    <h1>TOP Līderi</h1>
    <table>
        <tr><th>#</th><th>Spēlētājs</th><th>Punkti</th></tr>
"""

    for i, (name, sc) in enumerate(sorted_scores[:10], 1):
      row_class = ' class="first"' if i == 1 else ""
      html_content += (
          f"        <tr{row_class}><td>{i}</td><td>{name}</td><td>{sc}</td></tr>\n"
      )

    html_content += """    </table>
</body>
</html>"""

    with open("web/leaderboard.html", "w", encoding="utf-8") as html_file:
      html_file.write(html_content)

  except Exception as e:
    print(f"Kļūda saglabājot rezultātu: {e}")


def main():
  player_name = ""
  game_state = "MENU"  # MENU, PLAYING, GAMEOVER

  player_width = 40
  player_height = 40
  player_x = SCREEN_WIDTH // 2 - player_width // 2
  player_y = 500
  player_speed = 5
  player_hp = 3

  score = 0
  level = 1
  enemies_defeated = 0

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

  running = True
  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

      if game_state == "MENU":
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_RETURN:
            if player_name.strip() != "":
              game_state = "PLAYING"
          elif event.key == pygame.K_BACKSPACE:
            player_name = player_name[:-1]
          else:
            if len(player_name) < 15:
              player_name += event.unicode

      elif game_state == "PLAYING":
        if event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 1:  # Kreisais klikšķis - šaušana
            if shoot_cooldown <= 0:
              bullets.append(
                  {"x": player_x + player_width // 2 - 4, "y": player_y}
              )
              shoot_cooldown = 6 if fast_shoot_timer > 0 else 12
          elif event.button == 3:  # Labais klikšķis - Lāzers
            if special_ready and laser_timer <= 0:
              laser_timer = 180
              special_charge = 0
              special_ready = False

      elif game_state == "GAMEOVER":
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_r:
            player_x = SCREEN_WIDTH // 2 - player_width // 2
            player_y = 500
            player_hp = 3
            score = 0
            level = 1
            enemies_defeated = 0
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

      keys_pressed = pygame.key.get_pressed()
      if keys_pressed[pygame.K_w] and player_y > 340:
        player_y -= player_speed
      if keys_pressed[pygame.K_s] and player_y < SCREEN_HEIGHT - player_height:
        player_y += player_speed
      if keys_pressed[pygame.K_a] and player_x > 0:
        player_x -= player_speed
      if keys_pressed[pygame.K_d] and player_x < SCREEN_WIDTH - player_width:
        player_x += player_speed

      level = 1 + score // 50

      # Pretinieku ģenerēšana
      enemy_spawn_timer += 1
      if enemy_spawn_timer > max(30, 70 - level * 10) and len(enemies) < 7:
        base_hp = 1 + (level - 1) // 3
        enemies.append({
            "x": random.randint(50, SCREEN_WIDTH - 90),
            "y": random.randint(50, 220),
            "width": 40,
            "height": 30,
            "hp": base_hp,
            "max_hp": base_hp,
            "dx": random.choice([-2, 2]) * (1 + level * 0.2),
            "shoot_timer": random.randint(30, 100),
        })
        enemy_spawn_timer = 0

      # Asteroīdu ģenerēšana
      if level >= 3:
        asteroid_spawn_timer += 1
        level_steps = (level - 3) // 3
        spawn_threshold = max(40, 160 - level_steps * 30)

        if asteroid_spawn_timer > spawn_threshold and len(asteroids) < 7:
          side = random.choice(["left", "right"])
          start_x = -40 if side == "left" else SCREEN_WIDTH + 40
          ast_dx = (
              random.randint(2, 4) if side == "left" else -random.randint(2, 4)
          )
          asteroids.append({
              "x": start_x,
              "y": random.randint(50, 250),
              "size": random.randint(35, 55),
              "dx": ast_dx,
              "dy": random.randint(1, 3),
          })
          asteroid_spawn_timer = 0

      for b in bullets[:]:
        b["y"] -= 10
        if b["y"] < 0:
          bullets.remove(b)

      for eb in enemy_bullets[:]:
        eb["y"] += 4
        if eb["y"] > SCREEN_HEIGHT:
          enemy_bullets.remove(eb)

      for e in enemies[:]:
        e["x"] += e["dx"]
        if e["x"] <= 10 or e["x"] >= SCREEN_WIDTH - 50:
          e["dx"] *= -1

        e["shoot_timer"] -= 1
        if e["shoot_timer"] <= 0:
          enemy_bullets.append({
              "x": e["x"] + e["width"] // 2 - 3,
              "y": e["y"] + e["height"],
          })
          e["shoot_timer"] = random.randint(60, 140)

      for ast in asteroids[:]:
        ast["x"] += ast["dx"]
        ast["y"] += ast["dy"]
        if (
            ast["y"] > SCREEN_HEIGHT
            or ast["x"] < -100
            or ast["x"] > SCREEN_WIDTH + 100
        ):
          asteroids.remove(ast)
          continue

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        ast_rect = pygame.Rect(ast["x"], ast["y"], ast["size"], ast["size"])
        if player_rect.colliderect(ast_rect):
          asteroids.remove(ast)
          if shield_timer <= 0:
            player_hp -= 3
            if player_hp <= 0:
              game_state = "GAMEOVER"
              save_score(player_name, score)

      for p in powerups[:]:
        p["y"] += 3
        if p["y"] > SCREEN_HEIGHT:
          powerups.remove(p)
          continue
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        p_rect = pygame.Rect(p["x"], p["y"], 20, 20)
        if player_rect.colliderect(p_rect):
          if p["type"] == "heal":
            player_hp += 1
          elif p["type"] == "shield":
            shield_timer = 300
          elif p["type"] == "fast_shoot":
            fast_shoot_timer = 300
          powerups.remove(p)

      if laser_timer > 0:
        laser_rect = pygame.Rect(
            player_x + player_width // 2 - 15, 0, 30, player_y
        )
        for e in enemies[:]:
          e_rect = pygame.Rect(e["x"], e["y"], e["width"], e["height"])
          if laser_rect.colliderect(e_rect):
            enemies.remove(e)
            score += 10
        for eb in enemy_bullets[:]:
          eb_rect = pygame.Rect(eb["x"], eb["y"], 6, 12)
          if laser_rect.colliderect(eb_rect):
            enemy_bullets.remove(eb)

      for b in bullets[:]:
        b_rect = pygame.Rect(b["x"], b["y"], 8, 16)
        hit_bullet = False
        for e in enemies[:]:
          e_rect = pygame.Rect(e["x"], e["y"], e["width"], e["height"])
          if b_rect.colliderect(e_rect):
            e["hp"] -= 1
            hit_bullet = True
            if e["hp"] <= 0:
              enemies.remove(e)
              score += 10
              enemies_defeated += 1

              if not special_ready and laser_timer <= 0:
                special_charge += 1
                if special_charge >= 5:
                  special_ready = True

              if random.random() < 0.3:
                p_type = random.choices(
                    ["heal", "shield", "fast_shoot"], weights=[60, 30, 10]
                )[0]
                powerups.append({"x": e["x"], "y": e["y"], "type": p_type})
            break
        if hit_bullet and b in bullets:
          bullets.remove(b)

      for b in bullets[:]:
        b_rect = pygame.Rect(b["x"], b["y"], 8, 16)
        bullet_collided = False
        for eb in enemy_bullets[:]:
          eb_rect = pygame.Rect(eb["x"], eb["y"], 6, 12)
          if b_rect.colliderect(eb_rect):
            enemy_bullets.remove(eb)
            bullet_collided = True
            break
        if bullet_collided:
          if b in bullets:
            bullets.remove(b)
          continue

      player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
      for eb in enemy_bullets[:]:
        eb_rect = pygame.Rect(eb["x"], eb["y"], 6, 12)
        if player_rect.colliderect(eb_rect):
          enemy_bullets.remove(eb)
          if shield_timer <= 0:
            player_hp -= 1
            if player_hp <= 0:
              game_state = "GAMEOVER"
              save_score(player_name, score)

    # Zīmēšana
    screen.fill(BG_COLOR)

    if game_state == "MENU":
      title_surf = font_large.render("NEBULA STRIKE", True, PLAYER_COLOR)
      screen.blit(
          title_surf,
          (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 150),
      )
      prompt_surf = font_small.render(
          "Ievadi savu vārdu un spied ENTER:", True, TEXT_COLOR
      )
      screen.blit(
          prompt_surf,
          (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 260),
      )
      name_surf = font_large.render(
          player_name + ("_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""),
          True,
          YELLOW,
      )
      screen.blit(
          name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, 320)
      )

    elif game_state == "PLAYING":
      pygame.draw.line(
          screen, (40, 40, 70), (0, 310), (SCREEN_WIDTH, 310), 2
      )

      if shield_timer > 0:
        pygame.draw.circle(
            screen,
            SHIELD_COLOR,
            (player_x + player_width // 2, player_y + player_height // 2),
            32,
            2,
        )

      pygame.draw.rect(
          screen,
          PLAYER_COLOR,
          (player_x, player_y, player_width, player_height),
          border_radius=5,
      )
      pygame.draw.rect(
          screen,
          WHITE,
          (
              player_x + player_width // 2 - 5,
              player_y + 10,
              10,
              15,
          ),
          border_radius=3,
      )

      if laser_timer > 0:
        pygame.draw.rect(
            screen,
            LASER_COLOR,
            (player_x + player_width // 2 - 12, 0, 24, player_y),
        )

      for b in bullets:
        pygame.draw.rect(
            screen, BULLET_COLOR, (b["x"], b["y"], 8, 16), border_radius=3
        )

      for eb in enemy_bullets:
        pygame.draw.rect(
            screen,
            ENEMY_BULLET_COLOR,
            (eb["x"], eb["y"], 6, 12),
            border_radius=2,
        )

      for e in enemies:
        if e["max_hp"] == 1:
          e_color = (230, 50, 50)
        elif e["max_hp"] == 2:
          e_color = (230, 130, 50)
        elif e["max_hp"] == 3:
          e_color = (230, 230, 50)
        else:
          e_color = (180, 50, 230)

        pygame.draw.rect(
            screen,
            e_color,
            (e["x"], e["y"], e["width"], e["height"]),
            border_radius=4,
        )

      for ast in asteroids:
        pygame.draw.circle(
            screen,
            ASTEROID_COLOR,
            (ast["x"] + ast["size"] // 2, ast["y"] + ast["size"] // 2),
            ast["size"] // 2,
        )

      for p in powerups:
        if p["type"] == "heal":
          p_color = HEAL_COLOR
        elif p["type"] == "shield":
          p_color = SHIELD_COLOR
        else:
          p_color = FAST_SHOOT_COLOR
        pygame.draw.circle(screen, p_color, (p["x"] + 10, p["y"] + 10), 10)

      score_text = font_small.render(
          f"Punkti: {score} | Līmenis: {level}", True, TEXT_COLOR
      )
      hp_text = font_small.render(f"Dzīvības: {player_hp}", True, TEXT_COLOR)

      screen.blit(score_text, (20, 20))
      screen.blit(hp_text, (20, 50))

      y_offset = 85
      if laser_timer > 0:
        special_text = font_small.render(
            f"LĀZERS AKTĪVS! ({laser_timer // 60 + 1}s)", True, LASER_COLOR
        )
        screen.blit(special_text, (20, y_offset))
        y_offset += 30
      elif special_ready:
        special_text = font_small.render(
            "Special (Labais klikšķis): GATAVS!", True, SPECIAL_COLOR
        )
        screen.blit(special_text, (20, y_offset))
        y_offset += 30
      else:
        special_text = font_small.render(
            f"Special (Labais klikšķis): {special_charge}/5", True, TEXT_COLOR
        )
        screen.blit(special_text, (20, y_offset))
        y_offset += 30

      if shield_timer > 0:
        shield_text = font_small.render(
            f"Vairogs: {shield_timer // 60 + 1}s", True, SHIELD_COLOR
        )
        screen.blit(shield_text, (20, y_offset))
        y_offset += 30

      if fast_shoot_timer > 0:
        fast_text = font_small.render(
            f"Ātrā šaušana: {fast_shoot_timer // 60 + 1}s", True, FAST_SHOOT_COLOR
        )
        screen.blit(fast_text, (20, y_offset))

    elif game_state == "GAMEOVER":
      go_surf = font_large.render("SPĒLE BEIGUSIES", True, (230, 50, 50))
      final_score_surf = font_large.render(
          f"Tavs rezultāts: {score}", True, TEXT_COLOR
      )
      restart_surf = font_small.render(
          "Spied 'R', lai sāktu no jauna, vai 'ESC', lai izietu.", True, YELLOW
      )

      screen.blit(
          go_surf, (SCREEN_WIDTH // 2 - go_surf.get_width() // 2, 180)
      )
      screen.blit(
          final_score_surf,
          (SCREEN_WIDTH // 2 - final_score_surf.get_width() // 2, 260),
      )
      screen.blit(
          restart_surf,
          (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, 340),
      )

    pygame.display.flip()
    clock.tick(60)

  pygame.quit()
  sys.exit()


if __name__ == "__main__":
  main()