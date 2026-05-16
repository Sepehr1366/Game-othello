"""
A classic Othello game that where the user can play against an AI agent using the MiniMax
algorithm, or another human.
"""

import sys
import copy
import pygame

W_OFFSET = 80
H_OFFSET = 20


def directions(x, y):
    """Returns all possible directions around a cell"""
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
    """Loads and resizes game images"""
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)


class Token:
    """Represents a single game token (black or white piece)"""

    def __init__(self, player, row, col, image):
        self.player = player
        self.row = row
        self.col = col
        self.image = image

        self.w_offset = W_OFFSET
        self.h_offset = H_OFFSET

    def draw(self, window):
        window.blit(
            self.image,
            ((self.col * 80) + self.w_offset, (self.row * 80) + self.h_offset),
        )


class Grid:
    """Main board and game logic class"""

    def __init__(self, rows, cols, size, game):

        self.rows = rows
        self.cols = cols
        self.size = size
        self.game = game

        self.white_token = load_image("assets/WhiteToken.png", size)
        self.black_token = load_image("assets/BlackToken.png", size)

        self.tokens = {}
        self.grid = self.create_board()

        self.w_offset = W_OFFSET
        self.h_offset = H_OFFSET

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
                    ((col * 80) + self.w_offset, (row * 80) + self.h_offset, 80, 80),
                )

                pygame.draw.rect(
                    window,
                    (0, 0, 0),
                    ((col * 80) + self.w_offset, (row * 80) + self.h_offset, 80, 80),
                    1,
                )

        for token in self.tokens.values():
            token.draw(window)

        moves = self.find_available_moves(self.grid, self.game.current_player)

        for move in moves:

            pygame.draw.circle(
                window,
                (200, 200, 200),
                (
                    (move[1] * 80 + 40) + self.w_offset,
                    (move[0] * 80 + 40) + self.h_offset,
                ),
                10,
            )

    def insert_token(self, board, player, row, col):
        """Places a new token on the board and updates the game grid"""
        image = self.white_token if player == 1 else self.black_token

        self.tokens[(row, col)] = Token(player, row, col, image)

        board[row][col] = player

    def find_valid_cells(self, board, player):
        """Finds all valid positions where the current player can place a token"""
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
        """Determines which opponent tiles will be flipped after a move"""
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
        """Checks the board and returns all valid moves the player can make"""
        valid = self.find_valid_cells(board, player)
        playable = []

        for row, col in valid:

            tiles = self.swappable_tiles(row, col, board, player)

            if len(tiles) > 0:
                playable.append((row, col))

        return playable

    def evaluate(self, board):
        """Evaluates the board score for the AI"""
        score = 0

        for row in board:
            for cell in row:
                score += cell

        return score

    def minimax(self, board, depth, alpha, beta, maximizing):
        """AI decision-making function that finds the best possible move"""
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

                for tile in self.swappable_tiles(row, col, new_board, 1):
                    new_board[tile[0]][tile[1]] *= -1

                evaluation = self.minimax(new_board, depth - 1, alpha, beta, False)

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

                for tile in self.swappable_tiles(row, col, new_board, -1):
                    new_board[tile[0]][tile[1]] *= -1

                evaluation = self.minimax(new_board, depth - 1, alpha, beta, True)

                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)

                if beta <= alpha:
                    break

            return min_eval

    def get_best_move(self, board, player):
        """Finds the best move for the AI using Minimax"""

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

            for tile in self.swappable_tiles(row, col, new_board, player):
                new_board[tile[0]][tile[1]] *= -1

            score = self.minimax(
                new_board, 3, float("-inf"), float("inf"), player == -1
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
        """Calculates current scores for white and black players"""

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
        """Checks if no more moves are available for both players"""

        p1_moves = self.find_available_moves(board, 1)
        p2_moves = self.find_available_moves(board, -1)

        return len(p1_moves) == 0 and len(p2_moves) == 0

    def print_winner(self):
        """Displays the game winner"""

        white, black = self.get_score(self.grid)
        if white > black:
            self.game.winner_text = "WHITE WINS!"

        elif black > white:
            self.game.winner_text = "BLACK WINS!"

        else:
            self.game.winner_text = "TIE GAME!"


class Othello:
    """Main game controller class"""

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Othello")

        self.current_player = 1

        self.white_type = "HUMAN"
        self.black_type = "AI"
        self.game_started = False
        self.grid = Grid(8, 8, (80, 80), self)

        self.h_offset = H_OFFSET
        self.w_offset = W_OFFSET

        if sys.platform == "win32":
            self.font = pygame.font.SysFont("bookmanoldstyle", 32, bold=True)
            self.big_font = pygame.font.SysFont("bookmanoldstyle", 50, bold=True)

        elif sys.platform == "linux":
            self.font = pygame.font.SysFont("urwbookman", 32)
            self.big_font = pygame.font.SysFont("urwbookman", 50)

        else:
            self.font = pygame.font.SysFont(None, 32)
            self.big_font = pygame.font.SysFont(None, 50)

        self.reset_button = pygame.Rect(635, 680, 145, 50)
        self.hvh_button = pygame.Rect(250, 200, 330, 60)
        self.hvai_button = pygame.Rect(250, 300, 330, 60)
        self.choose_color = False
        self.hvh_mode = False
        self.white_button = pygame.Rect(250, 300, 300, 60)
        self.black_button = pygame.Rect(250, 400, 300, 60)

        self.running = True
        self.winner_text = ""

    def current_player_type(self):
        """Returns the type of the current player (Human or AI)"""
        if self.current_player == 1:
            return self.white_type

        return self.black_type

    def run(self):
        """Main game loop"""
        while self.running:

            if "HUMAN" in self.current_player_type():

                self.handle_input()

            else:

                self.ai_move()

            self.draw()

        pygame.quit()

    def ai_move(self):
        """Handles AI moves"""
        # STOP AI AFTER GAME ENDS
        if self.winner_text != "":
            return

        pygame.time.delay(300)  # once we finish, make "thinking time" slightly longer

        move = self.grid.get_best_move(self.grid.grid, self.current_player)

        if move:

            row, col = move
            self.make_move(row, col)

    def make_move(self, row, col):
        """Places a move and flips opponent pieces"""
        self.grid.insert_token(self.grid.grid, self.current_player, row, col)

        self.draw()
        pygame.time.delay(500)

        tiles = self.grid.swappable_tiles(row, col, self.grid.grid, self.current_player)

        for tile in tiles:

            tile_row, tile_col = tile

            self.grid.grid[tile_row][tile_col] *= -1

            image = (
                self.grid.white_token
                if self.current_player == 1
                else self.grid.black_token
            )

            self.grid.tokens[(tile_row, tile_col)] = Token(
                self.current_player, tile_row, tile_col, image
            )

        self.current_player *= -1

        moves = self.grid.find_available_moves(self.grid.grid, self.current_player)

        if len(moves) == 0:

            self.current_player *= -1

            second_moves = self.grid.find_available_moves(
                self.grid.grid, self.current_player
            )

            if len(second_moves) == 0:

                self.grid.print_winner()

    def handle_input(self):
        """Handles keyboard and mouse input"""
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    self.reset_game()

            # MOUSE
            if event.type == pygame.MOUSEBUTTONDOWN:

                mouse_pos = pygame.mouse.get_pos()

                if self.choose_color:

                    if self.white_button.collidepoint(mouse_pos):

                        if self.hvh_mode:
                            self.white_type = "HUMAN 1"
                            self.black_type = "HUMAN 2"

                        else:
                            self.white_type = "HUMAN"
                            self.black_type = "AI"

                        self.current_player = 1
                        self.game_started = True
                        self.choose_color = False
                        return

                    elif self.black_button.collidepoint(mouse_pos):

                        if self.hvh_mode:
                            self.white_type = "HUMAN 2"
                            self.black_type = "HUMAN 1"

                        else:
                            self.white_type = "AI"
                            self.black_type = "HUMAN"

                        self.current_player = 1
                        self.game_started = True
                        self.choose_color = False
                        return

                if not self.game_started:

                    if self.hvh_button.collidepoint(mouse_pos):

                        self.hvh_mode = True
                        self.choose_color = True

                    elif self.hvai_button.collidepoint(mouse_pos):

                        self.choose_color = True

                    return

                if self.reset_button.collidepoint(mouse_pos):

                    self.reset_game()
                    return

                if self.winner_text != "":
                    return

                if event.button == 1:

                    x, y = mouse_pos

                    board_x = x - W_OFFSET
                    board_y = y - H_OFFSET

                    if board_x < 640 and 0 <= board_y < 640:

                        col = board_x // 80
                        row = board_y // 80

                        moves = self.grid.find_available_moves(
                            self.grid.grid, self.current_player
                        )

                        if (row, col) in moves:
                            self.make_move(row, col)

    def reset_game(self):
        """Resets the game to the initial state"""
        self.grid = Grid(8, 8, (80, 80), self)

        self.current_player = 1
        self.winner_text = ""
        self.game_started = False
        self.choose_color = False
        self.hvh_mode = False

        self.white_type = "HUMAN"
        self.black_type = "AI"

    def draw_board_border(self):
        """Draws a border around the game board"""
        outer_border_dimension = (50, 0, 700, 673)
        pygame.draw.rect(self.screen, (0, 0, 0, 0), outer_border_dimension)

        middle_border_dim = (63, 8, 675, 660)
        pygame.draw.rect(self.screen, (255, 255, 255, 1), middle_border_dim)

        inner_border_dim = (65, 10, 670, 656)
        pygame.draw.rect(self.screen, (0, 0, 0, 0), inner_border_dim)

    def display_score(self):
        """Displays current scores on the screen"""
        score = self.grid.get_score(self.grid.get_grid())

        activated_color = (30, 144, 255)
        text_color = (255, 255, 255)

        text_surface = self.font.render("Score:", True, text_color)

        self.screen.blit(text_surface, (10, 673))

        white_color = text_color
        black_color = text_color

        if self.current_player == 1:
            white_color = activated_color
        else:
            black_color = activated_color

        white_text = self.font.render(
            f"{self.white_type}: {score[0]}", True, white_color
        )

        black_text = self.font.render(
            f"{self.black_type}: {score[1]}", True, black_color
        )

        self.screen.blit(white_text, (60, 710))
        self.screen.blit(black_text, (60, 750))

        arrow_y = 710 if self.current_player == 1 else 750

        if sys.platform == "linux":
            arrow = self.font.render("→", True, activated_color)
            self.screen.blit(arrow, (10, arrow_y))

        else:
            arrow = self.font.render("→", True, activated_color)
            self.screen.blit(arrow, (10, arrow_y))

    def display_current_token(self):
        """Displays current token in score area"""
        square_dimensions = (375, 685, 90, 90)
        pygame.draw.rect(self.screen, (0, 0, 0), (375 - 2, 685 - 2, 90 + 4, 90 + 4))
        pygame.draw.rect(self.screen, (0, 150, 0), square_dimensions)

        if self.current_player == -1:
            current_token = self.grid.black_token
        else:
            current_token = self.grid.white_token

        self.screen.blit(current_token, (380, 690))

    def draw(self):
        """Draws the game interface and winner screen"""
        self.screen.fill((42, 42, 42))

        if self.choose_color:

            self.draw_color_menu()
            pygame.display.update()
            return

        if not self.game_started and not self.choose_color:

            self.draw_menu()
            pygame.display.update()
            return

            # GAME
        self.draw_board_border()
        self.grid.draw(self.screen)

        self.display_score()

        self.display_current_token()

        pygame.draw.rect(
            self.screen, (200, 50, 50), self.reset_button, border_radius=10
        )
        if self.choose_color:

            self.draw_color_menu()

            pygame.display.update()

            return
        text_surface = self.font.render("RESET", True, (255, 255, 255))

        self.screen.blit(text_surface, (650, 690))

        if self.grid.is_game_over(self.grid.grid):

            self.grid.print_winner()

        if self.winner_text != "":

            winner_surface = self.big_font.render(self.winner_text, True, (255, 215, 0))

            self.screen.blit(winner_surface, (220, 640))
        pygame.display.update()

    def draw_menu(self):
        """Draws the main menu"""
        self.screen.fill((30, 30, 30))

        title = self.big_font.render("OTHELLO GAME", True, (255, 255, 255))

        self.screen.blit(title, (190, 80))

        pygame.draw.rect(self.screen, (50, 150, 255), self.hvh_button, border_radius=10)

        text = self.font.render("Human vs Human", True, (255, 255, 255))

        self.screen.blit(text, (270, 220))

        pygame.draw.rect(
            self.screen, (50, 200, 100), self.hvai_button, border_radius=10
        )

        text = self.font.render("Human vs AI", True, (255, 255, 255))

        self.screen.blit(text, (310, 320))

    def draw_color_menu(self):
        """Draws the color selection menu"""
        self.screen.fill((30, 30, 30))

        title = self.big_font.render("Choose Color", True, (255, 255, 255))

        self.screen.blit(title, (240, 150))

        pygame.draw.rect(
            self.screen, (220, 220, 220), self.white_button, border_radius=10
        )

        text = self.font.render("Play as White", True, (0, 0, 0))

        self.screen.blit(text, (300, 320))

        pygame.draw.rect(self.screen, (50, 50, 50), self.black_button, border_radius=10)

        text = self.font.render("Play as Black", True, (255, 255, 255))

        self.screen.blit(text, (300, 420))


if __name__ == "__main__":

    game = Othello()
    game.run()
