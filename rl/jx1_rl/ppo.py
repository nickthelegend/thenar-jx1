"""PPO with an asymmetric actor-critic (the algorithm of rsl_rl, which Isaac Lab uses), in plain PyTorch.

Actor: MLP on the (normalised) actor observation -> Gaussian mean, state-independent learned std.
Critic: MLP on the privileged observation. Running mean/std normalisers for both inputs are part of the checkpoint and
are baked into the exported policy. GAE(lambda), clipped surrogate + clipped value loss, entropy bonus, KL-adaptive
learning rate, time-out bootstrapping.
"""
from __future__ import annotations

import torch
import torch.nn as nn


def mlp(n_in, hidden, n_out, activation="elu"):
    act = {"elu": nn.ELU, "relu": nn.ReLU, "tanh": nn.Tanh}[activation]
    layers, d = [], n_in
    for h in hidden:
        layers += [nn.Linear(d, h), act()]
        d = h
    layers.append(nn.Linear(d, n_out))
    return nn.Sequential(*layers)


class Normalizer(nn.Module):
    """Running mean / std (Chan's parallel update); frozen with .eval()."""

    def __init__(self, n, eps=1e-2):
        super().__init__()
        self.eps = eps
        self.register_buffer("mean", torch.zeros(n))
        self.register_buffer("var", torch.ones(n))
        self.register_buffer("count", torch.zeros(()))

    def forward(self, x):
        return (x - self.mean) / (self.var.sqrt() + self.eps)

    @torch.no_grad()
    def update(self, x):
        b_mean, b_var, n = x.mean(0), x.var(0, unbiased=False), x.shape[0]
        tot = self.count + n
        delta = b_mean - self.mean
        self.mean += delta * n / tot
        self.var = (self.var * self.count + b_var * n + delta ** 2 * self.count * n / tot) / tot
        self.count = tot


class ActorCritic(nn.Module):
    def __init__(self, n_obs, n_priv, n_act, actor_hidden, critic_hidden, activation="elu", init_noise_std=1.0):
        super().__init__()
        self.actor = mlp(n_obs, actor_hidden, n_act, activation)
        self.critic = mlp(n_priv, critic_hidden, 1, activation)
        self.log_std = nn.Parameter(torch.full((n_act,), float(torch.log(torch.tensor(init_noise_std)))))
        self.obs_norm = Normalizer(n_obs)
        self.priv_norm = Normalizer(n_priv)

    def distribution(self, obs_n):
        mean = self.actor(obs_n)
        return torch.distributions.Normal(mean, self.log_std.exp().expand_as(mean))

    def value(self, priv_n):
        return self.critic(priv_n).squeeze(-1)


class Storage:
    def __init__(self, T, N, n_obs, n_priv, n_act, device):
        z = lambda *s: torch.zeros(*s, device=device)  # noqa: E731
        self.obs, self.priv, self.actions = z(T, N, n_obs), z(T, N, n_priv), z(T, N, n_act)
        self.rewards, self.dones, self.values, self.logp = z(T, N), z(T, N), z(T, N), z(T, N)
        self.mu, self.sigma = z(T, N, n_act), z(T, N, n_act)
        self.returns, self.adv = z(T, N), z(T, N)
        self.T, self.step = T, 0

    def add(self, obs, priv, actions, rewards, dones, values, logp, mu, sigma):
        t = self.step
        self.obs[t], self.priv[t], self.actions[t] = obs, priv, actions
        self.rewards[t], self.dones[t], self.values[t], self.logp[t] = rewards, dones, values, logp
        self.mu[t], self.sigma[t] = mu, sigma
        self.step += 1

    def compute_returns(self, last_values, gamma, lam):
        adv = torch.zeros_like(last_values)
        for t in reversed(range(self.T)):
            nxt = last_values if t == self.T - 1 else self.values[t + 1]
            nonterm = 1.0 - self.dones[t]
            delta = self.rewards[t] + nonterm * gamma * nxt - self.values[t]
            adv = delta + nonterm * gamma * lam * adv
            self.returns[t] = adv + self.values[t]
        self.adv = self.returns - self.values
        self.adv = (self.adv - self.adv.mean()) / (self.adv.std() + 1e-8)

    def minibatches(self, n_mb, epochs):
        B = self.T * self.obs.shape[1]
        flat = lambda x: x.reshape(B, *x.shape[2:])  # noqa: E731
        data = [flat(x) for x in (self.obs, self.priv, self.actions, self.values, self.adv, self.returns, self.logp, self.mu, self.sigma)]
        size = B // n_mb
        for _ in range(epochs):
            idx = torch.randperm(B, device=self.obs.device)
            for i in range(n_mb):
                j = idx[i * size:(i + 1) * size]
                yield [x[j] for x in data]


class PPO:
    def __init__(self, ac: ActorCritic, cfg: dict, device):
        self.ac, self.cfg, self.device = ac, cfg, device
        self.lr = cfg["learning_rate"]
        self.opt = torch.optim.Adam(ac.parameters(), lr=self.lr)

    def update(self, st: Storage):
        c = self.cfg
        stats = {"value_loss": 0.0, "surrogate": 0.0, "entropy": 0.0, "kl": 0.0}
        n = 0
        for obs, priv, act, old_v, adv, ret, old_logp, old_mu, old_sigma in st.minibatches(c["num_mini_batches"], c["num_learning_epochs"]):
            dist = self.ac.distribution(obs)
            logp = dist.log_prob(act).sum(-1)
            value = self.ac.value(priv)
            mu, sigma = dist.mean, dist.stddev
            entropy = dist.entropy().sum(-1)
            with torch.no_grad():
                kl = torch.sum(torch.log(sigma / old_sigma + 1e-5) + (old_sigma ** 2 + (old_mu - mu) ** 2) / (2.0 * sigma ** 2) - 0.5, -1).mean()
            if c.get("schedule") == "adaptive":
                if kl > c["desired_kl"] * 2.0:
                    self.lr = max(1e-5, self.lr / 1.5)
                elif 0.0 < kl < c["desired_kl"] / 2.0:
                    self.lr = min(1e-2, self.lr * 1.5)
                for g in self.opt.param_groups:
                    g["lr"] = self.lr
            ratio = torch.exp(logp - old_logp)
            surrogate = torch.max(-adv * ratio, -adv * torch.clamp(ratio, 1 - c["clip_param"], 1 + c["clip_param"])).mean()
            v_clip = old_v + (value - old_v).clamp(-c["clip_param"], c["clip_param"])
            value_loss = torch.max((value - ret) ** 2, (v_clip - ret) ** 2).mean()
            loss = surrogate + c["value_loss_coef"] * value_loss - c["entropy_coef"] * entropy.mean()
            self.opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.ac.parameters(), c["max_grad_norm"])
            self.opt.step()
            stats["value_loss"] += value_loss.item()
            stats["surrogate"] += surrogate.item()
            stats["entropy"] += entropy.mean().item()
            stats["kl"] += kl.item()
            n += 1
        st.step = 0
        return {k: v / n for k, v in stats.items()} | {"lr": self.lr, "std": self.ac.log_std.exp().mean().item()}
