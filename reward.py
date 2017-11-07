

already_dead = {1: False, 2: False, 3: False, 4: False}


# def get_reward(state, prev_state):

def is_dying(gamestate, player):
    # Check if player is dying

    # Return gamestate action for the player
    return gamestate[5 + (player - 1)*16] <= 0x0A

def feed_deaths(gamestate):
    # Check if player is dying, but make sure the 
    # reward only occurs on the first frame of death

    
    
    for player in already_dead:
        if is_dying(gamestate, player):
            already_dead[player] = True
        else:
            already_dead[player] = False





