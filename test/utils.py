from operator import itemgetter


def load_from_setup(setup: dict, *args) -> tuple:
    return itemgetter(*args)(setup)
