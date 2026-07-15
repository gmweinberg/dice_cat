#!/usr/bin/python

from collections import defaultdict
from random import randint
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="dice_cat_user",
    password="dice_cat_pw",
    database="dice_cat",
)



def insert_carlo_probs(loops):
    """Use a monte carlo simulation to calculate the probability of
       getting final results for various targets."""
    cursor = conn.cursor()
    sql = """REPLACE INTO pig_prob (target, total, plus0, plus1, plus2,
            plus3, plus4, plus5, loops)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    pig_sums = defaultdict(lambda: [0] * 6)
    for ii in range(loops):
        if ii % 10000 == 0:
            print("ii", ii)
        old = 0
        sum_ = 0
        while(True):
            new = randint(1, 6)
            if new == 1:
                break
            sum_ += new
            # update success here
            for iii in range(new):
                pig_sums[old  + 1 + iii][new - (1 + iii)] += 1
            old = sum_

    # pig sums
    max_ = max(pig_sums.keys())
    for ii in range(2, max_):
        params = []
        params.append(ii) # target
        params.append(1.0 * sum(pig_sums[ii]) / loops) # total prob
        for iii in range(6):
            params.append(1.0 * pig_sums[ii][iii] / loops)
        params.append(loops)
        cursor.execute(sql, params)
    conn.commit()


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--probs', action='store_true')
    parser.add_argument('--loops', type=int, default=100000)
    args = parser.parse_args()
    if args.probs:
        insert_carlo_probs(args.loops)
