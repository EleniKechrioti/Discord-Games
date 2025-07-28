import random
from datetime import datetime
import os

file_path = os.path.join(os.path.dirname(__file__), "words.txt")

with open(file_path, "r", encoding="utf-8") as f:
    words = [line.strip() for line in f]



def get_random_word():
    """
    Επιλέγει τυχαία μία λέξη από τη λίστα για χρήση ως λέξη-στόχος.
    Returns:
        str: Η επιλεγμένη λέξη.
    """
    today = datetime.utcnow().date()
    seed = int(today.strftime("%Y%m%d"))  
    rng = random.Random(seed)
    return rng.choice(words)