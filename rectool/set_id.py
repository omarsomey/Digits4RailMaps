from jproperties import Properties
import io

p = Properties()
p1 = Properties()
p2 = Properties()

def maximum(a, b, c): 
  
    if (a >= b) and (a >= c): 
        largest = a 
  
    elif (b >= a) and (b >= c): 
        largest = b 
    else: 
        largest = c 
          
    return largest 


def readId(path1, path2, path3):
    with open(path1, 'rb') as f:
        p.load(f, 'utf-8')
    with open(path2, 'rb') as f1:
        p1.load(f1, 'utf-8')
    with open(path3, 'rb') as f2:
        p2.load(f2, 'utf-8')

    id = int(p["video-id"].data)
    id1 = int(p1["video-id"].data)
    id2 = int(p2["gps-id"].data)

    return str(maximum(id, id1, id2))

def writeId(id, path1, path2, path3):
    p["video-id"]= id
    p1["video-id"]= id
    p2["gps-id"] = id

    with open(path1, 'wb') as f:
        p.store(f, encoding="utf-8")
    with open(path2, 'wb') as f1:
        p1.store(f1, encoding="utf-8")
    with open(path3, 'wb') as f2:
        p2.store(f2, encoding="utf-8")

        
def setId(path1, path2, path3):

    id  = readId(path1, path2, path3)
    writeId(id, path1, path2, path3)



