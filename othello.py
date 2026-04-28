
# this is a comment
import pygame
import random
import copy


def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    validdirections = []

    if x != minX:
        validdirections.append((x-1, y))
    if x != minX and y != minY:
        validdirections.append((x-1, y-1))
    if x != minX and y != maxY:   # FIXED
        validdirections.append((x-1, y+1))

    if x != maxX:
        validdirections.append((x+1, y))
    if x != maxX and y != minY:
        validdirections.append((x+1, y-1))
    if x != maxX and y != maxY:
        validdirections.append((x+1, y+1))

    if y != minY:
        validdirections.append((x, y-1))
    if y != maxY:
        validdirections.append((x, y+1))

    return validdirections


def loadImages(path, size):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    return img


class Othello:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Othello")

        self.player1 = 1
        self.player2 = -1
        self.currentplayer = 1

        self.rows = 8
        self.columns = 8

        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.RUN = True

    def run(self):
        while self.RUN:
            self.input()
            self.draw()

        pygame.quit()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    x, y = x // 80, y // 80

                    if 0 <= x < 8 and 0 <= y < 8:
                        availableMoves = self.grid.findAvailMove(
                            self.grid.gridLogic,
                            self.currentplayer
                        )

                        if (y, x) in availableMoves:
                            self.grid.insertToken(
                                self.grid.gridLogic,
                                self.currentplayer,
                                y,
                                x
                            )

                            swappableTiles = self.grid.swappableTiles(
                                y,
                                x,
                                self.grid.gridLogic,
                                self.currentplayer
                            )

                            for tile in swappableTiles:
                                tileY, tileX = tile
                                self.grid.gridLogic[tileY][tileX] *= -1

                                tokenImage = (
                                    self.grid.whitetoken
                                    if self.currentplayer == 1
                                    else self.grid.blacktoken
                                )

                                self.grid.tokens[(tileY, tileX)] = Token(
                                    self.currentplayer,
                                    tileY,
                                    tileX,
                                    tokenImage,
                                    self
                                )

                            self.currentplayer *= -1

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        pygame.display.update()


class Grid:
    def __init__(self, rows, columns, size, main):
        self.Game = main
        self.y = rows
        self.x = columns
        self.size = size

        self.whitetoken = loadImages('assets/WhiteToken.png', size)
        self.blacktoken = loadImages('assets/BlackToken.png', size)

        self.tokens = {}
        self.gridLogic = self.regenGrid(rows, columns)

    def regenGrid(self, rows, columns):
        grid = []

        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)

        # starting pieces
        self.insertToken(grid, 1, 3, 3)
        self.insertToken(grid, -1, 3, 4)
        self.insertToken(grid, 1, 4, 4)
        self.insertToken(grid, -1, 4, 3)

        return grid

    def drawGrid(self, window):
        for y in range(8):
            for x in range(8):
                pygame.draw.rect(
                    window,
                    (0, 150, 0),
                    (x*80, y*80, 80, 80)
                )
                pygame.draw.rect(
                    window,
                    (0, 0, 0),
                    (x*80, y*80, 80, 80),
                    1
                )

        for token in self.tokens.values():
            token.draw(window)

        availMoves = self.findAvailMove(
            self.gridLogic,
            self.Game.currentplayer
        )

        for move in availMoves:
            pygame.draw.circle(
                window,
                (200, 200, 200),
                (move[1]*80 + 40, move[0]*80 + 40),
                10
            )

    def findValidCells(self, grid, currentplayer):
        validCells = []

        for x in range(8):
            for y in range(8):
                if grid[x][y] != 0:
                    continue

                DIRECTIONS = directions(x, y)

                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]

                    if checkedCell == 0 or checkedCell == currentplayer:
                        continue

                    if (x, y) not in validCells:
                        validCells.append((x, y))

        return validCells

    def swappableTiles(self, x, y, grid, player):
        surroundCells = directions(x, y)
        swappableTiles = []

        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX = checkX - x
            difY = checkY - y

            currentLine = []
            run = True

            while run:
                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    break

                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))

                elif grid[checkX][checkY] == player:
                    break

                else:
                    currentLine.clear()
                    break

                checkX += difX
                checkY += difY

            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)

        return swappableTiles

    def findAvailMove(self, grid, currentplayer):
        validCells = self.findValidCells(grid, currentplayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            swapTiles = self.swappableTiles(
                x,
                y,
                grid,
                currentplayer
            )

            if len(swapTiles) > 0:
                playableCells.append(cell)

        return playableCells

    def insertToken(self, grid, currentplayer, y, x):
        tokenImage = (
            self.whitetoken
            if currentplayer == 1
            else self.blacktoken
        )

        self.tokens[(y, x)] = Token(
            currentplayer,
            y,
            x,
            tokenImage,
            self.Game
        )

        grid[y][x] = currentplayer


class Token:
    def __init__(self, player, gridX, gridY, image, main):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = gridY * 80
        self.posY = gridX * 80
        self.image = image

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))


if __name__ == '__main__':
    game = Othello()
    game.run()
