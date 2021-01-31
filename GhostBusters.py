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
            found = False
            for g in visible:
                if g.id == entity_id and g.type == entity_type:
                    g.update(Vec2(x, y), state, value, entity_id)
                    found = True
                    break
            if not found:
                if entity_role == -1:
                    new = Ghost()
                elif entity_role == 0:
                    new = Hunter(False)
                elif entity_role == 1:
                    new = Catcher(False)
                elif entity_role == 2:
                    new = Support(False)
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
        norm = self.norm()
        if norm == 0:
            return Vec2(100, 0)
        else:
            return Vec2(100 * (float(self.x) / norm),
                        100 * (float(self.y) / norm))

    def norm(self):
        return self.dist(Vec2(0, 0))

    def get(self):
        return (self.x, self.y)

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
        self.type = -1

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
        self.type = 1 if ((isAlly and my_team_id == 1) or
                          (not isAlly and my_team_id == 0)) else 0
        self.basePos = self.getBasePos()
        self.viewDist = 2200

    def getBasePos(self):
        if (self.isAlly and my_team_id == 0) or (not self.isAlly
                                                 and my_team_id == 1):
            return Vec2(0, 0)
        else:
            return Vec2(0, 0).opposite()


class Support(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)
        self.cooldown = 0

    def getNextMove(self):
        self.cooldown -= 1
        out = ""
        target = self.getTarget()
        if (target != None):
            if self.pos.dist(
                    target.pos
            ) > 1760 or self.cooldown > 0 or target.state == 0:
                close = self.getCloseDead()
                if close != None:
                    offset = (close.pos - self.basePos).normalized() * 10
                    out = "MOVE {x} {y} 🤚".format(x=close.pos.x + offset.x,
                                                  y=close.pos.y + offset.y)
                else:
                    out = "MOVE {x} {y} 🔫{cd}".format(
                        x=target.pos.x,
                        y=target.pos.y,
                        cd=(self.cooldown if self.cooldown > 0 else ""))
            else:
                out = "STUN {id} STUN".format(id=target.id)
                self.cooldown = 20
        else:
            targetPos = heat_catcher.getMaxPos()
            out = "MOVE {x} {y} 🔍".format(x=targetPos.x, y=targetPos.y)
        return out

    def getCloseDead(self):
        for e in visible:
            if e.type == -1 and e.state == 0 and e.pos.dist(self.pos) < 1100:
                return e

    def getTarget(self):
        for e in visible:
            if e.role == 1:
                return e

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

    def getNextMove(self):
        out = ""
        if self.state == 1:  # carry a ghost
            if self.pos.dist(self.basePos) >= 1600:  # in base range
                out = "MOVE {x} {y} 🏠".format(x=self.basePos.x,
                                              y=self.basePos.y)
            else:
                out = "RELEASE RELEASE"
                heat_dead.removeOne()
        else:  # carry nothing || stun || TRAPING
            target = self.getOptimalGhost()
            if (target != None):
                if self.pos.dist(target.pos) > 1760:
                    out = "MOVE {x} {y} 👀".format(x=target.pos.x,
                                                  y=target.pos.y)
                else:
                    if self.pos.dist(target.pos) < 900:
                        backward = (target.pos -
                                    self.pos).normalized().invert()
                        out = "MOVE {x} {y} 🥾".format(x=backward.x,
                                                      y=backward.y)
                    else:
                        if target.state == 0:
                            # print(target, file=sys.stderr, flush=True)
                            out = "TRAP {id} TRAP".format(id=target.id)
                        else:
                            out = "MOVE {x} {y} ⏲".format(x=self.pos.x,
                                                          y=self.pos.y)
            else:
                targetPos = heat_dead.getMaxPos()
                out = "MOVE {x} {y} 🔍".format(x=targetPos.x, y=targetPos.y)
        return out

    def getOptimalGhost(self):
        min_dist = None
        ghost = None
        for e in visible:
            if e.type == -1 and (e.state == 0):
                dist = e.pos.dist(self.basePos) + e.pos.dist(self.pos)
                if min_dist == None or dist < min_dist:
                    ghost = e
                    min_dist = dist
        if ghost == None:
            for e in visible:
                if e.type == -1 and e.state < 10 and e.value > 0:
                    dist = e.pos.dist(self.basePos) + e.pos.dist(self.pos)
                    if min_dist == None or dist < min_dist:
                        ghost = e
                        min_dist = dist
        return ghost

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
        dead = self.getDeadGhost()
        if ((catcher.state == 2 or catcher.state == 1
             or catcher.pos.dist(self.pos) > 4000) and dead != None):
            #PUSH
            target = dead
            offset = (target.pos - self.basePos).normalized() * 10
            out = "MOVE {x} {y} 🤚".format(x=target.pos.x + offset.x,
                                          y=target.pos.y + offset.y)
        elif (target != None):
            if self.pos.dist(target.pos) > 1760:
                out = "MOVE {x} {y} 👀".format(x=target.pos.x, y=target.pos.y)
            else:
                if self.pos.dist(target.pos) < 900:
                    backward = (target.pos - self.pos).normalized().invert()
                    out = "MOVE {x} {y} 🥾".format(x=backward.x, y=backward.y)
                else:
                    out = "BUST {id} 🧬".format(id=target.id)
                    if target.state == 1:
                        heat_alive.removeOne()
                        heat_lowHP.removeOne()
        else:
            targetPos = heat_lowHP.getMaxPos(
            ) if phase <= 2 else heat_alive.getMaxPos()
            out = "MOVE {x} {y} 🔍".format(x=targetPos.x, y=targetPos.y)
        return out

    def getDeadGhost(self):
        min_dist = None
        ghost = None
        for e in visible:
            if e.type == -1 and (e.state == 0):
                dist = e.pos.dist(self.pos)
                if (min_dist == None or dist < min_dist) and e.pos.dist(
                        catcher.pos) > 400 and e.pos.dist(
                            support.pos) > 400 and dist < 4000:
                    ghost = e
                    min_dist = dist
        return ghost

    def getOptimalGhost(self):
        min_dist = None
        ghost = None
        for e in visible:
            if e.type == -1 and ((phase <= 2 and e.state > 0 and e.state < 25)
                                 or (phase > 2 and e.state > 0)):
                dist = e.pos.dist(self.pos)
                if min_dist == None or dist < min_dist:
                    ghost = e
                    min_dist = dist
        return ghost

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id,
                       (0 if (self.isAlly and my_team_id == 0) or
                        (not self.isAlly and my_team_id == 1) else 1), 0)


