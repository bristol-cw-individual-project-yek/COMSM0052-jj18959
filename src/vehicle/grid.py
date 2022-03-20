GRID_SQUARE_LENGTH = 10

def position_to_grid_square(position:tuple):
    x = position[0]
    y = position[1]
    grid_x = x // GRID_SQUARE_LENGTH
    grid_y = y // GRID_SQUARE_LENGTH
    return (grid_x, grid_y)