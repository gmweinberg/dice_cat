DROP DATABASE dice_cat;

CREATE DATABASE dice_cat;

USE dice_cat;

-- Table showing probability of last player finishing with a given score given
-- the score state. We will only calculate the probability of scoreing
-- greater than or equal to the incoming high score. If tied is true we
-- only care about strictly greater than

CREATE TABLE one_four_probs (
	players int not null,
	after int not null,
  high_score int not null default 0,
	tied bool not null default false,
	score int not null,
	prob float not null,
	primary key (players, after, high_score, tied, score)
);

CREATE USER if not exists dice_cat_user identified by 'dice_cat_pw';

GRANT ALL on dice_cat.* to dice_cat_user;

