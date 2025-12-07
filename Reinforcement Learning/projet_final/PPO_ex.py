# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 14:36:26 2025

@author: julien.hautot
"""

import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Normal
import numpy as np

# --- Hyperparamètres ---
env_name = "Hopper-v5"
gamma = 0.99
lr = 3e-4
clip_eps = 0.2
epochs = 400
steps_per_epoch = 4096
batch_size = 128
entropy_coef = 0.01
hidden_dim = 256
device = "cuda" if torch.cuda.is_available() else "cpu"

# --- Environnement ---
env = gym.make(env_name)
obs_dim = env.observation_space.shape[0]
act_dim = env.action_space.shape[0]
max_action = float(env.action_space.high[0])

# --- Réseau Policy (Gaussian) ---
class Policy(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim, device=device),
            nn.Tanh(),
            nn.Linear(hidden_dim, act_dim, device=device),
            nn.Tanh()
        )
        self.log_std = nn.Parameter(torch.zeros(act_dim))  

    def forward(self, x):
        mu = self.net(x)
        std = torch.exp(self.log_std)
        return mu, std

# --- Réseau Value ---
class Value(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim, device=device),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim, device=device),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, x):
        return self.net(x)

# --- Initialisation ---
policy = Policy().to(device)
value = Value().to(device)
optimizer_policy = optim.Adam(policy.parameters(), lr=lr)
optimizer_value = optim.Adam(value.parameters(), lr=lr)

# --- Fonction pour générer trajectoires ---
def collect_trajectories():
    obs = env.reset()[0]
    obs_list, act_list, rew_list, logp_list, val_list, done_list = [], [], [], [], [], []
    for _ in range(steps_per_epoch):
        obs_tensor = torch.FloatTensor(obs).to(device)
        mu, std = policy(obs_tensor)
        dist = Normal(mu, std)
        act = dist.sample()
        logp = dist.log_prob(act).sum()
        val = value(obs_tensor)

        # Scale action to environment
        act_clamped = nn.Tanh()(act)
        next_obs, rew, terminated, truncated, _ = env.step(act_clamped.cpu().detach().numpy())
        done = terminated or truncated

        # Stockage
        obs_list.append(obs)
        act_list.append(act.detach())
        rew_list.append(rew)
        logp_list.append(logp.detach())
        val_list.append(val.detach())
        done_list.append(done)

        obs = next_obs
        if done:
            obs = env.reset()[0]

    return obs_list, act_list, rew_list, logp_list, val_list, done_list

# --- Fonction pour calculer avantages ---
def compute_advantages(rews, vals, dones):
    advs, gae = [], 0
    vals = vals + [0]  # V(s_T) = 0
    for t in reversed(range(len(rews))):
        delta = rews[t] + gamma * vals[t + 1] * (1 - dones[t]) - vals[t]
        gae = delta + gamma * 0.95 * (1 - dones[t]) * gae
        advs.insert(0, gae)
    returns = [adv + val for adv, val in zip(advs, vals[:-1])]
    return torch.FloatTensor(advs).to(device), torch.FloatTensor(returns).to(device)

# --- Entraînement ---
loss_fn = nn.MSELoss()

for epoch in range(epochs):
    obs_list, act_list, rew_list, logp_list, val_list, done_list = collect_trajectories()
    advs, returns = compute_advantages(rew_list, val_list, done_list)
    
    obs_tensor = torch.FloatTensor(obs_list).to(device)
    act_tensor = torch.stack(act_list).to(device)
    old_logp_tensor = torch.stack(logp_list).to(device)
    
    # --- Mise à jour PPO ---
    for _ in range(10):  # 10 mini-epochs
        idx = np.random.permutation(len(obs_list))
        for start in range(0, len(obs_list), batch_size):
            end = start + batch_size
            batch_idx = idx[start:end]

            obs_b = obs_tensor[batch_idx].to(device)
            act_b = act_tensor[batch_idx].to(device)
            adv_b = advs[batch_idx].to(device)
            ret_b = returns[batch_idx].to(device)
            old_logp_b = old_logp_tensor[batch_idx].to(device)

            # Policy
            mu, std = policy(obs_b)
            dist = Normal(mu, std)
            logp = dist.log_prob(act_b).sum(axis=-1)
            entropy = dist.entropy().sum(axis=-1).mean()
            ratio = torch.exp(logp - old_logp_b)
            surr1 = ratio*adv_b
            surr2 = torch.clamp(ratio, 1 - clip_eps, 1 +  clip_eps)*adv_b
            loss_policy = -torch.min(surr1, surr2).mean() - entropy_coef * entropy

            # Value
            val_pred = value(obs_b)
            loss_value = loss_fn(val_pred.squeeze(), ret_b)

            # Backprop
            optimizer_policy.zero_grad()
            loss_policy.backward()
            optimizer_policy.step()

            optimizer_value.zero_grad()
            loss_value.backward()
            optimizer_value.step()

    # --- Stats ---
    print(f"Epoch {epoch+1} | Avg Reward = {np.mean(rew_list):.2f}")