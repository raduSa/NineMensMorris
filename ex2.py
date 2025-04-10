import time
from NineMenMorrisClass import NineMensMorris


def minimax_alpha_beta(state, depth, max_depth, alpha, beta):
    if state.is_terminal() or depth >= max_depth:
        return state.evaluate(), [state]

    successors = state.get_successors()

    if state.current_player == state.MAX_PLAYER:  # MAX player
        best_value = float('-inf')
        best_path = []
        for succ in successors:
            eval_score, path = minimax_alpha_beta(succ, depth + 1, max_depth, alpha, beta)
            if eval_score > best_value or (eval_score == best_value and len(best_path) > len(path)):
                best_value = eval_score
                best_path = path

            # Alpha-Beta Pruning
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break

        return best_value, [state] + best_path

    else:  # MIN player
        best_value = float('inf')
        best_path = []
        for succ in successors:
            eval_score, path = minimax_alpha_beta(succ, depth + 1, max_depth, alpha, beta)
            if eval_score < best_value or (eval_score == best_value and len(best_path) > len(path)):
                best_value = eval_score
                best_path = path

            # Alpha-Beta Pruning
            beta = min(beta, best_value)
            if beta <= alpha:
                break

        return best_value, [state] + best_path


def minimax(state, depth, max_depth):
    """Generalized Minimax Algorithm for Two-Player Games.

    Args:
        state (GameState): The current game state.
        depth (int): Current search depth.
        max_depth (int): Maximum depth for search.

    Returns:
        tuple: (best score, best move sequence)
    """
    if state.is_terminal() or depth >= max_depth:
        return state.evaluate(), [state]

    successors = state.get_successors()

    if state.current_player == state.MAX_PLAYER:
        best_value = float('-inf')
        best_path = []
        for succ in successors:
            eval_score, path = minimax(succ, depth + 1, max_depth)
            if eval_score > best_value or (eval_score == best_value and len(best_path) > len(path)):
                best_value = eval_score
                best_path = path
        return best_value, [state] + best_path

    else:  # MIN player
        best_value = float('inf')
        best_path = []
        for succ in successors:
            eval_score, path = minimax(succ, depth + 1, max_depth)
            if eval_score < best_value or (eval_score == best_value and len(best_path) > len(path)):
                best_value = eval_score
                best_path = path
        return best_value, [state] + best_path


def main():
    start_time = time.time()

    initial_state = NineMensMorris([
    'X', '_', 'O',  # potential two-piece at [0,2]
    '_', '_', '_',
    '_', '_', '_',
    'X', 'X', 'X',
    '_', '_', 'O',
    '_', 'X', '_',
    '_', 'X', '_',
    'X', '_', 'O'], current_player=NineMensMorris.MAX_PLAYER, pieces_to_place=(0, 0))
    max_depth = 3
    best_eval, best_path = minimax_alpha_beta(initial_state, 0, max_depth, float('-inf'), float('inf'))
    # best_eval, best_path = minimax(initial_state, 0, max_depth)
    print("Best Evaluation Score:", best_eval)
    for step, state in enumerate(best_path):
        print(f"\nStep {step}:")
        print(state)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n{elapsed_time}")


main()
