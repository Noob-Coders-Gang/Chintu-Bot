import random
import numpy as np
import datetime

games = []


def getGames():
    return games


def getGamesByUser(user: str):
    for game in games:
        userid = str(game.getId())
        if userid == user:
            return game


def getGamesByMessage(message: str):
    for game in games:
        if game.getMessageId() == message:
            return game


class GameGrid:

    def __init__(self, user_id: str):
        self.message_id = ''
        self.channel = ''
        self.matrix = np.array([[0, 0, 0, 0], 
                                [0, 0, 0, 0], 
                                [0, 0, 0, 0], 
                                [0, 0, 0, 0]])
        self.user = user_id
        self.last_update = datetime.datetime.now()
        self.point = 0
        self.running = True

    def randomNumber(self):
        x = random.randint(0, 3)
        y = random.randint(0, 3)

        if self.matrix[x, y] == 0:
            self.matrix[x, y] = 2
        else:
            self.randomNumber()
    
    def getEmojiMessage(self):
        self.updateLastUpdate()
        message = ''

        for y in range(0, 4):
            for x in range(0, 4):
                num = self.matrix[y, x]

                if num == 0:
                    message += '<:blank:845902891487199243>'
                elif num == 2:
                    message += '<:2_:845901774539194369>'
                elif num == 4:
                    message += '<:4_:845901774959149056>'
                elif num == 8:
                    message += '<:8_:845901775101493248>'
                elif num == 16:
                    message += '<:16:845901775206875166>'
                elif num == 32:
                    message += '<:32:845901775193636894>'
                elif num == 64:
                    message += '<:64:845901775060074496>'
                elif num == 128:
                    message += '<:128:845901774762147851>'
                elif num == 256:
                    message += '<:256:845901774938177547>'
                elif num == 512:
                    message += '<:512:845901775118663710>'
                elif num == 1024:
                    message += '<:1024:845901775122857984>'
                elif num == 2048:
                    message += '<:2048:845901775273459767>'
                elif num == 4096:
                    message += '<:4096:845901775265726474>'
            message += '\n'

        return message

                

    def slideUp(self):

        def shiftUp():
            for p in range(0, 3):
                for yin in range(1, 4):
                    for xin in range(0, 4):
                        if self.matrix[yin, xin] != 0 and self.matrix[yin - 1, xin] == 0:
                            self.matrix[yin - 1, xin] = self.matrix[yin, xin]
                            self.matrix[yin, xin] = 0

        shiftUp()
        for y in range(1, 4):
            for x in range(0, 4):
                if self.matrix[y, x] == self.matrix[y - 1, x]:
                    self.matrix[y - 1, x] = self.matrix[y - 1, x] * 2
                    self.matrix[y, x] = 0
                    self.updatePoint(self.matrix[y - 1, x] / 2)

        shiftUp()

    def slideDown(self):

        def shiftDown():
            for p in range(0, 3):
                for yin in range(2, -1, -1):
                    for xin in range(3, -1, -1):
                        if self.matrix[yin, xin] != 0 and self.matrix[yin + 1, xin] == 0:
                            self.matrix[yin + 1, xin] = self.matrix[yin, xin]
                            self.matrix[yin, xin] = 0

        shiftDown()
        for y in range(2, -1, -1):
            for x in range(3, -1, -1):
                if self.matrix[y, x] == self.matrix[y + 1, x]:
                    self.matrix[y + 1, x] = self.matrix[y + 1, x] * 2
                    self.matrix[y, x] = 0
                    self.updatePoint(self.matrix[y + 1, x] / 2)

        shiftDown()

    def slideLeft(self):

        def shiftLeft():
            for p in range(0, 3):
                for xin in range(1, 4):
                    for yin in range(0, 4):
                        if self.matrix[yin, xin] != 0 and self.matrix[yin, xin - 1] == 0:
                            self.matrix[yin, xin - 1] = self.matrix[yin, xin]
                            self.matrix[yin, xin] = 0

        shiftLeft()
        for x in range(1, 4):
            for y in range(0, 4):
                if self.matrix[y, x] == self.matrix[y, x - 1]:
                    self.matrix[y, x - 1] = self.matrix[y, x - 1] * 2
                    self.matrix[y, x] = 0
                    self.updatePoint(self.matrix[y, x - 1] / 2)

        shiftLeft()

    def slideRight(self):

        def shiftRight():
            for p in range(0, 3):
                for xin in range(2, -1, -1):
                    for yin in range(3, -1, -1):
                        if self.matrix[yin, xin] != 0 and self.matrix[yin, xin + 1] == 0:
                            self.matrix[yin, xin + 1] = self.matrix[yin, xin]
                            self.matrix[yin, xin] = 0

        shiftRight()
        for x in range(2, -1, -1):
            for y in range(3, -1, -1):
                if self.matrix[y, x] == self.matrix[y, x + 1]:
                    self.matrix[y, x + 1] = self.matrix[y, x + 1] * 2
                    self.matrix[y, x] = 0
                    self.updatePoint(self.matrix[y, x + 1] / 2)

        shiftRight()

    def start(self):
        if getGamesByUser(self.user):
            self.stop()
        self.running = True
        self.randomNumber()
        self.randomNumber()
        games.append(self)
    
    def isGameOver(self):
        if 0 in self.matrix:
            return False

        for y in range(0, 4):
            for x in range(0, 4):
                num = self.matrix[y, x]

                try:
                    if self.matrix[y - 1, x] == num:
                        return False
                except Exception:
                    pass

                try:
                    if self.matrix[y + 1, x] == num:
                        return False
                except Exception:
                    pass

                try:
                    if self.matrix[y, x - 1] == num:
                        return False
                except Exception:
                    pass

                try:
                    if self.matrix[y, x + 1] == num:
                        return False
                except Exception:
                    pass
        
        return True
    
    def isGameWon(self):
        if 4096 in self.matrix:
            return True
        return False

    def stop(self):
        self.running = False
        games.remove(self)
    
    def updatePoint(self, point: int):
        self.point += point
    
    def getPoint(self):
        return self.point
    
    def isRunning(self):
        return self.running

    def setMessageId(self, msgid: str):
        self.message_id = msgid
    
    def getMessageId(self):
        return self.message_id

    def updateLastUpdate(self):
        self.last_update = datetime.datetime.now()
    
    def getLastUpdate(self):
        return (datetime.datetime.now() - self.last_update).total_seconds()

    def setChannelId(self, channel: str):
        self.channel = channel
    
    def getChannelId(self):
        return self.channel
    
    def getMatrix(self):
        return self.matrix

    def getId(self):
        return self.user
