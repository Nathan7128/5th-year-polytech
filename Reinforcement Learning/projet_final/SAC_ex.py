# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 14:43:09 2025

@author: julien.hautot
"""

# https://medium.com/data-science/soft-actor-critic-demystified-b8427df61665


import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Normal
from collections import deque, namedtuple
import random
import math
import os

# -------------------------
# Hyperparamètres (à adapter pour TP)
# -------------------------
ENV_NAME = "Hopper-v5"
SEED = 42
MAX_STEPS = 1000000
START_STEPS = 5000
UPDATE_AFTER = 1000
UPDATE_EVERY = 1
BATCH_SIZE = 256
GAMMA = 0.99
TAU = 0.005        
POLICY_LR = 3e-4
Q_LR = 1e-3
ALPHA_LR = 1e-3
HIDDEN = 256
REPLAY_SIZE = int(1e6)
AUTOMATIC_ENTROPY_TUNING = True

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", DEVICE)

# -------------------------
# Utils : replay buffer
# -------------------------
Transition = namedtuple("Transition", ("s", "a", "r", "s2", "done"))

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, *args):
        self.buffer.append(Transition(*args))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        return Transition(*zip(*batch))

    def __len__(self):
        return len(self.buffer)

# -------------------------
# Networks
# -------------------------
def weight_init(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        nn.init.zeros_(m.bias)

class MLP(nn.Module):
    def __init__(self, input_dim, output_dim, hidden=HIDDEN, activation=nn.ReLU):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden, device=DEVICE),
            activation(),
            nn.Linear(hidden, hidden, device=DEVICE),
            activation(),
            nn.Linear(hidden, output_dim, device=DEVICE)
        )
        self.net.apply(weight_init)

    def forward(self, x):
        return self.net(x)

# Critic (Q network) : prend state et action
class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = MLP(input_dim=state_dim+action_dim, output_dim=1, hidden=HIDDEN, activation=nn.ReLU)
    def forward(self, s, a):
        x = torch.cat([s, a], 1)
        return self.net(x)

# Policy : retourne action sampleable et log_prob (avec correction tanh)
LOG_STD_MIN = -20
LOG_STD_MAX = 2

class GaussianPolicy(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.shared = MLP(input_dim=state_dim, output_dim=2*action_dim, hidden=HIDDEN, activation=nn.ReLU)  
        self.action_dim = action_dim

    def forward(self, s):
        x = self.shared(s)
        mu, log_std = x[:, :self.action_dim], x[:, self.action_dim:]
        log_std = torch.tanh(log_std)
        # scale log_std to sensible range
        log_std = LOG_STD_MIN + 0.5 * (LOG_STD_MAX - LOG_STD_MIN) * (log_std + 1)
        std = log_std.exp()
        return mu, std

    def sample(self, s):
        mu, std = self.forward(s)
        dist = Normal(mu, std)
        z = dist.sample()
        action = torch.tanh(mu + std*z)
        
        log_prob = dist.log_prob(z) - torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(dim=-1, keepdim=True)
        return action, log_prob, torch.tanh(mu)  



# -------------------------
# Agent SAC
# -------------------------
class SACAgent:
    def __init__(self, env):
        self.env = env
        self.state_dim = env.observation_space.shape[0]
        self.action_dim = env.action_space.shape[0]
        self.act_limit = float(env.action_space.high[0])

        # networks
        self.policy = GaussianPolicy(state_dim=self.state_dim, action_dim=self.action_dim)
        self.q1 = QNetwork(state_dim=self.state_dim, action_dim=self.action_dim)
        self.q2 = QNetwork(state_dim=self.state_dim, action_dim=self.action_dim)
        self.q1_target = QNetwork(state_dim=self.state_dim, action_dim=self.action_dim)
        self.q2_target = QNetwork(state_dim=self.state_dim, action_dim=self.action_dim)

        # copy params to targets
        self.q1_target.load_state_dict(self.q1.state_dict())
        self.q2_target.load_state_dict(self.q2.state_dict())

        # optimizers
        self.policy_opt = optim.Adam(self.policy.parameters(), lr=POLICY_LR)
        self.q1_opt = optim.Adam(self.q1.parameters(), lr=Q_LR)
        self.q2_opt = optim.Adam(self.q2.parameters(), lr=Q_LR)

        # automatic entropy tuning
        if AUTOMATIC_ENTROPY_TUNING:
            # target_entropy = -|A|
            self.target_entropy = -self.action_dim
            # log alpha as parameter
            self.log_alpha = torch.tensor(0.0, requires_grad=True, device=DEVICE)
            self.alpha_opt = optim.Adam([self.log_alpha], lr=ALPHA_LR)
        else:
            self.alpha = 0.2

    def select_action(self, state, evaluate=False):
        s = torch.FloatTensor(state).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            if evaluate:
                _, _, mu = self.policy.sample(s)
                action = mu
                logp = None
            else:
                a, logp, _ = self.policy.sample(s)
                action = a
        action = action.cpu().numpy().squeeze(0)
        return action

    def update(self, replay_buffer, batch_size):
        
        transitions = replay_buffer.sample(batch_size)
        s = torch.FloatTensor(np.array(transitions.s)).to(DEVICE)
        a = torch.FloatTensor(np.array(transitions.a)).to(DEVICE)
        r = torch.FloatTensor(np.array(transitions.r)).to(DEVICE).unsqueeze(-1)
        s2 = torch.FloatTensor(np.array(transitions.s2)).to(DEVICE)
        # Ici, 'd' contient maintenant notre masque (0 si mort, 1 sinon)
        mask = torch.FloatTensor(np.array(transitions.done)).to(DEVICE).unsqueeze(-1)
        
        # --- compute target Q value ---
        with torch.no_grad():
            a2, logp_a2, _ = self.policy.sample(s2)
            q1_t = self.q1_target(s2, a2)
            q2_t = self.q2_target(s2, a2)
            q_target_min = torch.min(q1_t, q2_t)
            if AUTOMATIC_ENTROPY_TUNING:
                alpha = self.log_alpha.exp()
            else:
                alpha = self.alpha
            # target y = r + gamma*(min_q - alpha * logp_a2)
            # On multiplie le futur par le masque !
            # y = r + GAMMA * mask * (Valeur Future)
            next_q_value = q_target_min - alpha * logp_a2
            y = r + GAMMA * mask * next_q_value

        # --- Q losses ---
        q1_pred = self.q1(s, a)
        q2_pred = self.q2(s, a)
        q1_loss = nn.MSELoss()(q1_pred, y)
        q2_loss = nn.MSELoss()(q2_pred, y)

        self.q1_opt.zero_grad()
        q1_loss.backward()
        self.q1_opt.step()

        self.q2_opt.zero_grad()
        q2_loss.backward()
        self.q2_opt.step()

        # --- Policy loss ---
        a_new, logp_new, _ = self.policy.sample(s)
        q1_new = self.q1(s, a_new)
        q2_new = self.q2(s, a_new)
        q_new_min = torch.min(q1_new, q2_new)

        if AUTOMATIC_ENTROPY_TUNING:
            alpha = self.log_alpha.exp()
        else:
            alpha = self.alpha

        policy_loss = (alpha*logp_new - q_new_min).mean()

        self.policy_opt.zero_grad()
        policy_loss.backward()
        self.policy_opt.step()

        # --- entropy (alpha) tuning ---
        if AUTOMATIC_ENTROPY_TUNING:
            alpha_loss = (-self.log_alpha * (logp_new + self.target_entropy).detach()).mean()
            self.alpha_opt.zero_grad()
            alpha_loss.backward()
            self.alpha_opt.step()
            alpha = self.log_alpha.exp()
        else:
            alpha = self.alpha

        # --- soft update targets ---
        for param, target_param in zip(self.q1.parameters(), self.q1_target.parameters()):
            target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)
        for param, target_param in zip(self.q2.parameters(), self.q2_target.parameters()):
            target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)

        
        return {
            "q1_loss": q1_loss.item(),
            "q2_loss": q2_loss.item(),
            "policy_loss": policy_loss.item(),
            "alpha": alpha if not isinstance(alpha, torch.Tensor) else alpha.item()
        }



env = gym.make(ENV_NAME)
env.reset(seed=SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
random.seed(SEED)

agent = SACAgent(env)
replay = ReplayBuffer(REPLAY_SIZE)

total_steps = 0
episode = 0
ep_return = 0
ep_len = 0

os.makedirs("sac_checkpoints", exist_ok=True)

state, _ = env.reset()
while total_steps < MAX_STEPS:
    if total_steps < START_STEPS:
        action = env.action_space.sample()
    else:
        action = agent.select_action(state, evaluate=False)

    next_state, reward, terminated, truncated, _ = env.step(action)
# --- CORRECTION MASQUE ---
    # Si 'terminated' (mort) -> mask = 0
    # Si 'truncated' (temps écoulé) -> mask = 1 (car on veut continuer d'estimer la valeur)
    # Si rien -> mask = 1
    done = terminated or truncated
    mask = 1.0 if truncated else float(not done)

    # On stocke le 'mask' à la place du 'done' booléen pour simplifier l'update
    replay.push(state, action, reward, next_state, mask)

    state = next_state
    ep_return += reward
    ep_len += 1
    total_steps += 1

    if done:
        episode += 1
        print(f"Episode {episode} | Steps {total_steps} | Return {ep_return:.2f} | Len {ep_len}")
        state, _ = env.reset()
        ep_return = 0
        ep_len = 0

    
    if total_steps >= UPDATE_AFTER and total_steps % UPDATE_EVERY == 0:
        for j in range(UPDATE_EVERY):
            if len(replay) < BATCH_SIZE:
                continue
            info = agent.update(replay, BATCH_SIZE)
            #print(info)


env.close()