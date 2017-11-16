#!/usr/bin/python3
import melee
import argparse
import signal
import sys
import tensorflow as tf
import random
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop
import numpy as np

from util import *
from reward import *

import globals

def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
         raise argparse.ArgumentTypeError("%s is an invalid controller port. \
         Must be 1, 2, 3, or 4." % value)
    return ivalue

chain = None

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port your AI will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port the opponent will play on',
                    default=1)
parser.add_argument('--live', '-l',
                    help='The opponent is playing live with a GCN Adapter',
                    default=True)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')
parser.add_argument('--difficulty', '-i', type=int,
                    help='Manually specify difficulty level of SmashBot')
parser.add_argument('--nodolphin', '-n', action='store_true',
                    help='Don\'t run dolphin, (it is already running))')

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()

#Options here are:
#   "Standard" input is what dolphin calls the type of input that we use
#       for named pipe (bot) input
#   GCN_ADAPTER will use your WiiU adapter for live human-controlled play
#   UNPLUGGED is pretty obvious what it means
opponent_type = melee.enums.ControllerType.UNPLUGGED
if args.live:
    opponent_type = melee.enums.ControllerType.GCN_ADAPTER

#Create our Dolphin object. This will be the primary object that we will interface with
dolphin = melee.dolphin.Dolphin(ai_port=args.port, opponent_port=args.opponent,
    opponent_type=opponent_type, logger=log)

#initialize our global objects
globals.init(dolphin, args.port, args.opponent)

gamestate = globals.gamestate
controller = globals.controller

def signal_handler(signal, frame):
    dolphin.terminate()
    if args.debug:
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Run dolphin and render the output
if not args.nodolphin:
    dolphin.run(render=True)

#Plug our controller in
#   Due to how named pipes work, this has to come AFTER running dolphin
#   NOTE: If you're loading a movie file, don't connect the controller,
#   dolphin will hang waiting for input and never receive it
controller.connect()

# strategy = Bait()

supportedcharacters = [melee.enums.Character.PEACH, melee.enums.Character.CPTFALCON, melee.enums.Character.FALCO, \
    melee.enums.Character.FOX, melee.enums.Character.SAMUS, melee.enums.Character.ZELDA, melee.enums.Character.SHEIK, \
    melee.enums.Character.PIKACHU, melee.enums.Character.JIGGLYPUFF, melee.enums.Character.MARTH]

### Tensorflow ###

# tf.reset_default_graph()

# input_neurons

input_size = 32
output_size = 18


# hidden_weights = np.random.uniform(size=(input_size, hidden_size))
# output_weights = np.random.uniform(size=(hidden_size, output_size))


model = Sequential()

try:
    model = load_model('melee_model.h5')
except:

# Initialize input layer with tanh activation
    model.add(Dense(100, kernel_initializer='lecun_uniform', input_shape=(input_size,)))
    model.add(Activation('tanh'))

    # Initialize first hidden layer with tanh activitation
    model.add(Dense(100, kernel_initializer='lecun_uniform'))
    model.add(Activation('tanh'))

    # Initialize second hidden layer with tanh activitation
    model.add(Dense(100, kernel_initializer='lecun_uniform'))
    model.add(Activation('tanh'))

    # Initialize output layer with linear activitation for real-valued outputs
    model.add(Dense(output_size, kernel_initializer='lecun_uniform'))
    model.add(Activation('sigmoid'))

    rms = RMSprop()
    model.compile(loss='mse', optimizer=rms)

epsilon = 0.05
gamma = 0.9 
previous_gamestate = [0]*32
frame_counter = 100000
#Main loop
while True:
    try:
    #"step" to the next frame
    # for x in gamestate:
    #     print(x)
    # print ('-----')
        previous_gamestate = gamestate.player[1].tolist() + gamestate.player[2].tolist()
        # print(previous_gamestate)

        if gamestate.menu_state != melee.enums.Menu.IN_GAME:
            gamestate.step()
        # print()
        #What menu are we in?
        if gamestate.menu_state == melee.enums.Menu.IN_GAME:
            #The strategy "step" will cascade all the way down the objective hierarchy

            ##### RL ARCHITECTURE HERE #####


            qval = model.predict(np.asarray(previous_gamestate).reshape(1, 32), batch_size=1)
            # print(qval)
           

            if random.random() < epsilon:
                action = make_inputs(np.random.rand(1, 18))
            #     # print('random')
            else:
                action = make_inputs(qval)

            # print(action)
            # print('here')
            # print("-----")
            # print(action)
            # print(action[0])
            # print("-----")

            # if frame_counter <= 0:
            #     controller.press_button(melee.enums.Button.BUTTON_B)
            #     frame_counter = 10
            # else:
            #     # print("hi")
            #     controller.release_button(melee.enums.Button.BUTTON_B)

            # frame_counter -= 1

            apply_inputs(controller, action[0])
            gamestate.step()
        
            current_gamestate = gamestate.player[1].tolist() + gamestate.player[2].tolist()
            reward = get_reward(current_gamestate, previous_gamestate, player_port=1, ai_port=2)
            
         

            # print(reward)
            y = np.zeros((1, 18))
            y[:] = qval[:]
            if reward != 0:
                print("reward: " + str(reward))
                update = [reward + gamma * val for val in y[0]]
            else:
                update = [reward]*18

            # print(update)

            y[0] = update

            model.fit(np.asarray(gamestate.player[1].tolist() + gamestate.player[2].tolist()).reshape(1, 32), np.asarray(y), batch_size=1, nb_epoch=1, verbose=0)

            frame_counter -= 1            

            if frame_counter == 0:
                model.save('melee_model.h5')
                print("====== Model saved ======")


            '''
            RL Notes:

            Input: Game state of the players

            Output: Controller input

            Reward: Taking a stock

            Penalty: Losing a stock
            '''
            # melee.techskill.multishine(ai_state=globals.smashbot_state, controller=controller)

        #If we're at the character select screen, choose our character
        elif gamestate.menu_state == melee.enums.Menu.CHARACTER_SELECT:
            melee.menuhelper.choosecharacter(character=melee.enums.Character.MARTH,
                gamestate=gamestate, controller=controller, swag=False, start=False)
        #If we're at the postgame scores screen, spam START
        elif gamestate.menu_state == melee.enums.Menu.POSTGAME_SCORES:
            melee.menuhelper.skippostgame(controller=controller)
        #If we're at the stage select screen, choose a stage
        elif gamestate.menu_state == melee.enums.Menu.STAGE_SELECT:
            melee.menuhelper.choosestage(stage=melee.enums.Stage.FINAL_DESTINATION,
                gamestate=gamestate, controller=controller)
        #Flush any button presses queued up
        controller.flush()

        if log:
            log.log("Notes", "State: " + str(gamestate.menu_state), concat=True)
            log.logframe(gamestate)
            log.writeframe()
    except KeyboardInterrupt:
        break
