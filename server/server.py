import socket
import asyncore
import select
import random
import pickle
import time

BUFFERSIZE = 512

outgoing = []

class Minion:
  def __init__(self, ownerid):
    self.x = 50
    self.y = 50
    self.ownerid = ownerid
    self.myMap = "map1.jpg"

minionmap = {}

def updateWorld(message):
  arr = pickle.loads(message)
  playerid = arr[1]
  x = arr[2]
  y = arr[3]
  myMap = arr[4]
  if(arr[0]=="player left"):
      print(arr[0])
      print(playerid)
      minionmap.pop(playerid)
      print(str(minionmap))

  if playerid == 0: return

  minionmap[playerid].x = x
  minionmap[playerid].y = y
  minionmap[playerid].myMap = myMap

  remove = []

  for i in outgoing:
    update = ['player locations']

    for key, value in minionmap.items():
      update.append([value.ownerid, value.x, value.y, value.myMap])
    
    try:
      i.send(pickle.dumps(update))
    except Exception:
      remove.append(i)
      continue
    
    #print ('sent update data')

    for r in remove:
      outgoing.remove(r)

class MainServer(asyncore.dispatcher):
  def __init__(self, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.bind(('', port))
    self.listen(10)
  def handle_accept(self):
    conn, addr = self.accept()
    print ('Connection address:' + addr[0] + " " + str(addr[1]))
    outgoing.append(conn)
    playerid = random.randint(1000, 1000000)
    playerminion = Minion(playerid)
    minionmap[playerid] = playerminion
    conn.send(pickle.dumps(['id update', playerid]))
    SecondaryServer(conn)

class SecondaryServer(asyncore.dispatcher_with_send):
  def handle_read(self):
    recievedData = self.recv(BUFFERSIZE)
    if recievedData:
      updateWorld(recievedData)
    else: self.close()

MainServer(4321)
asyncore.loop()