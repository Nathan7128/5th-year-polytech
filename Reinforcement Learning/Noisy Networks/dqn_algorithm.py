import torch
import torch.nn as nn
import torch.nn.functional as F

from torchrl.modules import NoisyLinear
from collections import deque
import gymnasium as gym
import random
import matplotlib.pyplot as plt
from IPython import display
plt.ion()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
neurons = 128


# ---------------------
#  DQN MODEL
# ---------------------
class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = NoisyLinear(n_observations, neurons)
        self.layer2 = NoisyLinear(neurons, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        return self.layer2(x)

    def reset_noise(self):
        # IMPORTANT for exploration
        self.layer1.reset_noise()
        self.layer2.reset_noise()


episode_durations = []
losses = []

def plot_durations(show_result=False):
    plt.figure(1)
    durations_t = torch.tensor(episode_durations, dtype=torch.float)
    if show_result:
        plt.title("Result")
    else:
        plt.clf()
        plt.title("Training...")

    plt.xlabel("Episode")
    plt.ylabel("Duration")
    plt.plot(durations_t.numpy())

    if len(durations_t) >= 50:
        means = durations_t.unfold(0, 50, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(49), means))
        plt.plot(means.numpy(), linestyle='--')

    plt.pause(0.001)
    display.display(plt.gcf())
    display.clear_output(wait=True)


# ---------------------
# ENV INIT
# ---------------------
env = gym.make("CartPole-v1", render_mode="rgb_array")
state, info = env.reset()
n_observations = len(state)
n_actions = env.action_space.n

current_model = DQN(n_observations, n_actions).to(device)
target_model  = DQN(n_observations, n_actions).to(device)
target_model.load_state_dict(current_model.state_dict())
target_model.eval()

optimizer = torch.optim.AdamW(current_model.parameters(), lr=5e-4)
criterion = nn.SmoothL1Loss()

memory = deque(maxlen=10000)
batch_size = 128
discount = 0.99
TAU = 0.005
target_update_steps = 10
N_episodes = 1000


# ---------------------
# TRAINING LOOP
# ---------------------
for episode in range(N_episodes):
    state, info = env.reset()
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)

    done = False
    t = 0

    while not done:
        # -------------------
        # ACTION SELECTION
        # -------------------
        with torch.no_grad():
            q_values = current_model(state)
            action = torch.argmax(q_values, dim=1).item()

        # DEBUG → Vérifie l'exploration
        # print("Action =", action)

        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        # Stabiliser reward
        reward = torch.tensor([reward / 10.0], device=device)

        if not done:
            next_state = torch.tensor(next_state, dtype=torch.float32, device=device).unsqueeze(0)
        else:
            next_state = None

        memory.append((state, action, reward, next_state))
        state = next_state
        t += 1

        # Reset du bruit → EXPLORATION CONTINUE
        current_model.reset_noise()
        target_model.reset_noise()

        # -------------------
        # TRAINING DQN
        # -------------------
        if len(memory) >= batch_size:
            batch = random.sample(memory, batch_size)
            states, actions, rewards, next_states = zip(*batch)

            states = torch.cat(states).to(device)
            actions = torch.tensor(actions, device=device).long().unsqueeze(1)
            rewards = torch.cat(rewards).to(device)

            # Masque des états finaux
            non_final_mask = torch.tensor([s is not None for s in next_states], device=device)
            non_final_next_states = torch.cat([s for s in next_states if s is not None], dim=0)

            q_values = current_model(states).gather(1, actions).squeeze(1)

            # ----- DOUBLE DQN -----
            with torch.no_grad():
                next_actions = current_model(non_final_next_states).argmax(1).unsqueeze(1)
                next_q_values = torch.zeros(batch_size, device=device)
                next_q_values[non_final_mask] = target_model(non_final_next_states) \
                                                .gather(1, next_actions).squeeze(1)

            targets = rewards + discount * next_q_values

            loss = criterion(q_values, targets)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_value_(current_model.parameters(), 100)
            optimizer.step()
            losses.append(loss.item())

            # Soft update
            for target_param, param in zip(target_model.parameters(), current_model.parameters()):
                target_param.data.copy_(param.data * TAU + target_param.data * (1.0 - TAU))

    episode_durations.append(t)
    plot_durations()

print("Training Complete")
plot_durations(show_result=True)
plt.ioff()
plt.show()