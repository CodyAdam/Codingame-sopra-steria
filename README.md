# My rank : 35/168 [Leaderboard](https://www.codingame.com/hackathon/sopra-steria-coding-challenge/leaderboard/global)
# 

# Coding-Games-sopra-steria

Sopra Steria vous lance un défi de 10 jours, sous forme d’un hackathon en France uniquement. Le concours débute le 21 Janvier à 18h00 et finit le 31 janvier à 23h59.

## Objectif

Capturer plus de fantômes que l'équipe adverse.

## Règles

Le jeu se déroule sur une carte de largeur 16001 et de hauteur 9001 . Les coordonnées X=0, Y=0 représentent le coin supérieur gauche.

Chaque joueur contrôle une équipe de plusieurs busters. Chaque équipe commence à un coin opposé de la carte, près de sa base. Les Fantômes sont répartis sur la carte, et doivent être capturés et ramenés à la base. Chaque fantôme capturé par un buster ou ramené à la base vaut un point. Cependant, vous pouvez perdre un point si un de vos busters relâche son fantôme ailleurs que dans votre base.

#### La carte fonctionne comme suit :

-   Il y a toujours 2 équipes en jeu.
-   Au début du jeu, chaque joueur reçoit un identifiant d'équipe. Il indique à quelle base son équipe démarre. Le coin supérieur gauche ( X=0, Y=0) est pour l'équipe 0. Le coin - inférieur droit ( X=16000, Y=9000) est pour l'équipe 1.
-   Le brouillard empêche de connaître les positions des fantômes ou des busters adverses, sauf s'ils sont dans un rayon de 2200 unités d'un de vos propres busters.
-   Chaque buster a un identifiant unique. Chaque fantôme a un identifiant unique. Un fantôme et un Buster ayant le même identifiant ne sont pas reliés.
-   Les Busters fonctionnent comme suit :
-   Chaque buster a un role précis et des actions associées :
    -   Le CHASSEUR : C'est votre premier buster, il peut utiliser BUST. Il a un contour rouge dans le visualiseur.
    -   L'ATTRAPEUR : C'est votre deuxième buster, il peut utiliser TRAP et RELEASE. Il a un contour vert dans le visualiseur.
    -   L'ASSISTANT : C'est votre premier buster, il peut utiliser STUN et RADAR. Il a un contour bleu dans le visualiseur.
-   De plus, tout les busters peuvent utilliser MOVE.
-   MOVE suivit par des coordonnées fera avancer le buster de 800 unités vers le point choisi. La position sera arrondie au plus proche entier.
-   BUST suivi d'un identifiant de fantôme permettra au buster de viser un fantôme avec son pistolet à proton, et lui faire perdre 1 point d'endurance. Cette action fonctionne - si le fantôme trouve dans un rayon inférieur 1760 unités mais supérieur à 900 unités du buster.
-   TRAP suivi d'un identifiant de fantôme permettra au buster d'essayer d'aspirer le fantôme dans son piège. Il réussira si le fantôme a 0 points d'endurance et si le fantôme - trouve dans un rayon inférieur 1760 unités mais supérieur à 900 unités du buster. Les fantômes capturés ne sont plus visibles sur la carte.
-   Un buster peut transporter au plus 1 fantôme simultanément.
-   RELEASE va ordonner au buster de relâcher le fantôme qu'il est en train de porter. Si un fantôme est relâché à moins de 1600 unités d'un coin de map étant une base, le - fantôme est retiré du jeu et le possesseur de la base marque un point.
-   STUN suivi par l'id d'un buster produira un éclair qui assomera le buster cible. Un buster assommé ne peut pas effectuer d'actions pour 10 tours. L'ASSISTANT doit recharger - son arme pendant 20 tours avant de pouvoir de nouveau assommer. Un buster assommé va relâcher tout fantôme qu'il transporte.
-   L'ASSISTANT peut assommer un adversaire dans un rayon de 1760 unités.
-   RADAR va permettre au buster de gagner en vision à travers le brouillard et ainsi être capable de voir toutes les entités dans un rayon de 4400 unités autour de lui pour le - prochain tour. L'ASSISTANT peut utiliser cette action une fois par partie.
-   Les Busters font leurs actions en même temps mais les effets liés aux actions, y compris les déplacements, sont appliqués à la fin du tour.
-   Les Fantômes fonctionnent comme suit :
-   Les fantômes sont immobiles si sur leur point de départ et que les busters se trouvent à plus de 2200 unités si le fantôme est en train de subir un BUST. Si un fantôme n'est - pas sur son point de départ il va aller vers celui ci sauf si à l'issue de ce mouvement il serait à une distance de moins de 2200 unités d'un buster. Si des busters sont - proches , il va fuir le point au barycentre des Busters proches sauf si est en train de subir un BUST.
-   Les fantômes se déplacent à une vitesse de 400 unités.
-   L'endurance ne se régénère pas.
-   Le jeu s'arrête quand tous les fantômes ont été capturés ou après une limite de 250 tours.

