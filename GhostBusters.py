import sys
import math
import random
# To debug: print("Debug messages...", file=sys.stderr, flush=True)

W = 16000
H = 9000
TILE = 1000


def update(entities_count):
    for g in visible:
        g.updated = False

    for i in range(entities_count):
        entity_id, x, y, entity_type, entity_role, state, value = [
            int(j) for j in input().split()
        ]
        if entity_type == my_team_id:
            if entity_role == 0:
                hunter.update(Vec2(x, y), state, value, entity_id)
            elif entity_role == 1:
                catcher.update(Vec2(x, y), state, value, entity_id)
            elif entity_role == 2:
                support.update(Vec2(x, y), state, value, entity_id)
        else:
            if entity_role == -1:
                found = False
                for g in visible:
                    if g.id == entity_id:
                        g.update(Vec2(x, y), state, value, entity_id)
                        found = True
                        break
                if not found:
                    new = Ghost()
                    new.update(Vec2(x, y), state, value, entity_id)
                    visible.add(new)

    for g in visible.copy():
        if not g.updated:
            visible.remove(g)


def allToString():
    prefix = ""
    suffix = "\n"
    string = "\n"
    string += prefix + "busters_per_player: " + str(
        busters_per_player) + suffix
    string += prefix + "ghost_count: " + str(ghost_count) + suffix
    string += prefix + "my_team_id: " + str(my_team_id) + suffix
    string += prefix + "allies: " + str(allies) + suffix
    string += prefix + "enemies: " + str(enemies) + suffix
    string += prefix + "ghosts: " + str(''.join(str(g)
                                                for g in ghosts)) + suffix
    return string


class Vec2:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def opposite(self):
        return Vec2(W - self.x, H - self.y)

    def invert(self):
        return Vec2(-self.x, -self.y)

    def normalized(self):
        return Vec2(100 * (float(self.x) / self.norm()),
                    100 * (float(self.y) / self.norm()))

    def norm(self):
        return self.dist(Vec2(0, 0))

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, value):
        return Vec2(self.x * value, self.y * value)

    def __truediv__(self, value):
        return Vec2(self.x / value, self.y / value)

    def dist(self, other):
        return math.sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))

    def toGrid(self):
        return Vec2(self.x / TILE, self.y / TILE)

    def toFrame(self):
        return Vec2(self.x * TILE, self.y * TILE)

    def __str__(self):
        return "{x} {y}".format(x=str(self.x), y=str(self.y))


class Entity:
    def __init__(self):
        self.id = None
        self.type = None
        self.role = None
        self.pos = None
        self.state = None
        self.value = None
        self.updated = False

    def update(self, pos, state, value, entity_id, entity_type, entity_role):
        self.id = entity_id
        self.type = entity_type
        self.role = entity_role
        self.pos = Vec2(pos.x, pos.y)
        self.state = state
        self.value = value
        self.updated = True

    def __str__(self):
        prefix = "      "
        suffix = "\n"
        string = "\n"
        string += prefix + "id: " + str(self.id) + suffix
        string += prefix + "type: " + str(self.type) + suffix
        string += prefix + "role: " + str(self.role) + suffix
        string += prefix + "pos: " + str(self.pos) + suffix
        string += prefix + "state: " + str(self.state) + suffix
        string += prefix + "value: " + str(self.value) + suffix
        return string


class Ghost(Entity):
    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        if other == None:
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id, -1, -1)


class Unit(Entity):
    def __init__(self, isAlly):
        super().__init__()
        self.isAlly = isAlly
        self.basePos = self.getBasePos()
        self.viewDist = 2200

    # def getNearestGhost(self):
    #     dist = None
    #     ghost = None
    #     for g in ghosts:
    #         if g.last_seen == None:
    #             continue
    #         d = self.pos.dist(g.pos) + g.last_seen * 20
    #         if dist == None or d < dist:
    #             dist = d
    #             ghost = g
    #     return ghost

    def getBasePos(self):
        if (self.isAlly and my_team_id == 0) or (not self.isAlly
                                                 and my_team_id == 1):
            return Vec2(0, 0)
        else:
            return Vec2(0, 0).opposite()


class Support(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)

    def getNextMove(self):
        out = "MOVE " + str(self.basePos)
        return out

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id,
                       (0 if (self.isAlly and my_team_id == 0) or
                        (not self.isAlly and my_team_id == 1) else 1), 2)


class Catcher(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)

    def getNextMove(self):
        out = "MOVE " + str(self.basePos)
        return out

    # def getNextMove(self):
    #     out = ""
    #     if self.state == 1:  # carry a ghost
    #         if self.pos.dist(self.basePos) >= 1600:  # in base range
    #             out = "MOVE {x} {y}".format(x=self.basePos.x, y=self.basePos.y)
    #         else:
    #             ghosts[self.value].last_seen = None
    #             out = "RELEASE"
    #     else:  # carry nothing || stun || TRAPING
    #         nearestGhost = self.getNearestGhost()
    #         if nearestGhost != None:
    #             if self.pos.dist(nearestGhost.pos) > 1760:
    #                 out = "MOVE {x} {y}".format(x=nearestGhost.pos.x,
    #                                             y=nearestGhost.pos.y)
    #             else:
    #                 if self.pos.dist(nearestGhost.pos) < 900:
    #                     backward = (nearestGhost.pos -
    #                                 self.pos).normalized().invert()
    #                     out = "MOVE {x} {y}".format(x=backward.x, y=backward.y)
    #                 else:
    #                     print(nearestGhost, file=sys.stderr, flush=True)
    #                     out = "TRAP {id}".format(id=nearestGhost.entity_id)
    #         else:
    #             randomPos = Vec2(random.randint(0, W), random.randint(0, H))
    #             out = "MOVE {x} {y}".format(x=randomPos.x, y=randomPos.y)
    #     return out

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id,
                       (0 if (self.isAlly and my_team_id == 0) or
                        (not self.isAlly and my_team_id == 1) else 1), 1)


