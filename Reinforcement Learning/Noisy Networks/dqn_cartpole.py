# ---------------------------------------------------------------------------------------------------------------------------------------------------
# LIBRARIES
# ---------------------------------------------------------------------------------------------------------------------------------------------------

import torch
from torchrl.modules import NoisyLinear
import torch.nn as nn
import torch.nn.functional as F

from collections import deque
import random
import math

import gymnasium as gym

import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# VARIABLES
# ---------------------------------------------------------------------------------------------------------------------------------------------------

memory_size = 10000
n_episodes = 500

episodes_duration = []

device = torch.device("cuda" if torch.cuda.is_available() else"cpu")

neurons = 128
learning_rate = 3e-4
batch_size = 128

eps_start = 0.9
eps_end = 0.01
eps_decay = 2500
discount_factor = 0.99
tau = 0.005


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# CLASSES
# ---------------------------------------------------------------------------------------------------------------------------------------------------

class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, neurons)
        self.layer2 = nn.Linear(neurons, neurons)
        self.layer3 = nn.Linear(neurons, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)

    
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
# INITIALIZE GRAPHIC
# ---------------------------------------------------------------------------------------------------------------------------------------------------

plt.ion()  # Mode interactif
fig, ax = plt.subplots(figsize=(12, 6))
line, = ax.plot([], [], label="Durée des épisodes")
ax.set_xlim(0, n_episodes)
ax.set_ylim(0, 500)  # Ajuste selon CartPole-v1
ax.set_xlabel("Épisode")
ax.set_ylabel("Durée (steps)")
ax.set_title("Évolution de la durée des épisodes")
ax.legend()
ax.grid(True)


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# AGENT TRAINING
# ---------------------------------------------------------------------------------------------------------------------------------------------------

for episode in range(n_episodes):
    state, info = env.reset()
    state = torch.tensor(state, dtype=torch.float32).to(device).unsqueeze(0)

    done = False
    steps = 0

    while not done:
        sample = random.random()

        eps_threshold = eps_end + (eps_start - eps_end) * math.exp(-1. * steps / eps_decay)

        if sample <= eps_threshold:
            with torch.no_grad():
                q_values = current_model(state)
                action = q_values.argmax(dim=1).unsqueeze(0)
        else:
            action = torch.tensor([[env.action_space.sample()]]).to(device)

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
            torch.nn.utils.clip_grad_value_(current_model.parameters(), 200)
            optimizer.step()

            for target_param, param in zip(target_model.parameters(), current_model.parameters()):
                target_param.data.copy_(tau * param.data + (1 - tau) * target_param.data)

    episodes_duration.append(steps)

    line.set_data(range(len(episodes_duration)), episodes_duration)
    ax.relim()
    ax.autoscale_view()
    plt.pause(0.01)  # Pause courte pour actualiser le plot

plt.ioff()
plt.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# ADDITIONAL ANALYSIS
# ---------------------------------------------------------------------------------------------------------------------------------------------------


avg_duration = 0
ep_400_duration = 0
for episode in episodes_duration:
    avg_duration += episode
    if episode >= 400:
        ep_400_duration += 1

avg_duration /= len(episodes_duration)
ep_400_duration /= len(episodes_duration)

print("Durée moyenne des épisodes : ", avg_duration)
print(f"{ep_400_duration:.0%} des épisodes durent plus de 400 étapes")