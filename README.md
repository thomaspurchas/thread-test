Written for python3, using no external libraries (except `pytest` for
testing).

To run:

    python3 alien_invasion.py world_map_medium.txt 10

Run python3 alien_invasion -h for list of arguments.

To test, create a virtualenv and run:

    pip install pytest
    pytest

This approach uses objects for everything, this has the side-effect of
many side-effects. But the encapsulation is clean enough that relying
on side-effect shouldn't effect readability.

The `Board` object is responsible for storing high-level game state,
mostly sets of things that are living or dead. This makes it quick and
easy to evaluate current game state, and allows us to avoid unnecessary
searching.

The `City` objects are responsible for managing the existence of a
city, and storing relevant city state. They are also responsible for
updating the `Board` of changes to city state (occupied, destroyed).

The `Alien` objects are responsible for managing the existence of a
alien, and storing relevant alien state. They are also responsible for
updating the `Board` of changes to alien state (alive, dead). They also
decide where an alien will move too on each tick, and responsible for
informing the `City`s of these moves.

The map parsing is done via regex, this is a quick clean way to parse
the simple input files. It is also very robust to strange naming (e.g
calling a city `north=`).

The main loop is in `run_game` and on each loop asks every living alien
to make a move, then `check_occupancy` checks each occupied city for
potential alien fights. If a fight is found, then the involved aliens
die (there can be more than 2) and the city is destroyed. Once all alien
have made the max number of moves, or all cities are destroyed the game
ends.
