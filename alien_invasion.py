import sys
import re
import random
import argparse

# Regex for parsing map files. Read parse_map_and_setup_board docstring for more info
MAP_REGEX = re.compile(r"^(?P<city>.+?)(?: north=(?P<north>.+?)|)(?: south=(?P<south>.+?)|)(?: east=(?P<east>.+?)|)(?: west=(?P<west>.+?)|)$",
                       re.MULTILINE)


class Board:
    def __init__(self):
        """Sets up a new game board"""

        self.cities = []
        self.occupied_cities = set()
        self.living_cities = set()
        self.destroyed_cities = set()
        self.living_aliens = set()
        self.dead_aliens = set()

class City:
    def __init__(self, name, north, south, east, west, board):
        """Sets up a new city. Assumes board has already in initialised"""

        self.name = name
        self.north = north
        self.south = south
        self.east = east
        self.west = west

        self.board = board
        self.board.living_cities.add(self)

        self.occupying_aliens = set()

    def destroy(self):
        """
        Mark a city as destroyed, setting all city links to None, on
        both sides of the link.

        Also update the game board reflect the new status.
        """
        if self.north:
            self.north.south = None
        if self.south:
            self.south.north = None
        if self.east:
            self.east.west = None
        if self.west:
            self.west.east = None

        self.north = None
        self.south = None
        self.east = None
        self.west = None

        self.board.living_cities.discard(self)
        self.board.occupied_cities.discard(self)
        self.board.destroyed_cities.add(self)

    def add_alien(self, alien):
        """
        Adds an alien to the cities occupation.

        Also updates board of cities occupation status change
        """

        self.occupying_aliens.add(alien)

        self.board.occupied_cities.add(self)

    def remove_alien(self, alien):
        """
        Removes and occupying alien.

        Also updates board if the cities occupation status changes.
        """

        self.occupying_aliens.remove(alien)

        if len(self.occupying_aliens) < 1:
            self.board.occupied_cities.discard(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        desc = "<City(name={}, north={}, south={}, east={}, west={}, occupying_aliens={}>"
        return desc.format(self.name, self.north, self.south,
                           self.east, self.west, self.occupying_aliens)

class Alien:
    def __init__(self, name, starting_city, board):
        """
        Setup alien. It is assumed that the starting_city is on the
        board and already initialised.
        """

        self.name = name
        self.current_city = starting_city
        self.board = board

        self.current_city.add_alien(self)
        self.board.living_aliens.add(self)

        self.moves = 0
        self.alive = True

    def move(self):
        """
        Make the alien move to another city link with the current city.

        Also informs current and future city of the move.
        """

        if not self.alive:
            return

        self.current_city.remove_alien(self)

        valid_moves = ['north', 'south', 'east', 'west']
        valid_moves = [m for m in valid_moves if getattr(self.current_city, m) is not None]

        if len(valid_moves) > 0:
            direction = random.choice(valid_moves)
            self.current_city = getattr(self.current_city, direction)

        self.current_city.add_alien(self)

        self.moves += 1

    def kill(self):
        """
        Mark an alien as dead, and update the game board to reflect this.
        """

        self.alive = False
        self.board.living_aliens.remove(self)
        self.board.dead_aliens.add(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Alien name={}>".format(self.name)


def parse_map_and_setup_board(map_file):
    """
    Parse a map file and create a fully connect board with cities.

    It is assumed that the map_file is geographically valid and that
    city links are always in 'north' 'south' 'east' 'west' order.

    Geographically valid means that each cities links can be traversed
    in both directions e.g:

    north south=south
    south north=north

    is valid but:

    north south=south
    south north=somethingelse

    is not valid. No attempt is made to validate input geography.
    """
    board = Board()

    with open(map_file) as map:
        matches = MAP_REGEX.finditer(map.read())

        for match in matches:
            City(match.group('city'),
                            match.group('north'),
                            match.group('south'),
                            match.group('east'),
                            match.group('west'),
                            board
                )

    city_name_mapping = {c.name: c for c in board.living_cities}

    for city in board.living_cities:
        for direction in ['north', 'south', 'east', 'west']:
            setattr(city, direction, city_name_mapping.get(getattr(city, direction), None))

    return board

def setup_aliens(board):
    """Creates and alien for every occupied city on the board"""

    for i, city in enumerate(board.occupied_cities.copy()):
        Alien(str(i), city, board)

    return board

def setup_game(board, aliens):
    """Setups the game with correct number of aliens, places in random cities"""

    if aliens > len(board.living_cities):
        print("More aliens than cities!")
        exit()

    board.occupied_cities = set(random.sample(board.living_cities, aliens))
    setup_aliens(board)

    return board

def check_occupancy(board):
    """
    Checks occupied cities on the maps for aliens about the fight
    (more than 2 aliens in the same city).

    If aliens about to fight are found, the fight progresses, both aliens die
    and the city is destroyed.
    """
    for city in board.occupied_cities.copy():
        if len(city.occupying_aliens) > 1:
            for alien in city.occupying_aliens:
                alien.kill()

            if len(city.occupying_aliens) == 2:
                list_aliens = list(city.occupying_aliens)
                aliens = 'alien {} and alien {}'.format(
                    list_aliens[0],
                    list_aliens[1]
                )
            else:
                aliens = 'aliens: '
                aliens += ', '.join([str(a) for a in city.occupying_aliens])

            print("💥 City {} destroyed by {} 👽".format(
                city.name,
                aliens
            ))

            city.destroy()

def run_game(board, max_moves=10000):
    """
    Run the game until all aliens have moved a minamum of max_moves,
    there is only a single alien left (no point making them suffer) or
    they have destroyed all the cities (and themselves).
    """

    while True:
        end_game = True

        for alien in board.living_aliens:
            if alien.moves < 10000:
                end_game = False

            alien.move()

        check_occupancy(board)

        if len(board.living_cities) < 0:
            end_game = True
        if len(board.living_aliens) < 1:
            end_game = True

        if end_game:
            break

    return board

def write_cities(fh, board):
    """Writes the remains of the cities to the file handle"""

    for city in board.living_cities:
        line = city.name

        for direction in ['north', 'south', 'east', 'west']:
            linked_city = getattr(city, direction)
            if linked_city is not None:
                line += " {}={}".format(direction, linked_city.name)

        fh.write(line + '\n')

def save_cities(location, board):
    """Write the remains of the cities to either stdout or file"""

    if location == '-':
        write_cities(sys.stdout, board)
    else:
        with open(location, 'w') as fh:
            write_cities(fh, board)

def main(args):
    """Sets up and executes a simulation"""

    board = parse_map_and_setup_board(args.map)
    print("Found {} cities".format(len(board.living_cities)))

    board = setup_game(board, args.aliens)
    run_game(board, args.max_moves)
    save_cities(args.output, board)

def parse_args():
    """Create a command line argument parser"""

    parser = argparse.ArgumentParser(description='Invade some cities!')
    parser.add_argument('map', help="Map file to load")
    parser.add_argument('aliens', type=int, help="Number of aliens to create")
    parser.add_argument('-m', '--max-moves', type=int, help="Maximum number of moves an alien can make", default=10000, dest="max_moves")
    parser.add_argument('-o', '--output', help="Where should the results be written too", default="-", dest="output")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args)
