from datetime import date
import random

TOPICS = [
    "BFS",
    "DFS",
    "Binary Search",
    "Sliding Window",
    "Two Pointers"
]

def get_topic() -> str:
    # give the topic for the day
    today = date.today().isoformat()
    rng = random.Random(today)
    return rng.choice(TOPICS)