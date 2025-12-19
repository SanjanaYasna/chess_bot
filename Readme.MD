# Teetly and Nargiz , chess bot 1.0

# How to run: 

Cd into the chess_bot directory , then run..
```shell
python chess_run.py
```

## Project files (what each file does)

### Core gameplay 
- **`chess_run.py`** – Main engine and interactive game runner. Implements:
  - baseline move-pickers (capture-preferred vs purely random) and game loops (human vs bot; bot vs bot). :contentReference[oaicite:0]{index=0}
  - **Minimax** and **alpha–beta pruning** search, using a simple “immediate reward” evaluation and lightweight move ordering (checks/captures/promotions first). :contentReference[oaicite:1]{index=1} :contentReference[oaicite:2]{index=2}
  - outcome detection (checkmate/stalemate/insufficient material/75-move rule/fivefold repetition). :contentReference[oaicite:3]{index=3}

### Experiments 
- **`min_max_ab_test.py`** – Runs batches of bot-vs-bot games from the standard starting position to compare minimax vs alpha–beta at different depths. Uses multiprocessing and writes results to a CSV (columns include `minimax_color`, `alphabeta_color`, `depth_minimax`, `depth_alphabeta`, `outcome`). :contentReference[oaicite:4]{index=4}

- **`min_max_ab_test_opening.py`** – Same idea as `min_max_ab_test.py`, but starts from a selected **opening FEN** (e.g., Queen’s Gambit / Sicilian Dragon / Polish Opening) and records both `outcome` and `winner`. It also flushes results immediately to disk while matches run. :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}

### Local test 
- **`testing.py`** – Small, fast sanity tests. Includes a helper to create a board from a given FEN (or default start) and then run quick bot-vs-bot checks. :contentReference[oaicite:7]{index=7}

- **`testing_openings.py`** – Helper for testing bots from specific opening positions (uses opening FENs and runs greedy-vs-random or greedy-vs-greedy checks). :contentReference[oaicite:8]{index=8} :contentReference[oaicite:9]{index=9}

### Results 
- **`minimax_vs_alphabeta_results*.csv`** – Output datasets produced by the experiment scripts (see `min_max_ab_test.py` and `min_max_ab_test_opening.py` for the exact columns and default output filenames). :contentReference[oaicite:10]{index=10} :contentReference[oaicite:11]{index=11}
- **`results_table_ab_minmax.tex`**, **`minmax_ab_results.tex`** – LaTeX tables used in the written report to summarize experiment outcomes (generated/assembled from the CSV results).
- **`minmax_ab.txt`** – Run log captured from a batch/cluster execution (e.g., SLURM output / time-limit cancellation message). :contentReference[oaicite:12]{index=12}

