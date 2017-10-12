import numpy as np

def get_reward(state, player1_prev_stocks, player2_prev_stocks):
    player1_stocks = get_stocks_player1(state)
    player2_stocks = get_stocks_player2(state)

    if player1_stocks < player1_prev_stocks:
        return 10
    elif player2_stocks < player2_prev_stocks:
        return -10
    else:
        return -1

def get_stocks_player2(state):
    return state[19]

def get_stocks_player1(state):
    return state[3]

def piecewise(number, stick=False):
    # Stick to determine if the input is the stick type
    if not stick:
        if number < 0:
            return 0
        else:
            return 1
    return number

def make_inputs(q_values):
    n = list()
    '''
    Input Map
    [A, B, X, Y, Start, Z, L, R, D_up, D_down, D_left, D_right, 
            Stick_X, Stick_Y, CStick_X, CStick_Y, LShoulder, RShoulder]
    '''
    # print(type(q_values))
    print("lmao")
    # for i,x in enumerate(np.nditer(qval, op_flags=["readwrite"])):
    #     print(x)
    #     print(type(x))

    for input_index, potential_input in enumerate(np.nditer(q_values, op_flags=["readwrite"])):
        # Boolean for whether the value is a control stick rather than a button
        stick = False
        if input_index >= 12:
            stick = True
        n.append(piecewise(potential_input, stick=stick))
    return n
