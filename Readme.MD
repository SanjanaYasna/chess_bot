# Teetly and Nargiz , chess bot 1.0

# How to run: 

Cd into the chess_bot directory , then run..
```shell
python chess_run.py
```

# Game flow:

The bot starts by asking for the player's choice for whether the bot plays black or write. Enter w for white, b for black. 
Then, you can feed a starting FEN position, or hit enter for the default starting position. 

Enter your move in FEN and go back and forth with the bot.

After each move, the program prints the overall FEN position. The bot picks a random capture move from all legal moves, else it picks a random legal move if no capture moves remain.
The program ends in the case of a draw or one side winning. 

# Testing/Simulating Games Between Bots:

testing.py contains two tests for two bots playing against each other.

test_both_greedy_bots() tests two bots that both prioritize capture moves against each other. As you'd imagine, there is a very high chance they run into a stalemate due to insufficient material, and we assert that this is the outcome. Example outcome in examples/two_greedy_bots.txt

test_greedy_random_bot() has one bot prioritize capture (we call greedy), the other select any legal move. This one has a wider range of likely outcome, but usually the bot that captures then checkmates. Example outcome where first game black is greedy, next game white is greedy is in examples/one_greedy_other_random_bots.txt

