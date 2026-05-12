


import pygame
import copy


def directions(x, y):
    dirs = []

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:

            if dx == 0 and dy == 0:
                continue

            nx = x + dx
            ny = y + dy

            if 0 <= nx < 8 and 0 <= ny < 8:
                dirs.append((dx, dy))

    return dirs


def load_image(path, size):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)


class Token:

    def __init__(self, player, row, col, image):
        self.player = player
        self.row = row
        self.col = col
        self.image = image

    def draw(self, window):
        window.blit(self.image, (self.col * 80, self.row * 80))


class Grid:

    def __init__(self, rows, cols, size, game):

        self.rows = rows
        self.cols = cols
        self.size = size
        self.game = game

        self.white_token = load_image("assets/WhiteToken.png", size)
        self.black_token = load_image("assets/BlackToken.png", size)

        self.tokens = {}
        self.grid = self.create_board()

    def create_board(self):

        board = [[0 for _ in range(8)] for _ in range(8)]

        self.insert_token(board, 1, 3, 3)
        self.insert_token(board, -1, 3, 4)
        self.insert_token(board, 1, 4, 4)
        self.insert_token(board, -1, 4, 3)

        return board

    def draw(self, window):

        for row in range(8):
            for col in range(8):

                pygame.draw.rect(
                    window,
                    (0, 150, 0),
                    (col * 80, row * 80, 80, 80)
                )

                pygame.draw.rect(
                    window,
                    (0, 0, 0),
                    (col * 80, row * 80, 80, 80),
                    1
                )

        for token in self.tokens.values():
            token.draw(window)

        moves = self.find_available_moves(
            self.grid,
            self.game.current_player
        )

        for move in moves:

            pygame.draw.circle(
                window,
                (200, 200, 200),
                (move[1] * 80 + 40, move[0] * 80 + 40),
                10
            )

    def insert_token(self, board, player, row, col):

        image = (
            self.white_token
            if player == 1
            else self.black_token
        )

        self.tokens[(row, col)] = Token(
            player,
            row,
            col,
            image
        )

        board[row][col] = player

    def find_valid_cells(self, board, player):

        valid = []

        for row in range(8):
            for col in range(8):

                if board[row][col] != 0:
                    continue

                for dx, dy in directions(row, col):

                    nx = row + dx
                    ny = col + dy

                    if board[nx][ny] == -player:
                        valid.append((row, col))
                        break

        return valid

    def swappable_tiles(self, row, col, board, player):

        swappable = []

        for dx, dy in directions(row, col):

            nx = row + dx
            ny = col + dy

            current_line = []

            while 0 <= nx < 8 and 0 <= ny < 8:

                if board[nx][ny] == -player:

                    current_line.append((nx, ny))

                elif board[nx][ny] == player:

                    swappable.extend(current_line)
                    break

                else:
                    break

                nx += dx
                ny += dy

        return swappable

    def find_available_moves(self, board, player):

        valid = self.find_valid_cells(board, player)
        playable = []

        for row, col in valid:

            tiles = self.swappable_tiles(
                row,
                col,
                board,
                player
            )

            if len(tiles) > 0:
                playable.append((row, col))

        return playable

    def evaluate(self, board):

        score = 0

        for row in board:
            for cell in row:
                score += cell

        return score

    def minimax(self, board, depth, alpha, beta, maximizing):

        player = 1 if maximizing else -1
        moves = self.find_available_moves(board, player)

        if depth == 0 or len(moves) == 0:
            return self.evaluate(board)

        if maximizing:

            max_eval = float("-inf")

            for move in moves:

                new_board = copy.deepcopy(board)
                row, col = move

                new_board[row][col] = 1

                for tile in self.swappable_tiles(
                    row,
                    col,
                    new_board,
                    1
                ):
                    new_board[tile[0]][tile[1]] *= -1

                evaluation = self.minimax(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    False
                )

                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)

                if beta <= alpha:
                    break

            return max_eval

        else:

            min_eval = float("inf")

            for move in moves:

                new_board = copy.deepcopy(board)
                row, col = move

                new_board[row][col] = -1

                for tile in self.swappable_tiles(
                    row,
                    col,
                    new_board,
                    -1
                ):
                    new_board[tile[0]][tile[1]] *= -1

                evaluation = self.minimax(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    True
                )

                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)

                if beta <= alpha:
                    break

            return min_eval

    def get_best_move(self, board, player):

        best_move = None

        if player == 1:
            best_score = float("-inf")
        else:
            best_score = float("inf")

        moves = self.find_available_moves(board, player)

        for move in moves:

            new_board = copy.deepcopy(board)
            row, col = move

            new_board[row][col] = player

            for tile in self.swappable_tiles(
                row,
                col,
                new_board,
                player
            ):
                new_board[tile[0]][tile[1]] *= -1

            score = self.minimax(
                new_board,
                3,
                float("-inf"),
                float("inf"),
                player == -1
            )

            if player == 1:

                if score > best_score:
                    best_score = score
                    best_move = move

            else:

                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move

    def get_score(self, board):

        white = 0
        black = 0

        for row in board:
            for cell in row:

                if cell == 1:
                    white += 1

                elif cell == -1:
                    black += 1

        return white, black

    def get_grid(self):
        return self.grid

    def is_game_over(self, board):

        p1_moves = self.find_available_moves(board, 1)
        p2_moves = self.find_available_moves(board, -1)

        return len(p1_moves) == 0 and len(p2_moves) == 0

    def print_winner(self):

        white, black = self.get_score(self.grid)

        print(f"White: {white} | Black: {black}")

        if white > black:
            print("White wins!")

        elif black > white:
            print("Black wins!")

        else:
            print("Tie game!")


