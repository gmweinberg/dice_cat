#!/usr/bin/python

import mysql.connector
from itertools import combinations_with_replacement, product
from math import factorial
from collections import Counter

def roll_weight(roll):
    n = len(roll)
    counts = Counter(roll)
    weight = factorial(n)
    for c in counts.values():
        weight //= factorial(c)
    return weight

def all_rolls(dice):
    yield from combinations_with_replacement(range(1, 7), dice)

def all_rolls_test(dice):
    for result in all_rolls(dice):
        print(result)

def all_choices(held, roll):
    held_counts = Counter(held)
    roll_counts = Counter(roll)

    faces = sorted(roll_counts)

    # For each face, choose how many of that face to newly hold.
    ranges = [range(roll_counts[face] + 1) for face in faces]

    for add_amounts in product(*ranges):
        if sum(add_amounts) == 0:
            continue  # must hold at least one additional die

        choice_counts = held_counts.copy()

        for face, amount in zip(faces, add_amounts):
            choice_counts[face] += amount

        # Return canonical sorted tuple.
        yield tuple(
            face
            for face in sorted(choice_counts)
            for _ in range(choice_counts[face])
        )

def score_dice(dice):
    one = False;
    four = False;
    sum_ = 0;
    for die in dice:
        if die == 1:
            if one:
                sum_ += 1
            else:
                one = True
        elif die == 4:
            if four:
                sum_ += 4
            else:
                four = True
        else:
            sum_ += die
    if one and four:
        return sum_
    return 0 # fail to qualify

def get_util(new, old, tied):
    if new > old:
        return players - 1
    if tied or new == old:
        return 0
    return -1

def add_probs(old_probs, new_probs, weight):
    for key in new_probs:
        if key in old_probs:
            old_probs[key] += new_probs[key] * weight
        else:
            old_probs[key] = new_probs[key] * weight


conn = mysql.connector.connect(
    host="localhost",
    user="dice_cat_user",
    password="dice_cat_pw",
    database="dice_cat",
)

cursor = conn.cursor()

players = 0
drawish = False
expects = {}
held_probs = {}
iters = 0


def final_probs(high_score, tied, held=None):
    """Return a tuple (utility, probs) where probs is a dict of probabilities
       of scoring x. We only care about values >= high_score."""
    global held_probs
    global iters
    iters += 1
    if iters % 100 == 0:
        pass
        #print(iters)
    if held is None:
        held = []
    if held == []:
        held_probs = {}
    if len(held) == 6: #  no choices, no chances
        score = score_dice(held)
        utility = get_util(score, high_score, tied)
        if utility < 0:
            return (utility, {})
        return (utility, {score: 1.0})
    total_probs = {}
    result_util = 0
    total_weight = 0.0
    for roll in all_rolls(6 - len(held)):
        total_weight += roll_weight(roll)
    for roll in all_rolls(6 - len(held)):
        max_util = -2
        best_probs = {}
        weight = roll_weight(roll) / total_weight
        for achoice in all_choices(held, roll):
            if achoice in held_probs:
                utility, probs =  held_probs[achoice]
            else:
               utility, probs = final_probs(high_score, tied, achoice)
               held_probs[achoice] = (utility, probs)
            if utility > max_util: # TODO handle tie breaker
                best_probs = probs
                max_util = utility
        add_probs(total_probs, best_probs, weight)
        result_util += max_util * weight

    if not held:
        for prob_key in total_probs:
            expects[prob_key] = total_probs[prob_key]
        print(expects)

    return result_util, total_probs


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--players', type=int, default=2)
    parser.add_argument('--after', type=int, default=0)
    parser.add_argument('--score', type=int)
    parser.add_argument('--start', default='')
    parser.add_argument('--tied', action='store_true')
    parser.add_argument('--drawish', action='store_true')
    args = parser.parse_args()
    players = args.players
    drawish = args.drawish
    if args.score is not None:
        final_probs(args.score, False)


