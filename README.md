# midnight

## Simulator of the [Midnight](https://en.wikipedia.org/wiki/Midnight_(game)) game.

Create players, defining their strategy

```
player1 = Player(strategy=AlwaysConservativeStrategy())
player2 = Player(strategy=AlwaysConservativeStrategy())
```

Create a game, defining the number of rounds that will be played.

```
game = Game(n_rounds=10)
```

Add players

```
game.add_player(player1)
game.add_player(player2)
```

Run simulation

```
game.play()
```

Get game satistics as a `pandas.DataFrame`

```
game.get_game_stats()
```

Get players' scores as a `pandas.DataFrame`

```
game.get_all_scores()
```