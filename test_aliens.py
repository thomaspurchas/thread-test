import pytest
from alien_invasion import Board, City, Alien, check_occupancy, \
                           parse_map_and_setup_board, setup_game, \
                           save_cities

@pytest.fixture
def board():
    return Board()

@pytest.fixture
def test_map():
    return parse_map_and_setup_board('test_map.txt')

def get_city_by_name(name, board):
    for city in board.living_cities | board.destroyed_cities:
        if city.name == name:
            return city
    else:
        return None

def test_living_cities(board):
    c1 = City('1', None, None, None, None, board)
    c2 = City('2', None, None, None, None, board)

    assert len(board.living_cities) == 2
    assert c1 in board.living_cities and c2 in board.living_cities

def test_city_destroy(board):
    city = City('1', None, None, None, None, board)

    assert len(board.living_cities) == 1

    city.destroy()

    assert len(board.living_cities) == 0
    assert len(board.destroyed_cities) == 1

def test_alien_enter_city(board):
    city = City('1', None, None, None, None, board)
    alien = Alien('a1', city, board)

    assert alien in city.occupying_aliens
    assert len(city.occupying_aliens) == 1

    alien2 = Alien('a2', city, board)

    assert len(city.occupying_aliens) == 2
    assert alien2 in city.occupying_aliens and alien in city.occupying_aliens

def test_alien_move(board):
    city1 = City('1', None, None, None, None, board)
    city2 = City('2', None, None, None, None, board)

    city1.north = city2
    city2.south = city1

    alien = Alien('a', city1, board)

    assert alien in city1.occupying_aliens

    alien.move()

    assert alien in city2.occupying_aliens

def test_alien_destroy_city(board):
    city1 = City('1', None, None, None, None, board)
    city2 = City('2', None, None, None, None, board)
    city3 = City('3', None, None, None, None, board)

    city1.south = city2
    city2.north = city1
    city2.south = city3
    city3.north = city2

    alien1 = Alien('a1', city1, board)
    alien2 = Alien('a2', city3, board)

    assert alien1 in city1.occupying_aliens
    assert alien2 in city3.occupying_aliens
    assert len(city2.occupying_aliens) == 0

    alien1.move()
    alien2.move()

    assert len(city2.occupying_aliens) == 2
    assert alien1 in city2.occupying_aliens and alien2 in city2.occupying_aliens

    check_occupancy(board)

    assert city2 in board.destroyed_cities
    assert city2 not in board.living_cities

    assert alien2.alive == False and alien1.alive == False
    assert alien1 in board.dead_aliens and alien2 in board.dead_aliens
    assert alien1 not in board.living_aliens and alien2 not in board.living_aliens

def test_map_parsing_and_board_setup():
    board = parse_map_and_setup_board('test_map.txt')

    assert len(board.living_cities) == 10
    assert len(board.destroyed_cities) == 0
    assert len(board.living_aliens) == 0
    assert len(board.dead_aliens) == 0

    north = get_city_by_name('North', board)
    south = get_city_by_name('South', board)
    east = get_city_by_name('East', board)
    west = get_city_by_name('West', board)
    centre = get_city_by_name('centre', board)

    assert north is not None
    assert south is not None
    assert east is not None
    assert west is not None
    assert centre is not None

    assert north.south == centre
    assert south.north == centre
    assert east.west == centre
    assert west.east == centre
    assert centre.north == north
    assert centre.south == south
    assert centre.west == west
    assert centre.east == east

def test_map_parsing_hard(test_map):
    north = get_city_by_name('North city1', test_map)
    centre  = get_city_by_name('centre city', test_map)
    west = get_city_by_name('west city1', test_map)

    assert north is not None
    assert centre is not None
    assert west is not None

    assert north.south == centre
    assert north.west == west
    assert centre.north == north
    assert west.east == north

def test_map_parsing_harder(test_map):
    north = get_city_by_name('north=', test_map)
    east = get_city_by_name('east=', test_map)

    assert north is not None
    assert east is not None

    assert north.south == east
    assert east.north == north

def test_game_setup(test_map):
    board = test_map

    board = setup_game(board, 4)

    assert len(board.living_aliens) == 4
    assert len(board.occupied_cities) == 4

    for city in board.occupied_cities:
        assert len(city.occupying_aliens) == 1

def test_board_save(test_map, tmpdir):
    tmp_file = tmpdir.join('test_output.txt')
    save_cities(tmp_file, test_map)

    board2 = parse_map_and_setup_board(tmp_file)

    assert len(test_map.living_cities) > 0
    assert len(board2.living_cities) == len(test_map.living_cities)
