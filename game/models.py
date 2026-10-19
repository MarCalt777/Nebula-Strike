import random

def check_collision(rect1, rect2):
    # rect formāts: (x, y, width, height)
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return (x1 < x2 + w2) and (x1 + w1 > x2) and (y1 < y2 + h2) and (y1 + h1 > y2)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 45
        self.height = 40
        self.speed = 5
        self.hp = 3

    def update(self, keys_pressed, screen_width, screen_height):
        if keys_pressed.get("w") and self.y > 340:
            self.y -= self.speed
        if keys_pressed.get("s") and self.y + self.height < screen_height:
            self.y += self.speed
        if keys_pressed.get("a") and self.x > 0:
            self.x -= self.speed
        if keys_pressed.get("d") and self.x + self.width < screen_width:
            self.x += self.speed

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)


class Bullet:
    def __init__(self, x, y):
        self.x = x - 4
        self.y = y
        self.width = 8
        self.height = 16
        self.speed = 10
        self.active = True

    def update(self):
        self.y -= self.speed
        if self.y + self.height < 0:
            self.active = False

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)


class EnemyBullet:
    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.width = 6
        self.height = 12
        self.speed = 4 + min(6, ((level - 1) // 2))
        self.active = True

    def update(self, screen_height):
        self.y += self.speed
        if self.y > screen_height:
            self.active = False

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)


class Enemy:
    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.width = 45
        self.height = 40
        self.level = level
        
        self.max_hp = level
        self.hp = self.max_hp
        self.design_id = ((level - 1) % 5) + 1
        self.active = True
        
        base_speed = random.choice([-2.5, 2.5])
        speed_multiplier = 1 + (level - 1) * 0.4
        self.dx = base_speed * speed_multiplier

        min_t = max(12, 45 - level * 6)
        max_t = max(25, 90 - level * 8)
        self.shoot_timer = random.randint(min_t, max_t)

    def update(self, screen_width):
        self.x += self.dx
        
        if self.x <= 10:
            self.x = 10
            self.dx *= -1
        elif self.x + self.width >= screen_width - 10:
            self.x = screen_width - 10 - self.width  # Izlabots: ņem vērā kuģa platumu, lai neiesprūstu
            self.dx *= -1

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            min_t = max(12, 45 - self.level * 6)
            max_t = max(25, 90 - self.level * 8)
            self.shoot_timer = random.randint(min_t, max_t)
            return True
        return False

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)


class Asteroid:
    def __init__(self, level, screen_width):
        side = random.choice(["left", "right"])
        self.size = random.randint(35, 55)
        self.width = self.size
        self.height = self.size
        start_x = -40 if side == "left" else screen_width + 40
        self.x = start_x
        self.y = random.randint(50, 250)
        self.dx = random.randint(2, 4) if side == "left" else -random.randint(2, 4)
        self.dy = random.randint(1, 3)
        self.active = True

    def update(self, screen_width, screen_height):
        self.x += self.dx
        self.y += self.dy
        if self.y > screen_height or self.x + self.width < -100 or self.x > screen_width + 100:
            self.active = False

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)


class PowerUp:
    def __init__(self, x, y):
        self.type = random.choices(["heal", "shield", "fast_shoot"], weights=[60, 30, 10])[0]
        self.width = 20
        self.height = 20
        self.x = x
        self.y = y
        self.active = True

    def update(self, screen_height):
        self.y += 3
        if self.y > screen_height:
            self.active = False

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)