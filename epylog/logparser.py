from .model import Game, Player, PlayerGame, connection


current_game = Game(map_name=None, termination=None)
player_game_list = {}  # (pseudo, player_game)
player_id_matching = {}  # (id ingame du joueur, pseudo)
player_id_matching['1022'] = 'world'


with open('logTest.log', 'r') as f:
    for line in f:
        splited_line = line.split(' ')
        if splited_line[0] == 'Kill:':
            id_killer = splited_line[1]
            id_killed = splited_line[2]
            id_weapon = splited_line[3][0:-1]
            if id_killer != id_killed and id_killer != '1022':
                player_game_list[player_id_matching[id_killer]].kill += 1
            player_game_list[player_id_matching[id_killed]].death += 1
        elif splited_line[0] == 'Item:':
            id_looter = splited_line[1]
            name_item = splited_line[2][0:-1]
            name_player = player_id_matching[id_looter]
        elif splited_line[0] in ('Rcon', 'InitGame:'):
            connection.rollback()
            player_game_list.clear()
            if splited_line[0] == 'Rcon':
                name = splited_line[4][0:-1]
            else:
                split_list = line.split('\\')
                name = split_list[split_list.index('mapname')+1]
            current_game = Game(map_name=name, termination=None)
            connection.add(current_game)
        elif splited_line[0] == 'Exit:':
            end = splited_line[1]
            current_game.termination = end
            for pseudo, player_game in player_game_list.items():
                connection.add(player_game)
            connection.commit()
            player_game_list.clear()
            player_id_matching['1022'] = 'world'
        elif splited_line[0] == 'ClientUserinfoChanged:':
            ingame_id = splited_line[1]
            name_player = line.split('\\')[1]
            player_id_matching[ingame_id] = name_player
            player = connection.query(Player).filter(Player.pseudo == name_player).first()
            if player is None:
                player = Player(pseudo=name_player)
                connection.add(player)
            player_game = connection.query(PlayerGame).filter(PlayerGame.game == current_game,
                                                 PlayerGame.player == player).first()
            if player_game is None:
                player_game = PlayerGame(kill=0, death=0)
                player_game.player = player
                player_game.game = current_game
                player_game_list[player.pseudo] = player_game
        elif splited_line[0] == 'ClientDisconnect:':
            del player_id_matching[splited_line[1][0:-1]]