class Hunter(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)

    def getNextMove(self):
        out = ""

        target = self.getOptimalGhost()
        if (target != None):
            if self.pos.dist(target.pos) > 1760:
                out = "MOVE {x} {y}".format(x=target.pos.x, y=target.pos.y)
            else:
                if self.pos.dist(target.pos) < 900:
                    backward = (target.pos - self.pos).normalized().invert()
                    out = "MOVE {x} {y}".format(x=backward.x, y=backward.y)
                else:
                    print(target, file=sys.stderr, flush=True)
                    out = "BUST {id}".format(id=target.id)
                    if target.state == 1:
                        heat_alive.removeOne()
        else:
            targetPos = heat_alive.getMaxPos()
            out = "MOVE {x} {y}".format(x=targetPos.x, y=targetPos.y)
        return out

    def getOptimalGhost(self):
        for e in visible:
            if e.state > 0:
                return e

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id,
                       (0 if (self.isAlly and my_team_id == 0) or
                        (not self.isAlly and my_team_id == 1) else 1), 0)


class HeatMap():
    def __init__(self, number, matching_type, matching_role):
        self.width = int(W / TILE) + 1
        self.height = int(H / TILE) + 1
        self.number = number
        self.matching_type = -1
        self.matching_role = -1
        self.size = self.width * self.height
        self.heat = [[float(number / self.size) for i in range(self.width)]
                     for j in range(self.height)]

    def update(self):
        self.clear(hunter.pos, hunter.viewDist)
        self.clear(catcher.pos, catcher.viewDist)
        self.clear(support.pos, support.viewDist)
        self.updateHeat()

    def getMaxPos(self):
        current_max = 0
        blured = self.gaussBlur(self.heat, 3, 0.1)
        max_pos = None
        for y in range(self.height):
            for x in range(self.width):
                if current_max < blured[y][x]:
                    current_max = blured[y][x]
                    max_pos = Vec2(x, y).toFrame()
        return max_pos

    def increment(self, value):
        for y in range(self.height):
            for x in range(self.width):
                self.heat[y][x] += value
                if self.heat[y][x] < 0:
                    self.heat[y][x] = 0

    def gaussBlur(self, input, filterSize, sigma):
        gaussfilter = [[
            (1 / (sigma * math.sqrt(2 * math.pi))) *
            (math.exp(-((i - math.ceil(filterSize / 2))**2 +
                        (j - math.ceil(filterSize / 2))**2 / 2 * sigma**2)))
            for i in range(filterSize)
        ] for j in range(filterSize)]

        out = [[0.0 for k in range(self.width)] for l in range(self.height)]

        for x in range(self.width):
            for y in range(self.height):
                for i in range(filterSize):
                    for j in range(filterSize):
                        cx = int(x + i - int(filterSize / 2))
                        cy = int(y + j - int(filterSize / 2))
                        if cx >= 0 and cx < self.width and cy >= 0 and cy < self.height:

                            out[y][x] = out[y][x] + float(
                                gaussfilter[i][j] * input[cy][cx])
                # print("x={x} y={y}  maxX={w}  maxY={h}".format(x=x,
                #                                                y=y,
                #                                                w=self.width,
                #                                                h=self.height),
                #       file=sys.stderr,
                #       flush=True)
        return out

    def removeOne(self):
        self.number -= 1
        self.increment(-1 / self.size)

    def updateHeat(self):
        for e in visible:
            if e.type == self.matching_type and e.role == self.matching_role:
                if self.matching_type != -1 or (self.matching_type == -1
                                                and e.state > 0):
                    in_grid = e.pos.toGrid()
                    self.increment(-1 / self.size)
                    self.heat[in_grid.y][in_grid.x] += 1

    def clear(self, pos, viewDist):
        for y in range(self.height):
            for x in range(self.width):
                current = Vec2(x, y).toFrame()
                if pos.dist(current) < viewDist:
                    self.increment(self.heat[y][x] / self.size)
                    self.heat[y][x] = 0.0

    def __str__(self):
        string = ""
        total = 0.0
        gauss = self.gaussBlur(self.heat, 3, 0.1)
        for y in range(self.height):
            for x in range(self.width):
                total += self.heat[y][x]
                # string += str(round(self.heat[y][x] * 10000) / 10000) + " "
                string += str(round(gauss[y][x])) + " "
            string += "\n"

        return string + "\n" + str(total)


# Phase 1 : SUPP stun HUNTER && CATCHER scout && HUNTER damage
# Phase 2 : SUPP follow CATCHER, stun on catch && CATCHER scout && HUNTER damage

phase = 1
turn = 0
busters_per_player = int(input())  # amount of busters you control
ghost_count = int(input())  # amount of ghosts on the map
my_team_id = int(input())  # 0 : base is top left || 1 : on the bottom right

hunter = Hunter(True)
catcher = Catcher(True)
support = Support(True)
visible = set()
heat_alive = HeatMap(ghost_count, -1, -1)

# game loop
while True:
    turn += 1
    update(int(input()))
    heat_alive.update()
    print(heat_alive, file=sys.stderr, flush=True)
    # print(allToString(), file=sys.stderr, flush=True)

    # First the HUNTER : MOVE x y | BUST id
    # Second the GHOST CATCHER: MOVE x y | TRAP id | RELEASE
    # Third the SUPPORT: MOVE x y | STUN id | RADAR
    print(hunter.getNextMove())
    print(catcher.getNextMove())
    print(support.getNextMove())
