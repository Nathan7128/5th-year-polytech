import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import random

class RandomAgent:
    def __init__(self, env: gym.Env, learning_rate=0.1, discount_factor=0.2):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.n_states = env.observation_space.n
        self.n_actions = env.action_space.n
        self.q_table = np.zeros(shape=(self.n_states, self.n_actions))

    def get_action(self, state):
        return np.argmax(self.q_table[state])
    
    def update_param(self, s, a, reward, next_s):
        old_value = self.q_table[s, a]
        next_max = np.max(self.q_table[next_s])
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        self.q_table[s, a] = new_value


env = gym.make("Taxi-v3", render_mode = "ansi")
print(f"Action Space {env.action_space.n}")
print(f"State Space {env.observation_space.n}")

env.reset(seed=42)

agent = RandomAgent(env)

n_episodes = 1000

epsilon = 0.2

timesteps_per_episode = []
penalties_per_episode = []


for i in range (n_episodes):
    state = env.reset()[0]

    epochs, penalties, reward, = 0, 0, 0
    done = False

    while not done:
        if random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()

        else:
            action = agent.get_action(state=state)

        next_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        agent.update_param(s=state, a=action, reward=reward, next_s=next_state)

        if reward == -1:
            penalties += +1

        state = next_state

        epochs += 1
        penalties += reward

    timesteps_per_episode.append(epochs)
    penalties_per_episode.append(penalties)


# --- Affichage amélioré ---
plt.figure(figsize=(10, 6))

# Graphique 1 : durée par épisode
plt.subplot(2, 1, 1)
plt.plot(timesteps_per_episode, color="royalblue", linewidth=2)
plt.title("Durée (timesteps) par épisode", fontsize=13)
plt.xlabel("Épisode")
plt.ylabel("Nombre de pas")
plt.grid(True, linestyle="--", alpha=0.6)

# Graphique 2 : récompenses/pénalités par épisode
plt.subplot(2, 1, 2)
plt.plot(penalties_per_episode, color="crimson", linewidth=2)
plt.title("Récompense totale (ou pénalités) par épisode", fontsize=13)
plt.xlabel("Épisode")
plt.ylabel("Somme des récompenses")
plt.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.show()