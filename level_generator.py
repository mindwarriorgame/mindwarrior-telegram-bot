import json
import random

FIRST_LEVELS_0_1 = [
    ["f0", "s0", "c0"],
    ["s1", "t0", "c0", "c0"],
    ["s0", "s1", "c0"],
    ["s0", "s1", "t0", "c0", "c0"],
    ["c0", "c1", "f0"],
    ["f0", "s2", "c2", "c0", "c0"],
]

FIRST_LEVELS_2_3 = [
    ["f0", "s0", "s1", "c0"],
    ["s1", "t0", "c0", "c1", "c0"],
    ["s0", "s1", "s2", "f0", "f0", "c0"],
    ["s0", "s1", "t0", "t0", "c0", "c0", "c0", "c0"],
    ["c0", "c1", "f0", "c0", "t0"],
    ["f0", "s2", "t0", "c1", "c2", "c0", "c0"],
]

FIRST_LEVEL_4 = [
    ["f0", "s0", "s1", "s2", "c0"],
    ["s1", "s2", "t0", "c0", "c1", "c0"],
    ["s0", "s1", "s2", "c1", "f0", "f0", "c0"],
    ["s0", "s1", "t0", "c2", "c0", "c0", "c0", "c0"],
    ["c0", "c1", "c2", "s2", "f0", "c0", "t0"],
    ["f0", "s2", "t0", "c1", "c2", "c2", "c0", "c0"],
]

def generate_levels(difficulty: int):
    badges = ["f0", "s0", "s1", "s2", "t0", "c0", "c1", "c2"]

    new_levels = []
    for levelNo in range(5, 50):
        len_min = [5, 5, 7, 7, 9]
        len_max = [10, 10, 13, 13, 15]
        random_length = random.randint(len_min[difficulty], len_max[difficulty])
        level = []
        for levelBadge in range(random_length):
            level.append(random.choice(badges))
        new_levels.append(level)

    print(f"Difficulty: {difficulty}")
    print(json.dumps(new_levels))

def generate_over_50_level_pick_indices():
    indices = []

    for _ in range(0, 100):
        indices += [random.randint(0, 1024)]

    print(f"Indices:")
    print(json.dumps(indices))

