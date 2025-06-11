import pygame
import math
import random
from collections import defaultdict

def generate_terrain():
      # 优先生成大型地形
      terrains = []
      for _ in range(2):
          while True:
              x = randint(0, 1920-18)
              y = randint(0, 1080-18)
              new_area = [(x+i, y+j) for i in range(18) for j in range(18)]
              if not check_overlap(new_area, terrains):
                  terrains.append({'type':'large_mountain', 'area':new_area})
                  break
      # 类似生成其他地形...
      
  def check_overlap(new_area, existing):
      for t in existing:
          if any(pos in t['area'] for pos in new_area):
              return True
      return False

def circle_rect_collision(circle, rect):
    # 圆形士兵与矩形机械师碰撞检测
    closest_x = clamp(circle.x, rect.left, rect.right)
    closest_y = clamp(circle.y, rect.top, rect.bottom)
    dx = circle.x - closest_x
    dy = circle.y - closest_y
    return (dx**2 + dy**2) <= (circle.radius**2)

def flight_movement(path):
    # 飞行师移动路径处理
    for point in path:
        if in_mountain_area(point):
            raise InvalidPathException
        ignore_ground_units = True

def calculate_effects(unit):
    speed_multiplier = 1.0
    range_multiplier = 1.0
    
    if in_desert_or_valley(unit.position):
        speed_multiplier *= 0.5
        range_multiplier *= 0.85
        
    if in_buff_area(unit.position):
        range_multiplier *= 1.15
        
    # 最终应用
    unit.effective_speed = base_speed * speed_multiplier
    unit.attack_range = base_range * range_multiplier

class EconomySystem:
    def __init__(self):
        self.points = 20
        self.last_update = time.time()
        
    def update(self):
        if time.time() - self.last_update >= 60:
            self.points += 1
            self.last_update = time.time()
            
    def check_facility_contact(self, unit):
        for facility in facilities:
            if unit_in_facility(unit, facility):
                if not facility.claimed:
                    self.points += facility.reward
                    facility.claimed = True

class AttackSystem:
    def handle_attack(self, attacker, targets):
        if attacker.type == '机械师':
            # 溅射伤害处理
            main_target = get_nearest_target(attacker)
            apply_damage(main_target, 3)
            for t in get_adjacent_units(main_target, 3x3):
                apply_damage(t, 2)
                
        elif attacker.type == '飞行师' and attacker.is_moving:
            # 移动中双次攻击
            for _ in range(2):
                target = select_target(attacker)
                apply_damage(target, 5)

EPSILON = 1e-6

def move_unit(unit, dt):
    remaining_time = dt
    while remaining_time > EPSILON:
        step = min(remaining_time, 0.1)  # 分步计算
        dx = unit.direction.x * unit.effective_speed * step
        dy = unit.direction.y * unit.effective_speed * step
        
        # 斜向移动补偿
        if abs(dx - dy) < EPSILON:
            dx = round(dx * 100)/100
            dy = round(dy * 100)/100
            
        new_pos = unit.position + Vector2(dx, dy)
        if validate_position(new_pos):
            unit.position = new_pos
            remaining_time -= step
        else:
            break
            
    # 最终对齐到网格中心
    unit.position = snap_to_grid(unit.position)

def test_mountain_generation():
    # 验证大型山脉不重叠
    terrain_system.generate_initial_map()
    assert len(terrain_system.mountains) == 2
    assert no_overlapping(terrain_system.mountains)

def test_desert_movement_penalty():
    soldier = create_unit('士兵', position=desert_area_center)
    original_speed = soldier.base_speed
    soldier.update_effects()
    assert soldier.effective_speed == original_speed * 0.5

def test_aerial_unit_collision():
    flight = create_unit('飞行师')
    ground = create_unit('士兵')
    assert not collision_system.check_collision(flight, ground)

def validate_position(pos):
    if pos.x < 0 or pos.x >= 1920:
        return False
    if pos.y < 0 or pos.y >= 1080:
        return False
    if in_restricted_terrain(pos):
        return False
    return True

class GameClock:
    def __init__(self):
        self.paused = False
        self.time_accumulator = 0.0
        
    def update(self, real_dt):
        if not self.paused:
            self.time_accumulator += real_dt
            
    def get_game_time(self):
        return self.time_accumulator

def snap_to_grid(pos):
    return Vector2(
        round(pos.x * 2)/2 if abs(pos.x - round(pos.x)) < EPSILON else pos.x,
        round(pos.y * 2)/2 if abs(pos.y - round(pos.y)) < EPSILON else pos.y
    )

