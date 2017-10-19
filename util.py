import numpy as np
from melee import enums

def get_reward(state, prev_state):
    player1_prev_stocks = get_stocks_player1(prev_state)
    player2_prev_stocks = get_stocks_player2(prev_state)
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

def piecewise(number, stick=False, shoulder=False):
    # Stick to determine if the input is the stick type
   
    # Shoulder to determine if the input is the L&R shoulder type

    # performing a shift such that
    # the shoulder range becomes (0,1)
    if shoulder or stick:
        return (number.item(0) + 1) / 2


    if number < 0:
        return 0
    else:
        return 1

def make_inputs(q_values):
    n = list()

    '''
    Input Map
    [A, B, X, Y, Start, Z, L, R, D_up, D_down, D_left, D_right, 
    Stick_X, Stick_Y, CStick_X, CStick_Y, LShoulder, RShoulder]
    '''

    for input_index, potential_input in enumerate(np.nditer(q_values, op_flags=["readwrite"])):
        # Boolean for whether the value is a control stick rather than a button
        stick = False

        # Same boolean for L&R shoulders
        shoulder = False
        if input_index >= 12 and input_index <= 15:
            stick = True
        if input_index >= 16:
            shoulder = True

        n.append(piecewise(potential_input, stick=stick, shoulder=shoulder))
    return np.asarray([n])


# Access the controller to put in the inputs
def apply_inputs(controller, input_values):
    print("herea")
    print(input_values)
    print("end apply_inputs print")
    if input_values[0] == 1:
        controller.press_button(enums.Button.BUTTON_A)
        print("A Pressed")
    if input_values[1] == 1:
        controller.press_button(enums.Button.BUTTON_B)
        print("B Pressed")
    if input_values[2] == 1:
        controller.press_button(enums.Button.BUTTON_X)
        print("X Pressed")

    # Only need one jump button
    # if input_values[3] == 1:
    #     controller.press_button(enums.Button.BUTTON_Y)
    #     print("Y Pressed")

    # Don't press the start button
    # if input_values[4] == 1:
    #     controller.press_button(enums.Button.BUTTON_START)

    # if input_values[5] == 1:
    #     controller.press_button(enums.Button.BUTTON_Z)
    # if input_values[6] != 0:
    #     controller.press_shoulder(enums.Button.BUTTON_L, input_values[16])
    # if input_values[7] != 0:
    #     controller.press_shoulder(enums.Button.BUTTON_R, input_values[17])
    
    # Don't taunt
    # Will add in BM taunting later
    # if input_values[8] == 1:
    #     controller.press_button(enums.Button.BUTTON_A)    
    # if input_values[9] == 1:
    #     controller.press_button(enums.Button.BUTTON_A)  
    # if input_values[10] == 1:
    #     controller.press_button(enums.Button.BUTTON_A)  
    # if input_values[11] == 1:
    #     controller.press_button(enums.Button.BUTTON_A) 

    if input_values[12] or input_values[13] != 0:
        controller.tilt_analog(enums.Button.BUTTON_MAIN, input_values[12], input_values[13]) 
    # controller.empty_input() 
    
    







