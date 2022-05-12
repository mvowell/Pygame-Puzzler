class player:
    """
    This is a class to hold the player's position and attached blocks to the player
    """
    playerpos = [0,0]
    playerblocks = []
    def __init__(self,pos = [0,0],blocks=[]):
        self.playerpos = pos
        self.playerblocks = blocks

    # add a block to a location on the player
    def addblock(self,globalpos):
        self.playerblocks.append([globalpos[0]-self.playerpos[0],globalpos[1]-self.playerpos[1]])

    # remove all attached blocks, kind of useless
    def removeallblock(self):
        output = self.playerblocks
        self.playerblocks = []
        return

    #find the width of attached blocks + player
    def getwidth(self):
        min = 0
        max = 0
        for i in self.playerblocks:
            if i[0] > max:
                max = i[0]
            if i[0] < min:
                min = i[0]
        return max - min + 1

    # find the height
    def getheight(self):
        min = 0
        max = 0
        for i in self.playerblocks:
            if i[1] > max:
                max = i[1]
            if i[1] < min:
                min = i[1]
        return max - min + 1

    # find the top left corner of the player + blocks
    def getcorner(self):
        xmin = 0
        ymin = 0
        for i in self.playerblocks:
            if i[0] < xmin:
                xmin = i[0]
            if i[1] < ymin:
                ymin = i[1]
        return [xmin,ymin]

    # find the bottom right corner(opposite from getcorner)
    def brcrnr(self):
        xmax = 0
        ymax = 0
        for i in self.playerblocks:
            if i[0] > xmax:
                xmax = i[0]
            if i[1] > ymax:
                ymax = i[1]
        return [xmax+1, ymax+1]

    #find the bottom left corner, used later
    def blcrnr(self):
        xmin = 0
        ymax = 0
        for i in self.playerblocks:
            if i[0] < xmin:
                xmin = i[0]
            if i[1] > ymax:
                ymax = i[1]
        return [xmin, ymax+1]

    # rotate all of the blocks clockwise as if they were sitting on the floor, and the pivot point is the bottom right corner
    def rotatecw(self):
        output = []
        piv = self.brcrnr()
        piv = [piv[0]+self.playerpos[0],piv[1]+self.playerpos[1]]
        for i in self.playerblocks:
            coords = [-i[1],i[0]]
            output.append(coords)
        self.playerblocks = output
        diff = [piv[0]-self.playerpos[0],piv[1]-self.playerpos[1]]
        self.playerpos = [piv[0]+diff[1]-1,piv[1]-diff[0]]
        print(piv)

    # does the same thing as rotatecw, except for in the opposite direction
    def rotateccw(self):
        output = []
        piv = self.blcrnr()
        print(piv)
        piv = [piv[0] + self.playerpos[0], piv[1] + self.playerpos[1]]
        diff = self.blcrnr()
        diff = [-diff[0],-diff[1]]
        for i in self.playerblocks:
            coords = [i[1], -i[0]]
            output.append(coords)
        self.playerblocks = output
        self.playerpos = [piv[0]+diff[1],piv[1]-diff[0]-1]
        print(piv)

    # basic access functions to player position
    def moveplayer(self,diff):
        self.playerpos[0] += diff[0]
        self.playerpos[1] += diff[1]
    def setplayer(self,pos):
        self.playerpos[0] = pos[0]
        self.playerpos[1] = pos[1]

    # currently useless function, but is supposed to find the player's actual position within the bounding box of its attached boxes
    def getplayerrelcoord(self):
        return [self.getwidth()-1+self.getcorner()[0],self.getheight()-1+self.getcorner()[1]]