class Quadtree:
    """四叉树空间分区优化设施生成"""
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary  # pygame.Rect
        self.capacity = capacity
        self.objects = []
        self.divided = False

    def subdivide(self):
        x, y, w, h = self.boundary
        nw = pygame.Rect(x, y, w/2, h/2)
        ne = pygame.Rect(x + w/2, y, w/2, h/2)
        sw = pygame.Rect(x, y + h/2, w/2, h/2)
        se = pygame.Rect(x + w/2, y + h/2, w/2, h/2)
        self.nw = Quadtree(nw, self.capacity)
        self.ne = Quadtree(ne, self.capacity)
        self.sw = Quadtree(sw, self.capacity)
        self.se = Quadtree(se, self.capacity)
        self.divided = True

    def insert(self, rect):
        if not self.boundary.colliderect(rect):
            return False

        if len(self.objects) < self.capacity:
            self.objects.append(rect)
            return True
        else:
            if not self.divided:
                self.subdivide()
            return (self.nw.insert(rect) or self.ne.insert(rect) or
                    self.sw.insert(rect) or self.se.insert(rect))

    def query(self, rect):
        found = []
        if not self.boundary.colliderect(rect):
            return found
        
        for obj in self.objects:
            if rect.colliderect(obj):
                found.append(obj)
        
        if self.divided:
            found += self.nw.query(rect)
            found += self.ne.query(rect)
            found += self.sw.query(rect)
            found += self.se.query(rect)
        return found

class Facility:
    types = {
        'SmallMountain': {'size': (40,40), 'block': False, 'color': (100,80,50)},
        'LargeMountain': {'size': (60,60), 'block': False, 'color': (80,60,40)},
        'SmallTown': {'size': (30,30), 'block': False, 'color': (200,150,100)},
        'LargeTown': {'size': (50,50), 'block': False, 'color': (180,130,90)},
        'Fjord': {'size': (80,80), 'block': False, 'color': (70,130,200)}  # 所有设施均可穿越
    }
    # ... 其余代码不变
    def __init__(self, f_type, pos):
        self.type = f_type
        self.rect = pygame.Rect(pos, self.types[f_type]['size'])
        self.color = self.types[f_type]['color']
        self.grids = self.calculate_grids()

    def calculate_grids(self):
        return [(x, y) for x in range(self.rect.left, self.rect.right) 
                       for y in range(self.rect.top, self.rect.bottom)]

class Unit:
    def __init__(self, team, utype, pos):
        self.team = team
        self.type = utype
        self.pos = list(pos)
        self.hp = {'Soldier':5, 'Engineer':20, 'Flyer':10}[utype]
        self.speed = {'Soldier':3, 'Engineer':7, 'Flyer':5}[utype]
        self.attack_range = 50
        self.attack_cooldown = 2
        self.sight_radius = 150
        self.selected = False  # 新增选中状态

    def move(self, dx, dy, facilities):
        move_x = dx * self.speed
        move_y = dy * self.speed
    
        new_pos = [self.pos[0] + move_x, self.pos[1] + move_y]
        unit_rect = pygame.Rect(new_pos[0]-5, new_pos[1]-5, 10, 10)
    
    # 只检测需要阻挡的设施
        if not any(f.rect.colliderect(unit_rect) for f in facilities if f.types[f.type]['block']):
             self.pos = new_pos

class Game:
    def __init__(self):
        self.facilities = self.generate_facilities()
        self.teams = {
            'red': {'units': [], 'points': 20},
            'blue': {'units': [], 'points': 20}
        }
        self.frame_count = 0
        self.dragging = False
        self.select_rect = None
        self.start_pos = (0, 0)
        self.selected_units = {'red': [], 'blue': []}
        self.spawn_initial_units()

    def generate_facilities(self):
        facilities = []
        quadtree = Quadtree(pygame.Rect(0,0,W,H))
        
        for _ in range(15):
            f_type = random.choice(list(Facility.types.keys()))
            size = Facility.types[f_type]['size']
            
            for _ in range(100):
                x = random.randint(0, W - size[0])
                y = random.randint(0, H - size[1])
                test_rect = pygame.Rect(x, y, *size)
                
                if not quadtree.query(test_rect):
                    facilities.append(Facility(f_type, (x,y)))
                    quadtree.insert(test_rect)
                    break
        return facilities

    def spawn_initial_units(self):
        for team in ['red', 'blue']:
            base_x = 200 if team == 'red' else W-200
            for _ in range(5):
                pos = (base_x + random.randint(-50,50), 
                      H//2 + random.randint(-50,50))
                self.teams[team]['units'].append(Unit(team, 'Soldier', pos))
            
            engineer = Unit(team, 'Engineer', (base_x, H//2))
            self.teams[team]['units'].append(engineer)

    def spawn_unit(self, team, utype):
        cost = {'Soldier':1, 'Engineer':10, 'Flyer':25}[utype]
        if self.teams[team]['points'] >= cost:
            self.teams[team]['points'] -= cost
            base_x = 200 if team == 'red' else W-200
            pos = (base_x + random.randint(-50,50), H//2 + random.randint(-50,50))
            self.teams[team]['units'].append(Unit(team, utype, pos))

    def move_team_units(self, team, dx, dy):
        if dx == 0 and dy == 0:
            return
        
        length = math.hypot(dx, dy)
        if length == 0:
      
