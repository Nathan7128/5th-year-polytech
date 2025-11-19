import gymnasium as gym
import numpy as np

env = gym.make('MountainCarContinuous-v0', render_mode="human")

state = env.reset()
total_rewards = 0
for i in range(500):
    action = env.action_space.sample()
    next_state, reward, terminated, truncated, info = env.step(action)
    total_rewards += reward
    print(env.render())


env.close()
print(total_rewards)

positions_discrete = np.linspace(-1.2, 0.6, 10)
velocities_discrete = np.linspace(-0.07, 0.07, 100)

env = gym.make("MountainCarContinuous-v0", render_mode="rgb_array")  # default goal_velocity=0
env.reset(seed=42)