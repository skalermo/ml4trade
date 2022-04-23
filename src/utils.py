import random
from typing import List


def run_in_random_order(functions_and_calldata: List[callable]) -> None:
    random.shuffle(functions_and_calldata)
    for f in functions_and_calldata:
        f()
