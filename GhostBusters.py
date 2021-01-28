import sys
import math
# To debug: print("Debug messages...", file=sys.stderr, flush=True)


class Vec2:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def opposite(self):
        return (16000 - self.x, 9000 - self.y)

    def dist(self, other):
        return Math.sqrt(
            Math.pow(self.x - other.x, 2) + Math.pow(self.y - other.y))

    def __str__(self):
        return "({x}, {y})".format(x=str(self.x), y=str(self.y))


class Entity:
    def __init__(self):
        self.entity_id = None
        self.entity_type = None
        self.entity_role = None
        self.pos = None
        self.state = None
        self.value = None
        self.last_seen = None

    def update(self, pos, state, value):
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
        string += prefix + "tyoe: " + str(self.entity_type) + suffix
        string += prefix + "role: " + str(self.entity_role) + suffix
        string += prefix + "pos: " + str(self.pos) + suffix
        string += prefix + "state: " + str(self.state) + suffix
        string += prefix + "value: " + str(self.value) + suffix
        string += prefix + "last_seen: " + str(self.last_seen) + suffix
        return string


class Ghost(Entity):
    def __init__(self):
        super().__init__()


class Unit(Entity):
    def __init__(self, isAlly):
        super().__init__()
        self.isAlly = isAlly
        self.basePos = entities.allies.getBasePos(
        ) if isAlly else entities.enemies.getBasePos()


class Support(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)


class Catcher(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)

    def getNextMove(self):
        if state == 1:
            return
        elif state == 4:
            return
        else:  #nothing
            return
            #TODO do implementation
        print(entities.ghost_count, file=sys.stderr, flush=True)


class Hunter(Unit):
    def __init__(self, isAlly):
        super().__init__(isAlly)


class Team:
    def __init__(self, isAlly):
        self.hunter = Hunter(isAlly)
        self.catcher = Catcher(isAlly)
        self.support = Support(isAlly)
        self.isAlly = isAlly
        self.units = [self.hunter, self.catcher, self.support]

    def updateNotSeen(self):
        self.hunter.updateNotSeen()
        self.catcher.updateNotSeen()
        self.support.updateNotSeen()

    def getBasePos(self):
        if (self.isAlly and entities.my_team_id == 0) or (
                not self.isAlly and entities.my_team_id == 1):
            return Vec2(0, 0)
        else:
            return Vec2(0, 0).opposite()

    def __str__(self):
        prefix = "   "
        suffix = "\n"
        string = "\n"
        string += prefix + "hunter: " + str(self.hunter) + suffix
        string += prefix + "catcher: " + str(self.catcher) + suffix
        string += prefix + "support: " + str(self.support) + suffix
        return string


class Entities:
    def __init__(self, busters_per_player, ghost_count, my_team_id):
        self.busters_per_player = busters_per_player
        self.ghost_count = ghost_count
        self.my_team_id = my_team_id

        self.allies = Team(True)
        self.enemies = Team(False)
        self.ghosts = [Ghost() for g in range(ghost_count)]

    def update(self, entities_count):

        # Increse the not_seen timer for all entities
        self.allies.updateNotSeen()
        self.enemies.updateNotSeen()
        for g in self.ghosts:
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
                self.ghosts[entity_id].update(Vec2(x, y), state, value)
            elif entity_type == self.my_team_id:
                if entity_role == 0:
                    self.allies.hunter.update(Vec2(x, y), state, value)
                elif entity_role == 1:
                    self.allies.catcher.update(Vec2(x, y), state, value)
                elif entity_role == 2:
                    self.allies.support.update(Vec2(x, y), state, value)
            else:
                if entity_role == 0:
                    self.enemies.hunter.update(Vec2(x, y), state, value)
                elif entity_role == 1:
                    self.enemies.catcher.update(Vec2(x, y), state, value)
                elif entity_role == 2:
                    self.enemies.support.update(Vec2(x, y), state, value)

    def __str__(self):
        prefix = ""
        suffix = "\n"
        string = "\n"
        string += prefix + "busters_per_player: " + str(
            busters_per_player) + suffix
        string += prefix + "ghost_count: " + str(ghost_count) + suffix
        string += prefix + "my_team_id: " + str(my_team_id) + suffix
        string += prefix + "allies: " + str(self.allies) + suffix
        string += prefix + "enemies: " + str(self.enemies) + suffix
        string += prefix + "ghosts: " + str(''.join(
            str(g) for g in self.ghosts)) + suffix
        return string


# Phase 1 : SUPP stun HUNTER && CATCHER scout && HUNTER damage
# Phase 2 : SUPP follow CATCHER, stun on catch && CATCHER scout && HUNTER damage

phase = 1
turn = 0

busters_per_player = int(input())  # amount of busters you control
ghost_count = int(input())  # amount of ghosts on the map
my_team_id = int(input())  # 0 : base is top left || 1 : on the bottom right

entities = Entities(busters_per_player, ghost_count, my_team_id)

# game loop
while True:
    turn += 1
    entities_count = int(input())
    entities.update(entities_count)

    print(entities, file=sys.stderr, flush=True)
    # First the HUNTER : MOVE x y | BUST id
    # Second the GHOST CATCHER: MOVE x y | TRAP id | RELEASE
    # Third the SUPPORT: MOVE x y | STUN id | RADAR

    print("MOVE 4000 4500")
    print("MOVE 12000 4500")
    print("MOVE 8000 4500")

    entities.allies.catcher.getNextMove()
