from abc import ABC, abstractmethod

class GameState(ABC):
    """Abstract Base Class"""

    MAX_PLAYER = None  # Define in subclass
    MIN_PLAYER = None  # Define in subclass

    def __init__(self, board, current_player):
        self.board = board
        self.current_player = current_player

    @abstractmethod
    def get_successors(self):
        """Generate all valid successor states from the current state."""
        pass

    @abstractmethod
    def is_terminal(self):
        """Return True if the game has ended (win/loss/draw)."""
        pass

    @abstractmethod
    def evaluate(self):
        """Evaluate the game state from MAX's perspective."""
        pass


import copy

class NineMensMorris(GameState):
    MAX_PLAYER = 'X'
    MIN_PLAYER = 'O'
    EMPTY = '_'

    ADJACENT_POINTS = {
        0: [1, 9], 1: [0, 2, 4], 2: [1, 14], 3: [4, 10], 4: [1, 3, 5, 7],
        5: [4, 13], 6: [7, 11], 7: [4, 6, 8], 8: [7, 12], 9: [0, 10, 21],
        10: [3, 9, 11, 18], 11: [6, 10, 15], 12: [8, 13, 17], 13: [5, 12, 14, 20],
        14: [2, 13, 23], 15: [11, 16], 16: [15, 17, 19], 17: [12, 16],
        18: [10, 19], 19: [16, 18, 20, 22], 20: [13, 19],
        21: [9, 22], 22: [19, 21, 23], 23: [14, 22]
    }

    def __init__(self, board=None, current_player='X', pieces_to_place=(9, 9)):
        if board is None:
            board = [self.EMPTY] * 24
        self.pieces_to_place = {
            self.MAX_PLAYER: pieces_to_place[0],
            self.MIN_PLAYER: pieces_to_place[1]
        }
        self.pieces_on_board = {
            self.MAX_PLAYER: board.count(self.MAX_PLAYER),
            self.MIN_PLAYER: board.count(self.MIN_PLAYER)
        }
        self.phase = self.determine_phase()
        super().__init__(board, current_player)

    def is_part_of_mill(self, pos):
        '''
        Check if a piece is part of a mill
        '''
        # All possible mills on the board
        mills = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [9, 10, 11], [12, 13, 14], [15, 16, 17],
            [18, 19, 20], [21, 22, 23],
            [0, 9, 21], [3, 10, 18], [6, 11, 15],
            [1, 4, 7], [16, 19, 22], [8, 12, 17],
            [5, 13, 20], [2, 14, 23]
        ]
        player = self.board[pos]
        # Check if the position actually holds a piece
        if player == self.EMPTY:
            raise f"No piece on position {pos}!"
        return any(all(self.board[p] == player for p in mill) and (pos in mill) for mill in mills)

    def determine_phase(self):
        if self.pieces_to_place[self.MAX_PLAYER] > 0 or self.pieces_to_place[self.MIN_PLAYER] > 0:
            return 'placing'
        if self.pieces_on_board[self.MAX_PLAYER] == 3 or self.pieces_on_board[self.MIN_PLAYER] == 3:
            return 'flying'
        return 'moving'

    def other_player(self):
        return self.MIN_PLAYER if self.current_player == self.MAX_PLAYER else self.MAX_PLAYER

    def get_successors(self):
        successors = []
        if self.phase == 'placing':
            for i in range(24):
                if self.board[i] == self.EMPTY:
                    new_board = copy.deepcopy(self.board)
                    new_board[i] = self.current_player

                    new_pieces_to_place = (self.pieces_to_place[self.MAX_PLAYER], self.pieces_to_place[self.MIN_PLAYER])
                    if self.current_player == self.MAX_PLAYER:
                        new_place = (new_pieces_to_place[0] - 1, new_pieces_to_place[1])
                    else:
                        new_place = (new_pieces_to_place[0], new_pieces_to_place[1] - 1)

                    next_player = self.other_player()
                    new_state = NineMensMorris(new_board, next_player, new_place)
                    # check if a mill has been closed
                    if new_state.is_part_of_mill(i):
                        successors.extend(new_state.successors_on_mill_closed())
                    else:
                        successors.append(new_state)

        elif self.phase in ['moving', 'flying']:
            positions = [i for i, p in enumerate(self.board) if p == self.current_player]
            for src in positions:
                destinations = (self.ADJACENT_POINTS[src] if self.phase == 'moving'
                                else [i for i in range(24) if self.board[i] == self.EMPTY])
                for dst in destinations:
                    if self.board[dst] == self.EMPTY:
                        new_board = copy.deepcopy(self.board)
                        new_board[src] = self.EMPTY
                        new_board[dst] = self.current_player
                        new_place = (0, 0)  # no placing left at this point
                        new_state = NineMensMorris(new_board, self.other_player(), new_place)
                        # check if a mill has been closed
                        if new_state.is_part_of_mill(dst):
                            successors.extend(new_state.successors_on_mill_closed())
                        else:
                            successors.append(new_state)

        return successors

    def successors_on_mill_closed(self):
        """
        Return all possible states resulting from removing an opponent's piece.
        """

        opponent = self.current_player
        result_states = []

        # Removable pieces are pieces which are not part of mills
        removable = [i for i in range(24) if self.board[i] == opponent and not self.is_part_of_mill(i)]
        if not removable:
            # All opponent pieces are in mills, so we can take any of them
            removable = [i for i in range(24) if self.board[i] == opponent]

        for i in removable:
            new_board = copy.deepcopy(self.board)
            new_board[i] = self.EMPTY
            new_pieces_to_place = (self.pieces_to_place[self.MAX_PLAYER], self.pieces_to_place[self.MIN_PLAYER])

            result_states.append(NineMensMorris(new_board, self.current_player, new_pieces_to_place))

        return result_states

    def is_terminal(self):
        for player in [self.MAX_PLAYER, self.MIN_PLAYER]:
            if (self.pieces_on_board[player] + self.pieces_to_place[player] < 3) or not self.has_valid_moves(player):
                return True
        return False

    def has_valid_moves(self, player):
        if self.determine_phase() == 'placing':
            return True
        positions = [i for i, p in enumerate(self.board) if p == player]
        for src in positions:
            if self.determine_phase() == 'flying':
                if any(self.board[i] == self.EMPTY for i in range(24)):
                    return True
            else:
                if any(self.board[dst] == self.EMPTY for dst in self.ADJACENT_POINTS[src]):
                    return True
        return False

    def evaluate(self):
        def count_mills(player):
            mills = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],
                [9, 10, 11], [12, 13, 14], [15, 16, 17],
                [18, 19, 20], [21, 22, 23],
                [0, 9, 21], [3, 10, 18], [6, 11, 15],
                [1, 4, 7], [16, 19, 22], [8, 12, 17],
                [5, 13, 20], [2, 14, 23]
            ]
            return sum(all(self.board[p] == player for p in mill) for mill in mills)

        def count_blocked_pieces(player):
            if self.phase == 'flying':
                return 0
            return sum(
                all(self.board[adj] != self.EMPTY for adj in self.ADJACENT_POINTS[pos])
                for pos in range(24) if self.board[pos] == player
            )

        def count_two_and_three_piece_configs(player):
            mills = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],
                [9, 10, 11], [12, 13, 14], [15, 16, 17],
                [18, 19, 20], [21, 22, 23],
                [0, 9, 21], [3, 10, 18], [6, 11, 15],
                [1, 4, 7], [16, 19, 22], [8, 12, 17],
                [5, 13, 20], [2, 14, 23]
            ]
            two_piece = three_piece = 0
            # Can use a set, a piece can only be part of 2 two piece configs
            seen = set()
            for mill in mills:
                # Check if we have a two piece config
                if sum(1 for p in mill if self.board[p] == player) == 2 and \
                   sum(1 for p in mill if self.board[p] == self.EMPTY) == 1:
                    two_piece += 1
                    # Check if we have a three piece config
                    three_piece += any(p for p in mill if self.board[p] == player and p in seen)

                    seen.update(p for p in mill if self.board[p] == player)

            return two_piece, three_piece

        def count_double_mills(player):
            shared_positions = [i for i in range(24) if self.board[i] == player]
            count = 0
            for pos in shared_positions:
                mill_count = sum(1 for mill in [
                    [0, 1, 2], [3, 4, 5], [6, 7, 8],
                    [9, 10, 11], [12, 13, 14], [15, 16, 17],
                    [18, 19, 20], [21, 22, 23],
                    [0, 9, 21], [3, 10, 18], [6, 11, 15],
                    [1, 4, 7], [16, 19, 22], [8, 12, 17],
                    [5, 13, 20], [2, 14, 23]
                ] if pos in mill and all(self.board[p] == player for p in mill))
                if mill_count > 1:
                    count += 1
            return count

        def is_losing(player):
            return (self.pieces_on_board[player] + self.pieces_to_place[player] < 3) \
                or not self.has_valid_moves(player)

        weights = {
            "placing": {
                "mill": 26,
                "blocked": 1,
                "two_piece": 10,
                "three_piece": 7,
                "double_mill": 7,
                "piece_count": 9,
                "win": 0,
            },
            "moving": {
                "mill": 43,
                "blocked": 10,
                "two_piece": 0,
                "three_piece": 0,
                "double_mill": 8,
                "piece_count": 11,
                "win": 1086,
            },
            "flying": {
                "mill": 0,
                "blocked": 0,
                "two_piece": 10,
                "three_piece": 1,
                "double_mill": 25,
                "piece_count": 0,
                "win": 1190,
            }
        }

        max_player = self.MAX_PLAYER
        min_player = self.MIN_PLAYER

        weights_used = weights[self.phase]
        score = 0
        score += weights_used["mill"] * (count_mills(max_player) - count_mills(min_player))
        score += weights_used["blocked"] * (count_blocked_pieces(min_player) - count_blocked_pieces(max_player))
        two_piece_max_player, three_piece_max_player = count_two_and_three_piece_configs(max_player)
        two_piece_min_player, three_piece_min_player = count_two_and_three_piece_configs(min_player)
        score += weights_used["two_piece"] * (two_piece_max_player - two_piece_min_player)
        score += weights_used["three_piece"] * (three_piece_max_player - three_piece_min_player)
        score += weights_used["double_mill"] * (count_double_mills(max_player) - count_double_mills(min_player))
        score += weights_used["piece_count"] * (self.pieces_on_board[max_player] - self.pieces_on_board[min_player])

        if is_losing(min_player):
            score += weights_used["win"]
        elif is_losing(max_player):
            score -= weights_used["win"]

        return score

    def __repr__(self):
        rows = []
        for i in range(24):
            if i % 3 == 0:
                rows.append("\n")
            rows[-1] += self.board[i] + ' '
        return "".join(rows) + f"\nPlayer: {self.current_player}, Phase: {self.phase}"
