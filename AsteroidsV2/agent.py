import torch
import random
import numpy as np
import pygame
import matplotlib.pyplot as plt
from collections import deque
from asteroidsV2Training import AsteroidAI
from model import Linear_QNet, QTrainer

#el agente es el que juega al juego y aprende y tal
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.03
N_RANDOM_GAMES = 80
RANDOM_PROB = 100

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #random
        self.gamma = 0.75 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() cuando se llena la memoria
        self.model = Linear_QNet(15 * 3, 5, 5, 5)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        state = game.players[0].checkRadar(game.asteroids,game.bullets)
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
    scoreRecord = 0
    agent = Agent()
    game = AsteroidAI()
    run = True
    n_games = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if n_games == 500:
            run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            plt.title('Training...')
            plt.xlabel('Number of games')
            plt.ylabel('Score')
            plt.plot(plot_scores)
            plt.plot(plot_mean_scores)
            plt.ylim(ymin=0)
            plt.text(len(plot_scores)-1, plot_scores[-1], str(plot_scores[-1]))
            plt.text(len(plot_mean_scores)-1, plot_mean_scores[-1], str(plot_mean_scores[-1]))
            plt.show()
            
        oldState = agent.get_state(game)
        #get move
        finalMove = agent.get_action(oldState)

        #perform move and get reward
        reward, time, gameOver, score = game.play_step(finalMove)

        newState = agent.get_state(game)

        #train short memory
        agent.train_short_memory(oldState, finalMove, reward, newState, gameOver)

        #remember
        agent.remember(oldState, finalMove, reward, newState, gameOver)

        if gameOver:
            #train long memory, plot results
            game.reset()
            n_games += 1
            agent.train_long_memory()

            if score >= scoreRecord:
                scoreRecord = score
                agent.model.save()

            if time > timeRecord:
                timeRecord = time

            print('Game ',n_games, 'Time: ', time, 'TimeRecord: ', timeRecord, 'Score: ', score)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / n_games
            plot_mean_scores.append(mean_score)
            # plot(plot_scores,plot_mean_scores)

    plt.title('Training...')
    plt.xlabel('Number of games')
    plt.ylabel('Score')
    plt.plot(plot_scores)
    plt.plot(plot_mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(plot_scores)-1, plot_scores[-1], str(plot_scores[-1]))
    plt.text(len(plot_mean_scores)-1, plot_mean_scores[-1], str(plot_mean_scores[-1]))
    plt.show()
    pygame.quit()

if __name__ == '__main__':
    train()