class HeatMap():
    def __init__(self, number, matching_type, matching_role, matching_state,
                 unit):
        self.width = int(W / TILE) + 1
        self.height = int(H / TILE) + 1
        self.number = number
        self.matching_type = matching_type
        self.matching_role = matching_role
        self.matching_state = matching_state
        self.unit = unit
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
        blured = self.addProximity(self.gaussBlur())
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

    def gaussBlur(self):
        F_SIZE = 7
        SIGMA = 2
        main_filter = self.gaussFilter(F_SIZE, SIGMA)

        out = [[0.0 for k in range(self.width)] for l in range(self.height)]

        for x in range(self.width):
            for y in range(self.height):
                for i in range(F_SIZE):
                    for j in range(F_SIZE):
                        cx = int(x + i - int(F_SIZE / 2))
                        cy = int(y + j - int(F_SIZE / 2))
                        if cx >= 0 and cx < self.width and cy >= 0 and cy < self.height:
                            out[y][x] += main_filter[i][j] * self.heat[cy][cx]
        return out

    def addProximity(self, arr):
        P_SIZE = 7
        POWER = 0.4
        SIGMA = 5
        proximity_filter = self.gaussFilter(P_SIZE, SIGMA)

        x, y = self.unit.pos.toGrid().get()
        out = arr.copy()
        for i in range(P_SIZE):
            for j in range(P_SIZE):
                cx = int(x + i - int(P_SIZE / 2))
                cy = int(y + j - int(P_SIZE / 2))
                if cx >= 0 and cx < self.width and cy >= 0 and cy < self.height:
                    out[cy][cx] += proximity_filter[i][j] * POWER
        return out

    def gaussFilter(self, size, sigma):
        out = [[0.0 for k in range(size)] for l in range(size)]
        for i in range(int(-(size) / 2), int((size) / 2) + 1):
            for j in range(int(-(size) / 2), int((size) / 2) + 1):
                x0 = int((size) / 2)
                y0 = int((size) / 2)
                x = i + x0
                y = j + y0
                out[y][x] = math.exp(-((x - x0)**2 + (y - y0)**2) / 2 / sigma /
                                     sigma)
        return out

    def removeOne(self):
        self.number -= 1
        self.increment(-1 / self.size)

    def updateHeat(self):
        global phase
        for e in visible:
            if e.type == self.matching_type and e.role == self.matching_role:
                if (self.matching_state == "lowHP" and e.state > 0
                        and e.state < 20
                    ) or (self.matching_state == "alive" and e.state > 0) or (
                        self.matching_state == "dead"
                        and e.state == 0) or self.matching_state == "any":
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

    def getTotal(self):
        total = 0.0
        for y in range(self.height):
            for x in range(self.width):
                total += self.heat[y][x]
        return total

    def __str__(self):
        string = "heat = [\n"
        total = 0.0
        for y in range(self.height):
            for x in range(self.width):
                total += self.heat[y][x]
                string += str(round(self.heat[y][x] * 100) / 100) + " "
            string += ";\n"
        string += "];\n"
        return string + "\n" + str(total)


phase = 1
turn = 0
busters_per_player = int(input())  # amount of busters you control
ghost_count = int(input())  # amount of ghosts on the map
my_team_id = int(input())  # 0 : base is top left || 1 : on the bottom right

hunter = Hunter(True)
catcher = Catcher(True)
support = Support(True)
visible = set()

heat_lowHP = HeatMap(ghost_count, -1, -1, "lowHP", hunter)
heat_alive = HeatMap(ghost_count, -1, -1, "alive", hunter)
heat_dead = HeatMap(ghost_count, -1, -1, "dead", catcher)
heat_catcher = HeatMap(ghost_count, my_team_id + 1 % 2, 1, "any", support)

while True:
    turn += 1
    update(int(input()))
    heat_lowHP.update()
    heat_alive.update()
    heat_dead.update()
    heat_catcher.update()

    if (heat_alive.getTotal() <= ghost_count / 2
            or heat_dead.getTotal() <= ghost_count / 2
            or turn > 100) and phase <= 2:
        phase = 3

    print(phase, file=sys.stderr, flush=False)

    # First the HUNTER : MOVE x y | BUST id
    # Second the GHOST CATCHER: MOVE x y | TRAP id | RELEASE
    # Third the SUPPORT: MOVE x y | STUN id | RADAR
    print(hunter.getNextMove())
    print(catcher.getNextMove())
    print(support.getNextMove())
