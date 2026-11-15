# Methodology

Every number in the field note is produced by `src/analyze.py` and stored in
`data/processed/results.json`. Nothing is typed in by hand.

## 1. The 90-game series

**Sources.** Three independent records:

1. Toledo Athletics opponent-history page (Toledo SID)
2. BGSU Athletics opponent-history page (BGSU SID)
3. CollegeFootballData.com `/teams/matchup` (covers 1962 onward, 64 games)

**Rule.** For each game, score and host site are decided by majority vote of the
sources that cover it. If only two sources exist and they disagree, Toledo's
value is kept, the game is marked `unresolved`, and the choice is tested in a
sensitivity check.

**What the sources disagree on** (full detail in `discrepancies.csv`):

| Season | Disagreement | Resolution |
|---|---|---|
| 1924 | Toledo page says played in Bowling Green, BGSU page says Toledo | Unresolved. Kept Bowling Green. Flipping it moves the home-team record by one game. |
| 1933 | Toledo page: 25-7. BGSU page: 26-7 (dates also differ by a day) | Unresolved. Kept 25-7. Affects only point totals. |
| 1935 | Date: Nov. 1 (Toledo) vs. Nov. 2 (BGSU) | No effect on results. |
| 1967 | Toledo page labels it "Home" but lists the site as Bowling Green | Bowling Green (BGSU page and CFBD agree). This is why Toledo's page shows a 25-19-2 home record; the reconciled figure is 24-19-2. |
| 1968 | CFBD lists Bowling Green as host | Toledo (both school pages agree). |
| 1969 | Date: Fri. Oct. 10 vs. Sat. Oct. 11 | No effect on results. |
| 1981 | BGSU page says played in Toledo | Bowling Green (Toledo page and CFBD agree). |
| 2000 | BGSU page and box-score header: 54-20. Toledo page and CFBD: 51-17 | 51-17. BGSU's own box-score scoring plays add up to 51-17. The margin is +34 either way. |

## 2. Coin tosses, 1998-2025

**Source.** The official box score for each game (Toledo's site where it has
one, BGSU's otherwise). `pull_boxscores.py` extracts the toss line word for
word. `coin_toss.csv` stores that line next to its URL so anyone can check it.

**Coding.** Toss winner and decision are read from the line. Who received each
half is read from the opening and 2nd-half kickoffs in the same box score, then
cross-checked against CFBD drive data.

**Cross-check result.** CFBD and the box scores agree on both receivers in 19
of 20 games where both exist. The exception is 2007: CFBD lists Toledo's drive
first, but the box score shows Toledo kicking off to Bowling Green. The box
score is used.

**Games that can't be coded:**

- **1998.** The line reads "BG wins toss and defers; Miami will receive." Toledo
  kicked off to open the game and Bowling Green kicked off to open the 2nd half,
  which contradicts BG deferring. The line is a template error. Receivers are
  known; the toss winner is not.
- **2000.** The box score has no play-by-play. Neither the toss nor the receivers
  can be determined.

## 3. League baseline, FBS 2014-2025

**Why.** 27 rivalry games cannot detect any realistic coin-toss effect (see 5).
The league sample can.

**Data.** CFBD regular-season games where both teams are FBS, with closing
lines and drive data.

**Definitions.**

- *1st-half receiver*: offense on the first drive of the game.
- *2nd-half receiver*: offense on the first drive of the 3rd quarter.
- *Spread*: median closing spread across every book CFBD lists.
- *Middle Eight*: points on drives that end between 4:00 left in the 2nd
  quarter and 11:00 left in the 3rd. A drive's points are booked at its end.

**Quality gates.**

- `receiver_ok` (8,310 games, used for win analysis): the first drives of Q1
  and Q3 start at 14:00 or later, and were run by different teams.
- `points_ok` (5,545 games, used for Middle Eight): `receiver_ok` and the
  drive-level points add up to the official final score for both teams. Most
  failures are one missing scoring drive in CFBD's data, usually exactly 7
  points.

**Why this works as an experiment.** A coin decides who receives the 2nd half,
and nearly every winner defers. So 2nd-half receivers should look like a random
half of all teams. They do: their average closing spread is -0.22 and they are
the home team 49.2% of the time.

**Models.**

- Raw win rate with a Wilson 95% interval.
- Logistic regression of win on the 2nd-half receiver's closing spread. The
  intercept is the effect of receiving at a pick'em, reported in percentage
  points of win probability.
- Final margin plus closing spread (points beyond the line), mean with a
  2,000-sample bootstrap interval.

**Robustness.** By season the 2nd-half receiver's win rate ranges from 46.9%
to 53.7%, with no trend. Inside the `points_ok` subset it is 51.0%. Without
the 2020 season it is 50.2%.

## 4. Series streaks

Ties are dropped and the 86 decided games are shuffled 20,000 times. Two
questions:

- Is the series streakier than chance overall? Observed 40 runs vs. 44
  expected. 22.6% of shuffles have 40 or fewer. **No.**
- How unusual are the famous streaks? A 12-game run shows up in 0.8% of
  shuffles. A 9-game run shows up in 9.8%. Bowling Green's 1955-66 run, which
  covers Doyt Perry's entire tenure as head coach, is the only genuinely
  unusual stretch.

The seed is fixed (`91`), so results reproduce exactly.

## 5. Limitations

- **27 rivalry games is too few.** The smallest effect this sample could detect
  with 80% power is about 27 percentage points. The league data says the true
  effect is near zero.
- **The toss itself is not in CFBD.** League-wide we observe who received each
  half, not who won the toss. Since about 85% of rivalry toss winners deferred,
  "2nd-half receiver" is close to "toss winner," but not identical.
- **CFBD drive data has errors.** The rivalry cross-check found 1 wrong
  receiver in 20 games. Random errors like this pull estimates toward zero, so
  a small true effect could be slightly understated.
- **Weather.** Box scores report it, and it is in `coin_toss.csv`. CFBD's free
  tier does not include weather, so it is not in the league model.
- **Pre-1998 tosses.** Not in any public digital box score.
