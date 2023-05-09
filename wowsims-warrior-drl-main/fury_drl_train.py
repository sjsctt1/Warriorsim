import os
from typing import Dict

import gymnasium as gym
from gymnasium.wrappers import FrameStack
from fury_sim_env import FurySimEnv
from gymnasium.envs.registration import register

from ray import air, tune
from ray.tune import CLIReporter
from ray.rllib.policy import Policy
from ray.rllib.algorithms.ppo import PPOConfig
from ray.tune.registry import register_env
from ray.rllib.algorithms.callbacks import DefaultCallbacks
from ray.rllib.evaluation import Episode, RolloutWorker
from ray.rllib.algorithms.algorithm import Algorithm


class MyCallbacks(DefaultCallbacks):
    def on_episode_start(
        self,
        *,
        worker: RolloutWorker,
        base_env: gym.Env,
        policies: Dict[str, Policy],
        episode: Episode,
        env_index: int,
        **kwargs
    ):
        # Make sure this episode has just been started (only initial obs
        # logged so far).
        assert episode.length == 0, (
            "ERROR: `on_episode_start()` callback should be called right "
            "after env reset!"
        )
        print("episode {} (env-idx={}) started.".format(episode.episode_id, env_index))

    def on_episode_end(
        self,
        *,
        worker: RolloutWorker,
        base_env: gym.Env,
        policies: Dict[str, Policy],
        episode: Episode,
        env_index: int,
        **kwargs
    ):
        # Check if there are multiple episodes in a batch, i.e.
        # "batch_mode": "truncate_episodes".
        if worker.policy_config["batch_mode"] == "truncate_episodes":
            # Make sure this episode is really done.
            assert episode.batch_builder.policy_collectors["default_policy"].batches[
                -1
            ]["dones"][-1], (
                "ERROR: `on_episode_end()` should only be called "
                "after episode is done!"
            )
        dps = episode.last_info_for()["dps"]
        print(
            "episode {} (env-idx={}) ended with length {} and {} dps".format(
                episode.episode_id, env_index, episode.length, dps
            )
        )
        episode.custom_metrics["dps"] = dps

os.environ["TUNE_ORIG_WORKING_DIR"] = os.getcwd()

algorithm_version = 'PPO'
comment_suffix = "bloodsurge-reward-0.5"

config = PPOConfig()

config.num_gpus = 0
config.log_level = "INFO"
config.environment(env="FurySimEnv")
config.batch_mode = "complete_episodes"
config.rollouts(num_rollout_workers=23)
config.callbacks(MyCallbacks)
config.enable_connectors = False
config.train_batch_size = 10000
# config.training(
                # lambda_= tune.grid_search([0.9, 0.95, 1]),
                # sgd_minibatch_size=tune.grid_search([500, 1000, 1500]),
                # num_sgd_iter=tune.grid_search([10, 20, 30]),
                # entropy_coeff= tune.grid_search([0, 0.005, 0.01]),
                # kl_coeff= tune.grid_search([0.3, 0.4, 0.5]),
                # clip_param= tune.grid_search([0.1, 0.2, 0.3])
                # )

config.training(
                lambda_= 0.95,
                sgd_minibatch_size= 500,
                num_sgd_iter= 10,
                entropy_coeff= 0.0,
                kl_coeff= 0.5,
                clip_param= 0.3
                )


register(id="FurySimEnv", entry_point="fury_sim_env:FurySimEnv")
env = gym.make("FurySimEnv")
env_creator = lambda config: FurySimEnv(...)
# env_creator = lambda config: FrameStack(env, 10)


register_env("FurySimEnv", env_creator=env_creator)

config = config.to_dict()

result = tune.Tuner(algorithm_version,
            param_space=config,
            run_config=air.RunConfig(
            stop={"episodes_total": 10000},
            checkpoint_config=air.CheckpointConfig(
                checkpoint_at_end=True,
            ),

            local_dir=f"models/{comment_suffix}",

            progress_reporter=CLIReporter(

            metric_columns={

                "training_iteration": "training_iteration",

                "time_total_s": "time_total_s",

                "timesteps_total": "timesteps",

                "episodes_this_iter": "episodes_trained",

                "episode_reward_mean": "mean_reward_sum",

                "dps": "dps",                
            },
            sort_by_metric=True,
            ),
        ),
    ).fit()