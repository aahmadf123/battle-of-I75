---
title: "The coin toss won't decide the Battle of I-75"
date: 2026-11-18
tags: [football, toledo, analytics, college-football-data]
summary: "Toledo and Bowling Green are 43-43-4 after 90 games. I pulled every public coin toss in the rivalry and 8,310 FBS games to test whether deferring actually helps."
repo: https://github.com/aahmadf123/battle-of-i75
---

Toledo and Bowling Green have played 90 times since 1919. The series is
**43-43-4**. Friday night at the Glass Bowl breaks a 107-year tie.

Before every one of those games, a captain calls a coin in the air. Almost
every winner says the same thing: "We'll defer." Teams want the ball to start
the 2nd half. The idea is the Middle Eight: score late in the 2nd quarter,
then score again on the first drive after halftime.

So I tested it. Does winning the toss and deferring actually help you win?

**Short version:**

- The coin toss doesn't decide games. Across 8,310 FBS games, the team that
  receives the 2nd-half kickoff wins 50.3% of the time.
- Deferring does win the Middle Eight, by just under a point a game.
- That edge doesn't show up on the final scoreboard.
- In this rivalry the 2nd-half receiver is 16-11. That sounds meaningful. With
  27 games, it isn't.

## 1. 107 years, dead even

![Series lead after each game, 1919 to 2025](/field-notes/battle-of-i75/01_series_rollercoaster.png)

The tie hides a long Bowling Green era. BG led the series by as many as 11
games after 1994. Toledo needed 31 years to dig out.

Rivalries get told as a story of streaks, so I checked whether this one is
streakier than chance. I shuffled the 86 decided games 20,000 times.

- **Overall, it isn't.** The real series has 40 runs of consecutive wins. Random
  orderings average 44. About 1 in 4 shuffles is at least as streaky.
- **One stretch is real.** Bowling Green's 12 straight wins (1955 to 1966)
  happen in only 0.8% of shuffles. That run covers Doyt Perry's entire tenure
  as BG's head coach.
- **Toledo's 9 straight (2010 to 2018) is not unusual.** About 1 in 10 shuffles
  has a run that long.

Home field has helped, but less than you'd think. Home teams are 48-38 in
decided games (55.8%). In 86 games that isn't statistically different from a
coin flip (p = 0.33).

## 2. Every coin toss on record

![Every Battle of I-75 coin toss, 1998 to 2025](/field-notes/battle-of-i75/04_every_coin_toss.png)

Official box scores record the toss for 26 of the 28 games since 1998. I pulled
each line word for word. Every one is in the repo with its source link.

- The toss winner deferred **22 of 26** times.
- Four times the winner took the ball: Bowling Green in 2004, 2007 and 2015,
  and Toledo in 2009.
- Toss winners are **13-13**.
- Toledo is 7-3 when it deferred and 7-5 when Bowling Green deferred. No
  meaningful difference (p = 0.68).

Two games can't be coded. The 1998 line says "BG wins toss and defers; Miami
will receive." But Toledo kicked off to start the game and Bowling Green kicked
off to start the 2nd half, which can't happen if BG deferred. The line is a
template error. The 2000 box score has no play-by-play.

## 3. 27 games can't answer the question

![Rivalry sample vs. FBS sample](/field-notes/battle-of-i75/03_sample_size.png)

The 2nd-half receiver is 16-11 in this rivalry (59.3%). It's tempting to stop
there. But the 95% interval runs from 41% to 76%. With 27 games, only an effect
of about 27 percentage points would be detectable. No coin toss is worth that.

So I went to a sample that can answer it: every regular-season FBS vs. FBS game
from 2014 to 2025 in the CollegeFootballData.com database.

The setup is close to a natural experiment. A coin decides who gets the 2nd-half
kickoff. The receivers should look like a random half of all teams, and they do:
their average closing spread is -0.22 and they're at home 49.2% of the time.

## 4. Deferring wins the Middle Eight, not the game

![Middle Eight vs. final result for the 2nd-half receiver](/field-notes/battle-of-i75/02_middle_eight_vs_game.png)

- **Middle Eight:** the 2nd-half receiver outscores its opponent by **+0.93
  points** in the last 4:00 of the 2nd quarter plus the first 4:00 of the 3rd
  (95% CI +0.75 to +1.11, 5,545 games).
- **Final result:** after adjusting for the closing spread, receiving the 2nd
  half changes win probability by **-0.15 percentage points** (95% CI -1.45 to
  +1.16). Against the spread it's -0.17 points.

Why doesn't the Middle Eight edge carry through? My best guess: receiving the
2nd half means kicking off the 1st, so the other team gets the game's first
possession. Over 60 minutes, the possessions even out. I haven't tested that
directly yet.

The result holds up. By season, the 2nd-half receiver's win rate runs from
46.9% to 53.7% with no trend. Dropping 2020 gives 50.2%.

## What to watch Friday

None of this says the toss is irrelevant. Wind matters at the Glass Bowl, and
the box scores show it: 35 mph in 2011, 22 mph in 2013, 19 mph in 2014. A team
picking an end in a strong wind is making a real choice.

But if you hear "they won the toss, that's an edge," you can ignore it. Watch
the last four minutes before halftime instead. That's where deferring pays off,
and it's about one point.

## Data and method

Everything here is reproducible. The [repo](https://github.com/aahmadf123/battle-of-i75)
has the code, the coin-toss table with source links, and a full methodology,
including every place the official records disagree with each other (there are
eight).

- Series results: Toledo and BGSU athletics series pages, reconciled with
  CollegeFootballData.com by majority vote.
- Coin tosses and weather: official box scores from utrockets.com and
  bgsufalcons.com.
- League data: CollegeFootballData.com games, closing lines and drives.

*I work with UT Athletics on sports analytics. This piece uses only public data
and reflects my own views, not the university's.*
