import array
import gymnasium as gym
import numpy as np
import wowsims
import json

from feral import *

class FeralSimEnv(gym.Env):

    def __init__(self, render_mode=None):
        Load(True)
        aura_count = len(Auras.Labels)
        target_aura_count = len(TargetAuras.Labels)
        other_count = 3 # energy, cp, remaining dur
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(aura_count+target_aura_count+other_count,), dtype=np.float64)
        Spells.register()
        self.action_space = gym.spaces.Discrete(len(Spells.registered_actions()))

    def _get_obs(self):
        Auras.update()
        TargetAuras.update()
        resources = np.array([wowsims.getRemainingDuration(), wowsims.getEnergy(), wowsims.getComboPoints()], dtype=np.float64)
        return np.concatenate((resources, Auras.Durations, TargetAuras.Durations))
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        Reset()
        observation = self._get_obs()
        info = {}
        return observation, info
    
    def step(self, action):
        wowsims.trySpell(Spells.registered_actions()[action])
        truncated = False
        terminated, needs_input = False, False
        while not (terminated or needs_input):
            needs_input = wowsims.needsInput()
            terminated = wowsims.step()
        reward = wowsims.getDamageDone() if terminated else 0
        obs = self._get_obs()
        info = {}
        return obs, reward, terminated, truncated, info


if __name__ == "__main__":
    e = FeralSimEnv()
    observation, info = e.reset()
    terminated = False
    while not terminated:
        obs = observation
        action = e.action_space.sample()
        observation, reward, terminated, truncated, info = e.step(e.action_space.sample())
        print(obs[0], action, reward, terminated)
    print(reward)
