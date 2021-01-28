import sys
import math
import random
# To debug: print("Debug messages...", file=sys.stderr, flush=True)

W = 16000
H = 9000


def update(entities_count):

    # Increse the not_seen timer for all entities
    allies.updateNotSeen()
    enemies.updateNotSeen()
    for g in ghosts:
        g.updateNotSeen()

    for i in range(entities_count):
        entity_id, x, y, entity_type, entity_role, state, value = [
            int(j) for j in input().split()
        ]
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # entity_role: -1 for ghosts, 0 for the HUNTER, 1 for the GHOST CATCHER and 2 for the SUPPORT
        # entity_id: buster id or ghost id
        # x,y: position of this buster / ghost
        # state: For busters: 0=idle, 1=carrying a ghost. For ghosts: remaining hp.
        # value: For busters: Ghost id carried/busted or number of turns left when stunned.
        #                     For ghosts: number of busters attempting to trap this ghost.

        if entity_type == -1:
            ghosts[entity_id].update(Vec2(x, y), state, value, entity_id)
        elif entity_type == my_team_id:
            if entity_role == 0:
                allies.hunter.update(Vec2(x, y), state, value, entity_id)
            elif entity_role == 1:
                allies.catcher.update(Vec2(x, y), state, value, entity_id)
            elif entity_role == 2:
                allies.support.update(Vec2(x, y), state, value, entity_id)
        else:
            if entity_role == 0:
                enemies.hunter.update(Vec2(x, y), state, value, entity_id)
            elif entity_role == 1:
                enemies.catcher.update(Vec2(x, y), state, value, entity_id)
            elif entity_role == 2:
                enemies.support.update(Vec2(x, y), state, value, entity_id)


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
        return math.sqrt(
            math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))

    def __str__(self):
        return "{x} {y}".format(x=str(self.x), y=str(self.y))


class Entity:
    def __init__(self):
        self.entity_id = None
        self.entity_type = None
        self.entity_role = None
        self.pos = None
        self.state = None
        self.value = None
        self.last_seen = None

    def update(self, pos, state, value, entity_id, entity_type, entity_role):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.entity_role = entity_role
        self.pos = Vec2(pos.x, pos.y)
        self.state = state
        self.value = value
        self.last_seen = 0

    def updateNotSeen(self):
        if (self.last_seen != None):
            self.last_seen += 1

    def __str__(self):
        prefix = "      "
        suffix = "\n"
        string = "\n"
        string += prefix + "id: " + str(self.entity_id) + suffix
        string += prefix + "type: " + str(self.entity_type) + suffix
        string += prefix + "role: " + str(self.entity_role) + suffix
        string += prefix + "pos: " + str(self.pos) + suffix
        string += prefix + "state: " + str(self.state) + suffix
        string += prefix + "value: " + str(self.value) + suffix
        string += prefix + "last_seen: " + str(self.last_seen) + suffix
        return string


class Team:
    def __init__(self, isAlly):
        self.hunter = Hunter(isAlly)
        self.catcher = Catcher(isAlly)
        self.support = Support(isAlly)
        self.units = [self.hunter, self.catcher, self.support]

    def updateNotSeen(self):
        self.hunter.updateNotSeen()
        self.catcher.updateNotSeen()
        self.support.updateNotSeen()

    def __str__(self):
        prefix = "   "
        suffix = "\n"
        string = "\n"
        string += prefix + "hunter: " + str(self.hunter) + suffix
        string += prefix + "catcher: " + str(self.catcher) + suffix
        string += prefix + "support: " + str(self.support) + suffix
        return string


class Ghost(Entity):
    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        self.entity_id == other.entity_id

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id, -1, -1)


