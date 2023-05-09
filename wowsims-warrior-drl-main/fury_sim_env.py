import numpy as np

import wowsims
from fury import *

import gymnasium as gym
from gymnasium import spaces

class FurySimEnv(gym.Env):
    def __init__(self, render_mode=None):
        self.settings = Settings()
        self.settings.Load(True)
        aura_count = len(Auras.Labels)
        target_aura_count = len(TargetAuras.Labels)
        # Rage, sim duration, melee swing time [MH, OH], GCD ready time shape count,
        # last action
        other_count = 6
        Spells.register()
        self.spells_count = len(Spells.registered_actions())

        self.last_damage_done = 0
        self.observation_space = spaces.Box(low=-1, high=1, shape=(aura_count+target_aura_count+other_count+self.spells_count,), dtype=np.float64)
        # Last action is reserved for doNothing()
        self.action_space = spaces.Discrete(self.spells_count+1)

    def _get_obs(self, last_action):
        Auras.update()
        # TargetAuras.update()
        Spells.update()
        last_action = np.float64(last_action / (self.spells_count+1))
        non_array_obs = np.array([wowsims.getRemainingDuration() / wowsims.getIterationDuration(), wowsims.getRage(), wowsims.getGcdReadyTime(), 
                                last_action], dtype=np.float64)
        return np.concatenate((non_array_obs, Auras.Durations, TargetAuras.Durations, Spells.Cooldowns, AutoAttacks.get_swing_time()), dtype=np.float64)
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        self.settings.Reset()
        self.last_damage_done = 0
        observation = self._get_obs(self.spells_count+1)
        return observation, {}
    
    def step(self, action):
        truncated = False
        cast = False
        terminated, needs_input = False, False
        while not (terminated or needs_input):
            needs_input = wowsims.needsInput()
            terminated = wowsims.step()

        reward = 0

        if needs_input :
            # Reward agent for using bloodsurge slam
            if action == 2 and Auras.get_dur("Bloodsurge Proc") > 0:
                reward += 0.5
                
            # Last index of action means DoNothing
            if action == self.spells_count:
                cast = wowsims.doNothing()
            else :
                cast = wowsims.trySpell(Spells.registered_actions()[action])
        
        damage_done = wowsims.getDamageDone()
        dps = 0 if wowsims.getCurrentTime() <= 0 else damage_done / wowsims.getCurrentTime()
        damage_this_step = damage_done - self.last_damage_done
        self.last_damage_done = damage_done

        reward += dps / 10000

        observation = self._get_obs(last_action=action)
        
        info = {'dps': dps, 'spell metrics': wowsims.getSpellMetrics(), 'debug log': [wowsims.getCurrentTime(), action, cast, damage_this_step, damage_done, observation[1]]}
            
        return observation, reward, terminated, truncated, info