class Othello:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Othello")

        self.current_player = 1

        # MODES
        self.white_type = "HUMAN"
        self.black_type = "AI"

        self.grid = Grid(
            8,
            8,
            (80, 80),
            self
        )

        self.font = pygame.font.SysFont("urwbookman", 32)

        self.running = True

    def current_player_type(self):

        if self.current_player == 1:
            return self.white_type

        return self.black_type

    def run(self):

        while self.running:

            if self.current_player_type() == "HUMAN":
                self.handle_input()

            else:
                self.ai_move()

            self.draw()

        pygame.quit()

    def ai_move(self):

        pygame.time.delay(300)

        move = self.grid.get_best_move(
            self.grid.grid,
            self.current_player
        )

        if move:

            row, col = move
            self.make_move(row, col)

    def make_move(self, row, col):

        self.grid.insert_token(
            self.grid.grid,
            self.current_player,
            row,
            col
        )

        tiles = self.grid.swappable_tiles(
            row,
            col,
            self.grid.grid,
            self.current_player
        )

        for tile in tiles:

            tile_row, tile_col = tile

            self.grid.grid[tile_row][tile_col] *= -1

            image = (
                self.grid.white_token
                if self.current_player == 1
                else self.grid.black_token
            )

            self.grid.tokens[(tile_row, tile_col)] = Token(
                self.current_player,
                tile_row,
                tile_col,
                image
            )

        self.current_player *= -1

        if self.grid.is_game_over(self.grid.grid):
            self.grid.print_winner()

    def handle_input(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    x, y = pygame.mouse.get_pos()

                    col = x // 80
                    row = y // 80

                    moves = self.grid.find_available_moves(
                        self.grid.grid,
                        self.current_player
                    )

                    if (row, col) in moves:
                        self.make_move(row, col)

    def display_score(self):
        """Displays the Score in `draw` method"""
        score = self.grid.get_score(self.grid.get_grid())

        activated_color = (30, 144, 255) # blue
        text_color = (255, 255, 255) # white

        text_surface = self.font.render("Score:", True, text_color)
        self.screen.blit(text_surface, (10, 650))

        # One case for humans and another case for AI
        if self.current_player_type() == "HUMAN":
            text_surface = self.font.render(f"→", True, activated_color)
            self.screen.blit(text_surface, (10, 690))

            text_surface = self.font.render(f"{self.white_type}: {score[0]}", True, activated_color)
            self.screen.blit(text_surface, (40, 690))

            text_surface = self.font.render(f"{self.black_type}: {score[1]}", True, text_color)
            self.screen.blit(text_surface, (40, 730))

        if self.current_player_type() == "AI":
            text_surface = self.font.render(f"→", True, activated_color)
            self.screen.blit(text_surface, (10, 730))

            text_surface = self.font.render(f"{self.white_type}: {score[0]}", True, text_color)
            self.screen.blit(text_surface, (40, 690))

            text_surface = self.font.render(f"{self.black_type}: {score[1]}", True, activated_color)
            self.screen.blit(text_surface, (40, 730))

        return

    def draw(self):

        self.screen.fill((0, 0, 0))

        self.grid.draw(self.screen)

        self.display_score()

        pygame.display.update()


if __name__ == "__main__":

    game = Othello()
    game.run()