# Pre-generate to make sure all levels are deterministically all the time across all players
NEXT_LEVELS_0_1 = [["f0", "s1", "c1", "c1", "s2", "t0", "s0", "s0", "t0"], ["f0", "t0", "t0", "c0", "c0", "s0", "s2", "s1", "s0"], ["s2", "c2", "c0", "s0", "f0", "t0", "t0", "s2", "t0", "c2"], ["t0", "c0", "s0", "c1", "s2", "s0"], ["s2", "c0", "c2", "t0", "c2", "s1", "s1"], ["s0", "c0", "s0", "s0", "s0", "s1"], ["s2", "c2", "f0", "c0", "s1", "t0", "t0", "c2", "s1"], ["f0", "s0", "t0", "f0", "c2", "s2", "s0", "s2"], ["c1", "s1", "c2", "c2", "t0", "c2", "c0", "f0"], ["c2", "t0", "c1", "c0", "f0", "s2", "s0", "c0", "f0"], ["s1", "s1", "s2", "f0", "c2", "s0"], ["t0", "c2", "t0", "c1", "c1", "s1", "c0", "c1", "c0", "c2"], ["s1", "s0", "s0", "c2", "s0", "s0"], ["f0", "s0", "s0", "f0", "c2", "c2", "c2", "s0", "c2", "c1"], ["c1", "s1", "s0", "s2", "s1", "s2", "c0", "s1", "s1", "s1"], ["t0", "t0", "c0", "s2", "c2"], ["s0", "c1", "c1", "c0", "s1", "f0", "s1", "c1"], ["c0", "s0", "c2", "s0", "t0"], ["s0", "c2", "s1", "s0", "c0", "c0"], ["c1", "s2", "s1", "c2", "c1", "s2", "f0"], ["c1", "s0", "s1", "s0", "t0", "c2", "t0"], ["c0", "s2", "c2", "c2", "c0", "f0", "c2", "f0", "t0", "c0"], ["c1", "c0", "s2", "c2", "f0"], ["f0", "s1", "s0", "s0", "c2", "c2", "f0", "s2", "c1"], ["s0", "s2", "s1", "s2", "c2", "c0", "c1", "s2", "s1", "s1"], ["s2", "c1", "s1", "c0", "s1", "s2", "s1", "t0", "f0"], ["c2", "s2", "c1", "c1", "t0", "s2", "c2", "s2"], ["s0", "s2", "s1", "c1", "f0", "s2", "t0"], ["f0", "s2", "c2", "c1", "s1", "f0", "s1", "c2"], ["c1", "s0", "c2", "c1", "s1", "c0", "c0"], ["s0", "c0", "s1", "c1", "s2", "f0"], ["c0", "c1", "s2", "s0", "f0", "s1", "s2"], ["f0", "t0", "c2", "c1", "t0", "c0", "s2", "f0", "c0", "s1"], ["s2", "c2", "t0", "c2", "c0", "c2", "s0", "c2", "s1", "s2"], ["s0", "s0", "c1", "f0", "c1", "s2", "s1", "s1"], ["c1", "t0", "t0", "f0", "c1"], ["c1", "s0", "s1", "s0", "s1"], ["t0", "s0", "s0", "s0", "f0", "c2"], ["s0", "s1", "c2", "f0", "c1", "c1", "c2", "c2", "c1", "s0"], ["s0", "f0", "s1", "s0", "s2", "s0"], ["s2", "s0", "c1", "t0", "f0", "s0", "s2", "t0", "s2"], ["c2", "s2", "t0", "t0", "s2", "s1", "c2"], ["c1", "f0", "s1", "s0", "s0", "s2", "c0", "s2", "s1", "c1"], ["f0", "s1", "s0", "s1", "s1", "c0", "c1", "c0", "s0"], ["s1", "c1", "t0", "c2", "c1", "s0", "t0", "f0", "c0", "t0"]]
NEXT_LEVELS_2_3 = [["s2", "f0", "c0", "c1", "s0", "s1", "s2", "c0", "s0", "f0", "s2", "s1", "c1"], ["s1", "c2", "t0", "c1", "f0", "c1", "f0", "s1", "c2", "f0", "c1"], ["c1", "c1", "f0", "c1", "t0", "s0", "c2", "s1", "t0", "c1"], ["t0", "s0", "c1", "s2", "s1", "c2", "c2", "c2", "s1", "c2", "t0"], ["s0", "s0", "s0", "s1", "s0", "t0", "c1", "s2", "s1", "t0", "s1", "c1", "s0"], ["c1", "s1", "c2", "c2", "s1", "s2", "t0", "t0"], ["c2", "s0", "t0", "s1", "s2", "f0", "t0", "c1"], ["t0", "s1", "t0", "c2", "s2", "c0", "s0", "t0", "c1", "s0", "s0", "c2", "c1"], ["t0", "f0", "t0", "t0", "c2", "t0", "c0", "s2", "t0", "c2", "s1", "s2"], ["s1", "s0", "s1", "s2", "c2", "c0", "s1", "f0", "c0", "t0", "s1"], ["s2", "c1", "c2", "t0", "s1", "f0", "t0"], ["s1", "t0", "c0", "s0", "c1", "s0", "c0", "s2", "t0"], ["t0", "t0", "s1", "s1", "c0", "c2", "s1", "c1"], ["c1", "t0", "c2", "f0", "c2", "s0", "s0", "s1"], ["s1", "s1", "f0", "c0", "c0", "s2", "t0", "f0", "f0", "s0", "c1", "c0", "s2"], ["t0", "c0", "s1", "c0", "c2", "c2", "s0", "t0", "s1"], ["c1", "c1", "f0", "s1", "s0", "f0", "c2", "s2"], ["s0", "c2", "c1", "s1", "f0", "s1", "s1", "c2", "s1", "s2", "s1", "t0"], ["c2", "s1", "s1", "s0", "c1", "s2", "f0", "s1", "f0"], ["s2", "s1", "s2", "s0", "s0", "s2", "c1", "c2", "c2", "s1"], ["s2", "c2", "c2", "c0", "c0", "s2", "f0"], ["c2", "f0", "c0", "s2", "f0", "c1", "f0", "c0", "c0", "c1", "c1"], ["t0", "c2", "c2", "f0", "f0", "c2", "t0"], ["c1", "s0", "s2", "s1", "s1", "t0", "c2", "s0", "c0", "s1", "s0", "t0"], ["c2", "f0", "c1", "s0", "s2", "f0", "s2", "s0", "f0", "c1", "f0", "c1"], ["c2", "s0", "c1", "c0", "s1", "t0", "f0", "s2", "c1", "c0", "s1", "t0"], ["c0", "c2", "t0", "t0", "s0", "s2", "c0", "c0"], ["t0", "c0", "t0", "c2", "s0", "s0", "s0", "c1", "c1", "s2"], ["s2", "c0", "f0", "c1", "s0", "c1", "c2", "s0", "c1", "c2"], ["c0", "s0", "s1", "f0", "c1", "t0", "s2", "s0"], ["c0", "c0", "c0", "c1", "c1", "f0", "f0", "c1", "c2", "s1", "c1", "c0", "c0"], ["c2", "t0", "c2", "c2", "s0", "t0", "f0"], ["s2", "c0", "s1", "t0", "s1", "f0", "c2"], ["s1", "t0", "c0", "c2", "f0", "c0", "c1"], ["s1", "t0", "s1", "c0", "c2", "c0", "f0", "c2", "c1", "s0", "c0", "f0"], ["c1", "f0", "c1", "t0", "s0", "c2", "f0", "s0", "s2", "c0", "s1", "s1", "f0"], ["c0", "s0", "c0", "f0", "c2", "s0", "c0", "s1", "s1"], ["f0", "c1", "s1", "t0", "s1", "f0", "s1", "t0", "s2", "c1"], ["c1", "s1", "t0", "s1", "t0", "c1", "s2", "s2", "c2", "c2", "c2", "c1"], ["c0", "c1", "t0", "s2", "s2", "s0", "s0", "f0", "s2", "c2", "c0"], ["c0", "c2", "c0", "s0", "t0", "c2", "s2", "c2"], ["s0", "s2", "s1", "s1", "c0", "f0", "f0", "c0", "t0", "f0", "c2", "s0"], ["t0", "s1", "c1", "s2", "c0", "s0", "c2", "s0", "c0", "c0", "c0", "s2", "t0"], ["c0", "s1", "t0", "c1", "c0", "s0", "s2"], ["s1", "c1", "c1", "c2", "s2", "s0", "c0", "f0", "c1", "s0", "t0"]]
NEXT_LEVELS_4 = [["t0", "c1", "t0", "f0", "f0", "s2", "t0", "c1", "s1", "c0", "c0", "t0", "s0", "c2", "s2"], ["s0", "c2", "s2", "c0", "s2", "s0", "t0", "c2", "t0", "c0", "c1", "s2"], ["s0", "t0", "s1", "c0", "c1", "c1", "s2", "f0", "t0", "t0", "s1", "c1", "c1"], ["c1", "t0", "c2", "c2", "s1", "s0", "s0", "c0", "t0", "t0", "s1", "s1"], ["f0", "t0", "c2", "s1", "s0", "c0", "c0", "s2", "t0", "f0", "t0"], ["c1", "s2", "s1", "c1", "c1", "s0", "s2", "s1", "s2"], ["t0", "s1", "s0", "s1", "s0", "s1", "s0", "s1", "s0", "c1"], ["c2", "f0", "c0", "f0", "t0", "c1", "s2", "f0", "f0", "t0"], ["t0", "s2", "c0", "s2", "c2", "c2", "c2", "s0", "s1", "t0", "s2", "c2", "s0", "c2", "c2"], ["s0", "s2", "c0", "c0", "s2", "c1", "s2", "s2", "t0"], ["s1", "s0", "f0", "t0", "f0", "c1", "c2", "s0", "f0", "s1"], ["s1", "c0", "t0", "c2", "c1", "s0", "c0", "s1", "s1", "c1", "c1", "s0", "s0"], ["s2", "s0", "c2", "t0", "s2", "s1", "f0", "c1", "s2", "c1"], ["s2", "s2", "s2", "s1", "t0", "t0", "f0", "s1", "s2"], ["c2", "c2", "c1", "c0", "c2", "s2", "c1", "c2", "s2"], ["c0", "s0", "s1", "f0", "c1", "c1", "c0", "c1", "c2", "c0", "s1", "c2", "c1"], ["c0", "t0", "s1", "c2", "c0", "c0", "c0", "c0", "c0", "c0", "s1", "f0", "s1"], ["f0", "c1", "c1", "s1", "s2", "s0", "c2", "f0", "c2", "s2", "s0", "c0", "t0", "c1", "c2"], ["c0", "c2", "c0", "f0", "t0", "s0", "s0", "s0", "t0", "c2", "s1"], ["t0", "c2", "c2", "f0", "t0", "c1", "t0", "c0", "c1", "s2", "c2", "s2"], ["c0", "c2", "c0", "t0", "c0", "s1", "s0", "c0", "s1"], ["s2", "c2", "s2", "t0", "c1", "c2", "s0", "f0", "s0", "c0", "t0", "s2", "f0", "f0", "s1"], ["f0", "c1", "f0", "s0", "s2", "c1", "s2", "c1", "s0", "c2", "s2", "s2"], ["s0", "c0", "c0", "s0", "s1", "s1", "c2", "s0", "c1", "f0", "s0", "s0", "s2", "c1", "c0"], ["c0", "f0", "c2", "s1", "f0", "s0", "c1", "c0", "c0", "t0", "c1", "t0"], ["c2", "c1", "c0", "c0", "s0", "s1", "c1", "f0", "c1", "t0"], ["c1", "s0", "c1", "s0", "c2", "s2", "c0", "s1", "s1", "f0", "s0", "c1", "s1", "c0"], ["c2", "f0", "s1", "c2", "c1", "f0", "c0", "s0", "s1", "c2"], ["t0", "c2", "c0", "c1", "f0", "s1", "c1", "f0", "s0", "t0", "s2", "f0", "c0", "s1", "s0"], ["s2", "t0", "s2", "c1", "s1", "c1", "c2", "s2", "s0", "c0", "s1", "c1", "c0", "c0", "c0"], ["t0", "s2", "c2", "s0", "c1", "s1", "f0", "s0", "s0", "s0"], ["c1", "c1", "t0", "f0", "c1", "s1", "s2", "c1", "f0"], ["c0", "s2", "s1", "t0", "s2", "s0", "t0", "f0", "c2", "c2"], ["c2", "t0", "c2", "f0", "s1", "s2", "t0", "f0", "s1", "c2", "c1", "s0"], ["c0", "t0", "c1", "f0", "s0", "c2", "t0", "c1", "c0", "s2", "c2", "s0", "c0", "t0", "t0"], ["s1", "s0", "c2", "s2", "c0", "c0", "s1", "c0", "c1", "s2", "c0", "t0", "s1", "c1"], ["c2", "c0", "c2", "t0", "c2", "f0", "s0", "f0", "s2", "s0", "s0"], ["c2", "s2", "s0", "c2", "t0", "c2", "s0", "s0", "s1", "f0", "s1", "c2", "c2", "s2", "s1"], ["c1", "s2", "c1", "s2", "s0", "s2", "s2", "s1", "s1", "c0", "c1", "c0", "c1", "s1", "c0"], ["t0", "s0", "c0", "s0", "c2", "s2", "f0", "c2", "c2", "f0", "s1", "c1", "s2"], ["s0", "s1", "s1", "c1", "f0", "f0", "c0", "s1", "s2", "s1", "t0", "c1"], ["t0", "s1", "s1", "t0", "s1", "f0", "c0", "c1", "s0", "s0", "t0"], ["s2", "s2", "c0", "f0", "c1", "c0", "s2", "c2", "t0", "s2", "f0"], ["c2", "c1", "s2", "c1", "s1", "t0", "c1", "s1", "c1", "t0", "c0"], ["t0", "c2", "t0", "f0", "c0", "s0", "f0", "s0", "s1"]]
NEXT_LEVEl_OVER_50_PICK_INDICES = [371, 167, 279, 723, 166, 799, 215, 14, 81, 865, 363, 59, 9, 786, 443, 650, 69, 30, 1004, 107, 207, 653, 134, 360, 401, 884, 85, 317, 303, 126, 320, 263, 442, 165, 5, 492, 829, 788, 127, 225, 324, 783, 560, 41, 741, 317, 541, 65, 984, 176, 930, 55, 444, 251, 276, 61, 943, 128, 591, 957, 589, 102, 745, 721, 609, 535, 938, 573, 670, 699, 946, 62, 19, 820, 432, 584, 111, 249, 707, 669, 90, 706, 67, 393, 419, 1019, 786, 448, 256, 1, 234, 535, 178, 647, 389, 790, 50, 0, 620, 637]



def get_level(difficulty: int, level_starting_zero: int):
    if level_starting_zero < len(FIRST_LEVELS_0_1):
        return FIRST_LEVELS_0_1[level_starting_zero] if difficulty < 2 else FIRST_LEVELS_2_3[level_starting_zero] if difficulty < 4 else FIRST_LEVEL_4[level_starting_zero]

    shifted_level = level_starting_zero - len(FIRST_LEVELS_0_1)
    next_levels = NEXT_LEVELS_0_1 if difficulty < 2 else NEXT_LEVELS_2_3 if difficulty < 4 else NEXT_LEVELS_4
    if shifted_level < len(next_levels):
        return next_levels[shifted_level]

    idx = shifted_level - len(next_levels)
    pick_index = NEXT_LEVEl_OVER_50_PICK_INDICES[idx % len(NEXT_LEVEl_OVER_50_PICK_INDICES)]

    return next_levels[pick_index % len(next_levels)]

