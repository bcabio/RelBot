import sys

already_dead = {1: False, 2: False}

# These are just big numbers to keep track of the player stocks
# during melee time mode which doesn't offer stocks
p1_stocks = 9223372036854775807
p2_stocks = 9223372036854775807
# def get_reward(state, prev_state):

def get_stocks(gamestate, player):

    return gamestate[3 + (player - 1)*16]

def is_dying(gamestate, player):
    # Check if player is dying

    # Return gamestate action for the player
    return gamestate[5 + (player - 1)*16] <= 0x0A

def get_damage(gamestate, player):
    return gamestate[2 + (player - 1)*16]

def get_reward(gamestate, prev_gamestate, player_port=1, ai_port=2, damage_ratio=0.01):
    # Check if player is dying, but make sure the 
    # reward only occurs on the first frame of death

    stock_reward = 0

    if is_dying(gamestate, ai_port) and already_dead[ai_port] is False:
        stock_reward = -1
        print('I died ',)
        already_dead[ai_port] = True
    if is_dying(gamestate, player_port) and already_dead[player_port] is False:
        stock_reward = 1
        print('cpu died',)
        already_dead[player_port] = True

    if not is_dying(gamestate, ai_port):
        already_dead[ai_port] = False

    if not is_dying(gamestate,player_port):
        already_dead[player_port] = False

    prev_dmg_1 = get_damage(prev_gamestate, 1)
    prev_dmg_2 = get_damage(prev_gamestate, 2)
    curr_dmg_1 = get_damage(gamestate, 1)
    curr_dmg_2 = get_damage(gamestate, 2)

    # From player 2 perspective, if player two takes more damage, then the losses are higher
    losses = (curr_dmg_1 - prev_dmg_1) - (curr_dmg_2 - prev_dmg_2) 

    if stock_reward == 0:
        return damage_ratio * losses

    return stock_reward




