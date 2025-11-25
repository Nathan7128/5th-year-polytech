# ---------------------------------------------------------------------------------------------------------------------------------------------------
# LIBRARIES
# ---------------------------------------------------------------------------------------------------------------------------------------------------

import torch
from torchrl.modules import NoisyLinear
import torch.nn as nn
import torch.nn.functional as F

from collections import deque

import gymnasium as gym

import random

# ---------------------------------------------------------------------------------------------------------------------------------------------------
# VARIABLES
# ---------------------------------------------------------------------------------------------------------------------------------------------------

memory_size = 10000
n_episodes = 400

episodes_duration = []

device = torch.device("cuda" if torch.cuda.is_available() else"cpu")

neurons = 128
learning_rate = 0.001
batch_size = 64

discount_factor = 0.99
tau = 0.005

# ---------------------------------------------------------------------------------------------------------------------------------------------------
# CLASSES
# ---------------------------------------------------------------------------------------------------------------------------------------------------

class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = NoisyLinear(n_observations, neurons)
        self.layer2 = NoisyLinear(neurons, neurons)
        self.layer3 = NoisyLinear(neurons, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)

    def reset_noise(self):
        self.layer1.reset_noise()
        self.layer2.reset_noise()
        self.layer3.reset_noise()

    
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# RL ENVIRONMENT
# ---------------------------------------------------------------------------------------------------------------------------------------------------

env = gym.make("CartPole-v1", render_mode="rgb_array")
state, info = env.reset()
n_observations = len(state)
n_actions = env.action_space.n

memory = deque(maxlen=memory_size)

# ---------------------------------------------------------------------------------------------------------------------------------------------------
# DQN MODELS
# ---------------------------------------------------------------------------------------------------------------------------------------------------

current_model = DQN(n_observations, n_actions).to(device)
target_model  = DQN(n_observations, n_actions).to(device)
target_model.load_state_dict(current_model.state_dict())

optimizer = torch.optim.Adam(current_model.parameters(), lr=learning_rate)
criterion = nn.MSELoss()


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# AGENT TRAINING
# ---------------------------------------------------------------------------------------------------------------------------------------------------

for episode in range(n_episodes):
    state, info = env.reset()
    state = torch.tensor(state, dtype=torch.float32).to(device).unsqueeze(0)

    done = False
    steps = 0

    current_model.reset_noise()
    target_model.reset_noise()

    while not done:
        current_model.reset_noise()
        q_values = current_model(state)
        action = q_values.argmax(dim=1).unsqueeze(0)

        next_state, reward, terminated, truncated, _ = env.step(action.item())
        done = terminated or truncated

        reward = torch.tensor([reward], dtype=torch.float32).to(device).unsqueeze(0)

        if not done:
            next_state = torch.tensor(next_state, dtype=torch.float32).to(device).unsqueeze(0)
        else:
            next_state = None

        memory.append((state, action, reward, next_state))
        state = next_state
        steps += 1

        if len(memory) >= batch_size:
            batch = random.sample(memory, batch_size)
            states, actions, rewards, next_states = zip(*batch)
            states = torch.cat(states).to(device)
            actions = torch.cat(actions).to(device)
            rewards = torch.cat(rewards).to(device)

            q_values = current_model(states).gather(1, actions).squeeze(1)

            non_final_mask = torch.tensor([s is not None for s in next_states], device=device, dtype=torch.bool)
            non_final_next_states = torch.cat([s for s in next_states if s is not None])
            
            next_state_values = torch.zeros(batch_size, device=device)
            with torch.no_grad():
                next_state_values[non_final_mask] = target_model(non_final_next_states).max(1).values
            expected_state_action_values = (next_state_values * discount_factor) + rewards
            loss = criterion(q_values, expected_state_action_values)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_value_(current_model.parameters(), 5)
            optimizer.step()
    
    episodes_duration.append(steps)

    for target_param, param in zip(target_model.parameters(), current_model.parameters()):
        target_param.data.copy_(tau * param.data + (1 - tau) * target_param.data)

    if episode % 20 == 0 and len(memory) >= batch_size:
        print(f"Episode {episode} | Duration: {steps} | Loss: {loss.item():.4f}")