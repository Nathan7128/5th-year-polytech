import torch
import torch.nn as nn
import torch.nn.functional as F

from torchrl.modules import NoisyLinear
from collections import deque
import gymnasium as gym
import random
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
neurons = 128



class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = NoisyLinear(n_observations, neurons)
        self.layer2 = NoisyLinear(neurons, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        return self.layer2(x)

    def reset_noise(self):
        self.layer1.reset_noise()
        self.layer2.reset_noise()


env = gym.make("CartPole-v1", render_mode="rgb_array")
state, info = env.reset()
n_observations = len(state)
n_actions = env.action_space.n

current_model = DQN(n_observations, n_actions).to(device)
target_model  = DQN(n_observations, n_actions).to(device)
target_model.load_state_dict(current_model.state_dict())
target_model.eval()

optimizer = torch.optim.Adam(current_model.parameters(), lr=5e-4)
criterion = nn.SmoothL1Loss()

memory = deque(maxlen=10000)
batch_size = 128
discount = 0.99
TAU = 0.005
N_episodes = 1000


for episode in range(N_episodes):
    state, info = env.reset()
    state = torch.from_numpy(state).float().to(device).unsqueeze(0)

    done = False
    steps = 0

    while not done:
        action = current_model(state).argmax(dim=1).item()

        current_model.reset_noise()
        target_model.reset_noise()

        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        reward = torch.tensor([reward], device=device)

        if not done:
            next_state = torch.from_numpy(next_state).float().to(device).unsqueeze(0)
        else:
            next_state = None

        memory.append((state, action, reward, next_state))
        state = next_state
        steps += 1


        current_model.reset_noise()
        target_model.reset_noise()



        if len(memory) >= batch_size:
            batch = random.sample(memory, batch_size)
            states, actions, rewards, next_states = zip(*batch)

            states = torch.cat(states).to(device)
            actions = torch.tensor(actions, device=device).long().unsqueeze(1)
            rewards = torch.cat(rewards).to(device)

            non_final_mask = torch.tensor([s is not None for s in next_states], device=device)
            non_final_next_states = torch.cat([s for s in next_states if s is not None], dim=0)

            q_values = current_model(states).gather(1, actions).squeeze(1)

            with torch.no_grad():
                next_q_values = torch.zeros(batch_size, device=device)
                non_final_mask = torch.tensor([s is not None for s in next_states], device=device)
                if non_final_mask.any():
                    non_final_next_states = torch.cat([s for s in next_states if s is not None], dim=0)
                    next_q_values[non_final_mask] = target_model(non_final_next_states).max(dim=1).values

            targets = rewards + discount * next_q_values

            loss = criterion(q_values, targets)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_value_(current_model.parameters(), 100)
            optimizer.step()

            with torch.no_grad():
                for t, s in zip(target_model.parameters(), current_model.parameters()):
                    t.mul_(1 - TAU).add_(s * TAU)

    if episode % 20 == 0 and len(memory) >= batch_size:
        print(f"Episode {episode} | Duration: {steps} | Loss: {loss.item():.4f}")