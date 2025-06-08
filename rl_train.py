import csv
import json
import random
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
from config import LOG_BASE_DIR

import torch
import torch.nn as nn
import torch.optim as optim


class DuelingDQN(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.feature = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
        )
        self.adv = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, action_dim),
        )
        self.val = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.feature(x)
        adv = self.adv(feat)
        val = self.val(feat)
        return val + adv - adv.mean(dim=1, keepdim=True)


class DDQNAgent:
    def __init__(self, state_dim: int = 5, action_dim: int = 3):
        self.policy = DuelingDQN(state_dim, action_dim)
        self.target = DuelingDQN(state_dim, action_dim)
        self.target.load_state_dict(self.policy.state_dict())
        self.memory: deque[Tuple] = deque(maxlen=10000)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=0.0005)
        self.loss_fn = nn.HuberLoss()
        self.steps = 0
        self.eps_start = 1.0
        self.eps_end = 0.05
        self.eps_decay = 50000
        self.action_dim = action_dim

    def remember(self, *transition: Tuple):
        self.memory.append(transition)

    def act(self, state: torch.Tensor) -> int:
        eps = max(self.eps_end, self.eps_start - self.steps / self.eps_decay)
        if random.random() < eps:
            return random.randrange(self.action_dim)
        with torch.no_grad():
            q = self.policy(state.unsqueeze(0))
            return int(q.argmax().item())

    def update(self, batch_size: int = 32, gamma: float = 0.99) -> float:
        if len(self.memory) < batch_size:
            return 0.0
        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        states = torch.tensor(states, dtype=torch.float32)
        actions = torch.tensor(actions, dtype=torch.long).unsqueeze(1)
        rewards = torch.tensor(rewards, dtype=torch.float32).unsqueeze(1)
        next_states = torch.tensor(next_states, dtype=torch.float32)
        dones = torch.tensor(dones, dtype=torch.float32).unsqueeze(1)

        q_values = self.policy(states).gather(1, actions)
        next_actions = self.policy(next_states).argmax(1, keepdim=True)
        next_q = self.target(next_states).gather(1, next_actions)
        target_q = rewards + gamma * next_q * (1 - dones)
        loss = self.loss_fn(q_values, target_q.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.steps += 1
        if self.steps % 500 == 0:
            self.target.load_state_dict(self.policy.state_dict())
        return float(loss.item())


def load_dataset(path: Path) -> List[Tuple]:
    data = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            if d["next_state"] is None:
                continue
            data.append(
                (
                    d["state"],
                    d["action"],
                    d["reward"],
                    d["next_state"],
                    d["done"],
                )
            )
    return data


def train(data_path: Path, out_dir: Path | None = None, episodes: int = 1):
    out_dir = out_dir or (LOG_BASE_DIR / "RL모델결과")
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(data_path)
    agent = DDQNAgent()
    rewards: List[float] = []
    for ep in range(episodes):
        random.shuffle(dataset)
        total_loss = 0.0
        for transition in dataset:
            agent.remember(*transition)
            loss = agent.update()
            total_loss += loss
        rewards.append(total_loss)
    date_str = datetime.now().strftime("%Y-%m-%d")
    weight_path = out_dir / "nova_policy_weights_v1.pth"
    torch.save(agent.policy.state_dict(), weight_path)
    csv_path = out_dir / f"reward_log_{date_str}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["episode", "loss"])
        for i, r in enumerate(rewards):
            writer.writerow([i, r])
    return weight_path, csv_path


if __name__ == "__main__":
    base = LOG_BASE_DIR / "강화학습전처리"
    latest = sorted(base.glob("nova_rl_data_*.jsonl"))[-1]
    w, c = train(latest)
    print("saved", w, c)
