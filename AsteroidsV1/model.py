import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as f
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden1_size, hidden2_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden1_size)
        self.linear2 = nn.Linear(hidden1_size, hidden2_size)
        self.linear3 = nn.Linear(hidden2_size, output_size)

    def forward(self, x):
        x = f.relu(self.linear1(x))
        x = self.linear2(x)
        x = self.linear3(x)
        return x

    def save(self, number):
        file_name='model' + str(number) + '.pth'
        model_folder_path = './AsteroidsV1/modelsV1'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    def load(self, number):
        file_name='model' + str(number) + '.pth'
        model_folder_path = './AsteroidsV1/modelsV1'
        file_name = os.path.join(model_folder_path, file_name)
        torch.load(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.RMSprop(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, gameover):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1: #only 1 dim
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            gameover = (gameover, )
        
        # 1: predicted Q values with current state
        pred = self.model(state)
        target = pred.clone()

        for index in range(len(gameover)):
            Q_new = reward[index]
            if not gameover[index]:
                Q_new = reward[index] + self.gamma * torch.max(self.model(next_state[index]))

            target[index][torch.argmax(action).item()] = Q_new

        # 2: predicted Q values with new state
        # 3: r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        # 4: loss = RMSE(Q, Q_new)
        self.optimizer.zero_grad() #empty gradiants

        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()