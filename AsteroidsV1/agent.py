import torch
import random
import numpy as np
import pygame
from collections import deque
from asteroidsV1Training import AsteroidAI
from model import Linear_QNet, QTrainer
from helper import plot

#el agente es el que juega al juego y aprende
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
N_RANDOM_GAMES = 80
RANDOM_PROB = 100

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #random
        self.gamma = 0.75 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() cuando se llena la memoria
        #self.model = Linear_QNet(30, 256, 256, 5)
        self.model = Linear_QNet(15 * 5, 10, 10, 5)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game, number):
        state = game.players[number].checkRadar(game.players,game.asteroids,game.playerBullets,game.barricades)
        return state

    def remember(self, state, action, reward, next_state, gameover):
        self.memory.append((state, action, reward, next_state, gameover))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) #list of tuples
        else: 
            mini_sample = self.memory
        states, actions, rewards, next_states, gameovers = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, gameovers)

    def train_short_memory(self, state, action, reward, next_state, gameover):
        self.trainer.train_step(state, action, reward, next_state, gameover)

    def get_action(self, state):
        # random moves: tradeoff between exploration / explotation
        self.epsilon = N_RANDOM_GAMES - self.n_games
        #final_move = [0,0,0,0,0]
        final_move = [0,0,0,0,0]
        if random.randint(0, RANDOM_PROB) < self.epsilon:
            move = random.randint(0, 4)
            # move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
        


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    timeRecord = 0
    agent1 = Agent()
    agent2 = Agent()
    agent3 = Agent()
    agent4 = Agent()
    agents = [agent1, agent2, agent3, agent4]
    game = AsteroidAI()
    run = True
    n_games = 0
    #agent.model.load()
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if n_games == 500:
            run = False

        oldStates = [None,None,None,None]
        finalMoves = [None,None,None,None]
        newStates = [None,None,None,None]
        
        for i in range(0,4):

            if game.players[i].alive == True:
                #get current state
                oldStates[i] = agents[i].get_state(game,i)
                #get move
                finalMoves[i] = agents[i].get_action(oldStates[i])

        #perform move and get reward
        rewards, time, gameOvers = game.play_step(finalMoves)

        for i in range(0,4):
            if game.players[i].alive == True:
                newStates[i] = agents[i].get_state(game,i)

                #train short memory
                agents[i].train_short_memory(oldStates[i], finalMoves[i], rewards[i], newStates[i], gameOvers[i])

                #remember
                agents[i].remember(oldStates[i], finalMoves[i], rewards[i], newStates[i], gameOvers[i])

        if gameOvers[0] and gameOvers[1] and gameOvers[2] and gameOvers[3]:
            #train long memory, plot results
            game.reset()
            n_games += 1
            for i in range(0,4):
                agents[i].n_games += 1
                agents[i].train_long_memory()

            if time > timeRecord:
                timeRecord = time
                for i in range(0,4):
                    agents[i].model.save(i)

            # plot_scores.append(time)
            total_score += time
            mean_score = total_score / n_games
            # plot_mean_scores.append(mean_score)
            # plot(plot_scores,plot_mean_scores)

            print('Game ',n_games, 'Time: ', time, 'TimeRecord: ', timeRecord, 'MeanTime: ', mean_score)

    pygame.quit()

if __name__ == '__main__':
    train()