L'état du jeu lors d'un tour vous est donné en une liste d'entités, chacune possédant un id, position, type, role, state et value.

#### La valeur de type sera :

-   0 pour un buster de l'équipe 0.
-   1 pour un buster de l'équipe 1.
-   -1 pour un fantôme.

#### La valeur du role sera :

-   0 pour le CHASSEUR.
-   1 pour l'ATTRAPEUR.
-   2 pour l'ASSISTANT.
-   -1 pour un fantôme.

#### La valeur de state sera :

-   Pour les busters :

    -   0: Buster ne transportant pas de fantôme.
    -   1: Buster transportant un fantôme.
    -   2: Buster assommé.
    -   3: Buster en train de TRAP un fantôme.
    -   4: Buster en train de BUST un fantôme.

-   Pour les fantômes, cette valeur est leur taux d'endurance.

#### value pourra être :

-   Pour un buster:

    -   si ce buster transporte un fantôme, l'id de ce fantôme.
    -   Si ce buster est assommé, le nombre de tours avant qu'il puisse à nouveau bouger.

-   Pour un fantôme, c'est le nombre de busters en train d'essayer de le TRAP ou en train de le BUST.

### Conditions de Victoire

Avoir capturé plus de fantômes que l'équipe adverse à la fin du jeu.

### Conditions de Défaite

-   Votre programme produit une sortie invalide.
-   Votre programme dépasse la limite de temps.
-   Vous avez moins de fantôme que votre adversaire à la fin du jeu.

## Règles pour les experts

-   Les positions de départ des busters et des fantômes sont symétriques.
-   Les déplacements des fantômes se font 1 tour après vous avoir repéré.
-   Si un fantôme sort de la carte après un déplacement, ses nouvelles coordonnées sont bornées avec celles de la carte.
-   Utiliser STUN sur un buster déjà assommé, l'assommera pour 10 nouveaux tours.
-   Si un buster transportant un fantôme est assommé dans une base, le fantôme est retiré du jeu et le possesseur de la base marque un point.

## Note

Votre programme doit d'abord lire les données d'initialisation depuis l'entrée standard, puis, dans une boucle infinie, lire les données contextuelles de la partie et écrire sur la sortie standard les actions pour vos busters.

## Entrées du jeu

### Entrées d'initialisation

Ligne 1: un entier bustersPerPlayer pour le nombre de busters contrôlés par l'équipe.
Ligne 2: un entier ghostCount pour le nombre de fantômes sur la carte.
Ligne 3: un entier myTeamId l'identifiant de votre équipe.

### Entrées pour un tour de jeu

Ligne 1: un entier entities le nombre d'entités visibles par vous pour ce tour.
Les entities lignes suivantes : 6 entiers séparés par des espaces, entityId , x , y , entityType , entityRole , state & value . Représentent un buster ou un fantôme.

### Sortie pour un tour de jeu

Une ligne pour chacun de vos busters: une des actions suivantes :

-   MOVE suivi de deux entiers x et y
-   BUST suivi d'un entier ghostId
-   TRAP suivi d'un entier ghostId
-   RELEASE
-   STUN suivi par un entier busterId
-   RADAR

Vous pouvez ajouter du texte après vos instructions, il sera montré dans le player (un message par buster).

Votre première ligne sera pour votre CHASSEUR qui peut utiliser MOVE ou BUST,
la seconde ligne sera pour votre ATTRAPEUR qui peut utiliser MOVE, TRAP ou RELEASE,
et la dernière ligne sera pour votre ASSISTANT qui peut utiliser MOVE, STUN ou RADAR.

## Contraintes

bustersPerPlayer = 3
8 ≤ ghostCount ≤ 13
endurance dans {3, 15, 40}

Temps de réponse par tour ≤ 100 ms