class Unit(Entity):
    def __init__(self, isAlly):
        super().__init__()
        self.isAlly = isAlly
        self.basePos = self.getBasePos()

    def update(self, pos, state, value, entity_id, entity_type, entity_role):
        if value != 0:
            ghosts[value].carried = True
        return super().update(pos, state, value, entity_id, entity_type,
                              entity_role)

    def getNearestGhost(self):
        dist = None
        ghost = None
        for g in ghosts:
            if g.last_seen == None:
                continue
            d = self.pos.dist(g.pos) + g.last_seen * 20
            if dist == None or d < dist:
                dist = d
                ghost = g
        return ghost

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
        out = ""
        if self.state == 1:  # carry a ghost
            if self.pos.dist(self.basePos) >= 1600:  # in base range
                out = "MOVE {x} {y}".format(x=self.basePos.x, y=self.basePos.y)
            else:
                ghosts[self.value].last_seen = None
                out = "RELEASE"
        else:  # carry nothing || stun || TRAPING
            nearestGhost = self.getNearestGhost()
            if nearestGhost != None:
                if self.pos.dist(nearestGhost.pos) > 1760:
                    out = "MOVE {x} {y}".format(x=nearestGhost.pos.x,
                                                y=nearestGhost.pos.y)
                else:
                    if self.pos.dist(nearestGhost.pos) < 900:
                        backward = (nearestGhost.pos -
                                    self.pos).normalized().invert()
                        out = "MOVE {x} {y}".format(x=backward.x, y=backward.y)
                    else:
                        print(nearestGhost, file=sys.stderr, flush=True)
                        out = "TRAP {id}".format(id=nearestGhost.entity_id)
            else:
                randomPos = Vec2(random.randint(0, W), random.randint(0, H))
                out = "MOVE {x} {y}".format(x=randomPos.x, y=randomPos.y)
        return out

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id,
                       (0 if (self.isAlly and my_team_id == 0) or
                        (not self.isAlly and my_team_id == 1) else 1), 1)


class Hunter(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)

    def getNextMove(self):
        out = ""
        if (True):  # carry nothing || STUN || busting
            nearestGhost = self.getNearestGhost()
            if nearestGhost != None:
                if self.pos.dist(nearestGhost.pos) > 1760:
                    out = "MOVE {x} {y}".format(x=nearestGhost.pos.x,
                                                y=nearestGhost.pos.y)
                else:
                    if self.pos.dist(nearestGhost.pos) < 900:
                        backward = (nearestGhost.pos -
                                    self.pos).normalized().invert()
                        out = "MOVE {x} {y}".format(x=backward.x, y=backward.y)
                    else:
                        print(nearestGhost, file=sys.stderr, flush=True)
                        out = "BUST {id}".format(id=nearestGhost.entity_id)
            else:
                randomPos = Vec2(random.randint(0, W), random.randint(0, H))
                out = "MOVE {x} {y}".format(x=randomPos.x, y=randomPos.y)
        return out

    def update(self, pos, state, value, entity_id):
        super().update(pos, state, value, entity_id,
                       (0 if (self.isAlly and my_team_id == 0) or
                        (not self.isAlly and my_team_id == 1) else 1), 0)


class HeatMap():
    def __init__(self):
        super().__init__()


# Phase 1 : SUPP stun HUNTER && CATCHER scout && HUNTER damage
# Phase 2 : SUPP follow CATCHER, stun on catch && CATCHER scout && HUNTER damage

phase = 1
turn = 0

busters_per_player = int(input())  # amount of busters you control
ghost_count = int(input())  # amount of ghosts on the map
my_team_id = int(input())  # 0 : base is top left || 1 : on the bottom right

allies = Team(True)
enemies = Team(False)
ghosts = [Ghost() for g in range(ghost_count)]

# game loop
while True:
    turn += 1
    entities_count = int(input())
    update(entities_count)

    # print(allToString(), file=sys.stderr, flush=True)

    # First the HUNTER : MOVE x y | BUST id
    # Second the GHOST CATCHER: MOVE x y | TRAP id | RELEASE
    # Third the SUPPORT: MOVE x y | STUN id | RADAR

    print(allies.hunter.getNextMove())
    print(allies.catcher.getNextMove())
    print(allies.support.getNextMove())
