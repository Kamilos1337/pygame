import pygame, sys
from pygame.locals import *
import pickle
import select
import socket
import random
import atexit
WIDTH = 1200
HEIGHT = 759
BUFFERSIZE = 2048

screen = pygame.display.set_mode((WIDTH, HEIGHT))
image = pygame.image.load("img/map1.jpg").convert_alpha()
          #INSIDE OF THE GAME LOOP

pygame.display.set_caption('Game')

clock = pygame.time.Clock()



serverAddr = '127.0.0.1'
if len(sys.argv) == 2:
  serverAddr = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverAddr, 4321))

def exit_handler():
      ge = ['player left', playerid, 0,0, "map1.jpg", ""]
      s.send(pickle.dumps(ge))

atexit.register(exit_handler)

playerid = 0
characters = ["1.png", "2.png", "3.png", "4.png"]
random = characters[random.randint(0,3)]

class Details:
  def __init__(self, x, y, id, myMap, character):
    self.x = x
    self.y = y
    self.vx = 0
    self.vy = 0
    self.id = id
    self.myMap = myMap
    self.character = character

  def update(self):
    self.x += self.vx
    self.y += self.vy

    if self.x > WIDTH - 50:
      self.x = WIDTH - 50
    if self.x < 0:
      self.x = 0
    if self.y > HEIGHT - 50:
      self.y = HEIGHT - 50
    if self.y < 0:
      self.y = 0

    if self.id == 0:
      self.id = playerid

  def render(self):
    if(self.myMap=="map1.jpg"):
        arrow =  pygame.image.load("img/nextmap.png")
        screen.blit(arrow, (1130, 407))
    if(self.myMap=="map2.jpg"):
        arrow =  pygame.image.load("img/previousmap.png")
        screen.blit(arrow, (0, 370))
    myCharacter =  pygame.image.load("img/"+self.character)
    screen.blit(myCharacter, (self.x, self.y))



  def changeMap(self):
    if(self.myMap=="map1.jpg"):
         self.myMap="map2.jpg"
    else:
         self.myMap="map1.jpg"
    bg = pygame.image.load("img/"+self.myMap).convert_alpha()
    screen.blit(bg, (0, 0))

  def clearMap(self):
    bg = pygame.image.load("img/"+self.myMap).convert_alpha()
    screen.blit(bg, (0, 0))



#game events
#['event type', param1, param2]
#
#event types:
# id update
# ['id update', id]
#
# player locations
# ['player locations', [id, x, y], [id, x, y] ...]

#user commands
# position update
# ['position update', id, x, y]

class GameEvent:
  def __init__(self, vx, vy):
    self.vx = vx
    self.vy = vy

Player = Details(50, 50, 0, "map1.jpg", random)
players = []

while True:
  ins, outs, ex = select.select([s], [], [], 0)
  for inm in ins:
    try:
        gameEvent = pickle.loads(inm.recv(BUFFERSIZE))
    except:
        ifer = "none"
    if gameEvent[0] == 'id update':
      playerid = gameEvent[1]
      print("Moje player id", playerid)
    if gameEvent[0] == 'player locations':
      gameEvent.pop(0)
      players = []

      for elem in gameEvent:
        if (elem[0] != playerid):
            players.append(Details(elem[1], elem[2], elem[0], elem[3], elem[4]))

  for event in pygame.event.get():
    if event.type == QUIT:
    	pygame.quit()
    	sys.exit()
    if event.type == KEYDOWN:
      if event.key == K_LEFT: Player.vx = -10
      if event.key == K_RIGHT: Player.vx = 10
      if event.key == K_UP: Player.vy = -10
      if event.key == K_DOWN: Player.vy = 10
      if event.key == K_c:
          Player.changeMap()
          pygame.display.flip()
    if event.type == KEYUP:
      if event.key == K_LEFT and Player.vx == -10: Player.vx = 0
      if event.key == K_RIGHT and Player.vx == 10: Player.vx = 0
      if event.key == K_UP and Player.vy == -10: Player.vy = 0
      if event.key == K_DOWN and Player.vy == 10: Player.vy = 0

  clock.tick(60)
  Player.clearMap()
  Player.update()
  print(Player.x, Player.y, Player.myMap)
  if (Player.x>1080 and Player.y>350 and Player.y<400 and Player.myMap=="map1.jpg"):
        Player.changeMap()
  if (Player.x<50 and Player.y>320 and Player.y<400 and Player.myMap=="map2.jpg"):
        Player.changeMap()
  for m in players:
    if (m.x>1150 and m.y>404 and m.y<464 and m.myMap=="map1.jpg"):
        m.changeMap()
    if (m.x<50 and m.y>320 and m.y<400 and m.myMap=="map2.jpg"):
        m.changeMap()
    if(Player.myMap==m.myMap):
        m.render()

  Player.render()


  pygame.display.flip()
  ge = ['position update', playerid, Player.x, Player.y, Player.myMap, Player.character]
  s.send(pickle.dumps(ge))
s.close()
