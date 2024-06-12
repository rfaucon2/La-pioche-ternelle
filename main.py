import pyxel as px
import random

def clamp(x, l, h):
    return min(max(x,l),h)

WINSIZE = 128
TILE_SIZE = 8

TILES = {
    "air": (0, 15, 1), #(u, v, variantes)
    "cave_air": (1, 1, 1),
    "clouds": (1, 15, 4),
    "top_grass": (0, 6, 3),
    "dirt": (0, 8, 3),
    "stone": (0, 7, 4),
    "brick": (0, 9, 1),
    "chest": (0, 4, 1),
    "bomb":(0, 13, 1)
}

ENERGY_LUT = {
    "dirt": 1,
    "stone": 2,
    "brick": 3,
    "chest": -5,
    "bomb": 5
}

GROUND_TILES = ["brick", "stone", "dirt", "air"]
CLOSE_CAVE_TILES = ["dirt", "dirt", "dirt", "cave_air", "cave_air", "stone"]
MEDIUM_CAVE_TILES = ["dirt", "dirt", "cave_air", "stone", "stone", "brick"]
DEEP_CAVE_TILES = ["stone", "brick"]

class App:
    def __init__(self):
        px.init(WINSIZE, WINSIZE, title="Ceci est un putain de jeu sivouplé aimez le", fps=60, quit_key=px.KEY_ESCAPE)
        px.mouse(True)
        
        self.buttons = []
        self.reset_button = Button(11.5 * TILE_SIZE, 11 * TILE_SIZE, 9, "Reset", self._reset_game)
        self.buttons.append(self.reset_button)
        px.load("res.pyxres")

        random.seed(None)
        px.nseed(random.randint(0, 2**20))
        self.highscore = 0
        self.depth = 0
        self._reset_game()

        px.run(self.update, self.draw)
    
    def _reset_game(self):
        if self.depth > self.highscore:
            self.highscore = self.depth
        self.perso = Perso(5,0, 30 + self.highscore // 2)

        self.depth = 0 # Depth of the top most line 
        self.layout = []
        for _ in range(3):
            self.layout.append([(TILES["air"] if random.randint(0, 3) else TILES["clouds"]) for _ in range(11)])
        for _ in range(3):
            self.layout.append([TILES["air"]] * 11)

        self.layout.append([TILES["top_grass"]] * 11)
        self.layout.append([TILES["dirt"]] * 11)

        for _ in range(8):
            self.layout.append([TILES[CLOSE_CAVE_TILES[random.randrange(0, len(CLOSE_CAVE_TILES))]] for _ in range(11)])
            
    def update(self):
        if self.perso.get_energy() > 0:
            moves = self.perso.update()
            self.depth += moves[1]
            if moves[1]:
                self._update_generate_more()
            
            tile = self.layout[5][self.perso.x]

            if tile != TILES["cave_air"] and self.depth > 0:
                self.layout[5][self.perso.x] = TILES["cave_air"]
                energy = 0
                for i in range(len(ENERGY_LUT.keys())):
                    if TILES[list(ENERGY_LUT.keys())[i]] == tile:
                        energy = ENERGY_LUT[list(ENERGY_LUT.keys())[i]]
                self.perso.use_energy(energy)
            
                

        for b in self.buttons:
            b.update()
            rect = b.get_rect()
            if px.btnp(px.MOUSE_BUTTON_LEFT):
                if rect[0] < px.mouse_x < rect[2] and rect[1] < px.mouse_y < rect[3]:
                    b.get_callback()()
    
    def _update_generate_more(self):
        
        del self.layout[0]
        
        tileset = DEEP_CAVE_TILES
        if self.depth < 20:
            tileset = CLOSE_CAVE_TILES
        elif self.depth > 20 and self.depth < 50:
            tileset = MEDIUM_CAVE_TILES
        
        new_line = [TILES[tileset[random.randrange(0, len(tileset))]] for _ in range(11)]
        for tile_index in range(len(new_line)):
            if px.rndf(0,1) < 0.03:
                new_line[tile_index] = TILES["chest"]
            if px.rndf(0,1) < 0.07:
                new_line[tile_index] = TILES["bomb"]
        self.layout.append(new_line)

    def draw(self):
        px.cls(0)
        debug = False
        if not debug:
            self._draw_menu()
            if self.perso.get_energy() > 0:
                self._draw_layout()
                self.perso.draw()
            else:
                self._draw_death_screen()
        else:
            px.blt(0,0,0,0,0,20*TILE_SIZE, 20*TILE_SIZE, colkey=0)

    def _draw_death_screen(self):
        # px.text(2 * TILE_SIZE, 7.5 * TILE_SIZE, "Plus d'energie", 8)
        px.blt(0,0,1,0,8,80,128)

    def _draw_layout(self):
        for y in range(len(self.layout)):
            for x in range(len(self.layout[y])):
                
                u, v, var = self.layout[y][x]
                u *= TILE_SIZE
                v *= TILE_SIZE
                px.blt(x * TILE_SIZE, y * TILE_SIZE, 0, u, v, TILE_SIZE, TILE_SIZE, colkey= (7 if v == TILES["bomb"][1] * TILE_SIZE else 0))
        # Draw energy bar
        px.blt(0.5 * TILE_SIZE , 0.5 * TILE_SIZE , 0, 0, 5 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE, colkey=0)
        px.rect(0.5 * TILE_SIZE + 1, 0.5 * TILE_SIZE + 1, (3*TILE_SIZE - 5) * (self.perso.get_energy() / self.perso.get_max_energy()), TILE_SIZE-2, 11)

        # Display depth
        px.text(11.7 * TILE_SIZE, 3 * TILE_SIZE, f"Depth:{self.depth}", 7)
    
    def _draw_menu(self):
        # Draw background
        for x in range (5):
            for y in range(16):
                px.rect(TILE_SIZE*(11+x), TILE_SIZE * y, TILE_SIZE, TILE_SIZE, abs(int(px.noise(x/10, y/10, px.frame_count/60)*7)))
            
        # Draw energy bar
        px.blt(0.5 * TILE_SIZE , 0.5 * TILE_SIZE , 0, 0, 5 * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE, colkey=0)
        px.rect(0.5 * TILE_SIZE +1, 0.5 * TILE_SIZE +1, (3*TILE_SIZE - 5) * (self.perso.get_energy() / self.perso.get_max_energy()), TILE_SIZE-2, 11)
        # Display buttons
        for b in self.buttons:
            b.draw()

        # Display highscore
        px.text(11.7 * TILE_SIZE, TILE_SIZE, f"Best:{self.highscore}", 7)


class Button:
    WIDTH = 4 * TILE_SIZE
    HEIGHT = 1.5 * TILE_SIZE

    def __init__(self, x, y, col, string, callback):
        self.x = x
        self.y = y
        self.col = col
        self.string = string
        self.callback = callback

        self.hovered = False

    def update(self):
        self.hovered = (self.x <= px.mouse_x <= self.x + self.WIDTH and self.y <= px.mouse_y <= self.y + self.HEIGHT)

    def draw(self):
        px.rect(self.x, self.y, self.WIDTH, self.HEIGHT, self.col)
        
        if self.hovered:
            px.rectb(self.x, self.y, self.WIDTH, self.HEIGHT, 10)

        px.text(self.x + 3, self.y + 3, self.string, 1)
    
    def get_rect(self):
        return (self.x , self.y , (self.x + self.WIDTH) , (self.y + self.HEIGHT))

    def get_callback(self):
        return self.callback


class Perso:
    def __init__(self, x, y, max_energy):
        self.x = x
        self.y = y
        self.input_buffer = [0, 0]

        self.money = 0
        
        self.energy = max_energy
        self.max_energy = max_energy
        
    def update(self):
        ret = self._update_move()
        return ret
    
    def _update_move(self):
        if px.btn(px.KEY_LEFT):
            self.input_buffer[0] -= 1
        if px.btn(px.KEY_RIGHT):
            self.input_buffer[0] += 1
        if px.btn(px.KEY_DOWN):
            self.input_buffer[1] += 1
        self.input_buffer = [clamp(self.input_buffer[0], -1, 1),clamp(self.input_buffer[1], 0, 1)]
        if px.frame_count % 10 != 0: return [0,0]
        temp = self.input_buffer
        self.input_buffer = [0,0]
        if temp[0] != 0:
            temp[1] = 0
        self.x += temp[0]
        self.y += temp[1]
        self.x = clamp(self.x,0,10)
        self.y = max(self.y, 0)
        return temp
        
    def draw(self):
        px.blt(self.x*TILE_SIZE, 5*TILE_SIZE, 0, 0, 2*TILE_SIZE, TILE_SIZE, TILE_SIZE, colkey=7)
    
    def get_energy(self):
        return self.energy
    def get_max_energy(self):
        return self.max_energy
    def use_energy(self, e):
        self.energy -= e
        clamp(self.energy,0, self.max_energy)

    def get_money(self):
        return self.money
    def increase_money(self):
        self.max_money += 5

App()