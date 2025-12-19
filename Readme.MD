# Teetly and Nargiz , chess bot 1.0

# How to run: 

Cd into the chess_bot directory , then run..
```shell
python chess_run.py
```

## Project files (what each file does)

### Core gameplay 
- **`chess_run.py`** – Main engine and interactive game runner. Implements:
  - baseline move-pickers (capture-preferred vs purely random) and game loops (human vs bot; bot vs bot). 
  - **Minimax** and **alpha–beta pruning** search, using a simple “immediate reward” evaluation and lightweight move ordering (checks/captures/promotions first). 
  - outcome detection (checkmate/stalemate/insufficient material/75-move rule/fivefold repetition). 

### Experiments 
- **`min_max_ab_test.py`** – Runs batches of bot-vs-bot games from the standard starting position to compare minimax vs alpha–beta at different depths. Uses multiprocessing and writes results to a CSV (columns include `minimax_color`, `alphabeta_color`, `depth_minimax`, `depth_alphabeta`, `outcome`). 

- **`min_max_ab_test_opening.py`** – Same idea as `min_max_ab_test.py`, but starts from a selected **opening FEN** (e.g., Queen’s Gambit / Sicilian Dragon / Polish Opening) and records both `outcome` and `winner`. It also flushes results immediately to disk while matches run. 

### Local test 
- **`testing.py`** – Small, fast sanity tests. Includes a helper to create a board from a given FEN (or default start) and then run quick bot-vs-bot checks. 

- **`testing_openings.py`** – Helper for testing bots from specific opening positions (uses opening FENs and runs greedy-vs-random or greedy-vs-greedy checks). 
### Results 
- **`minimax_vs_alphabeta_results*.csv`** – Output datasets produced by the experiment scripts (see `min_max_ab_test.py` and `min_max_ab_test_opening.py` for the exact columns and default output filenames). 
- **`results_table_ab_minmax.tex`**, **`minmax_ab_results.tex`** – LaTeX tables used in the written report to summarize experiment outcomes (assembled from the CSV results).


