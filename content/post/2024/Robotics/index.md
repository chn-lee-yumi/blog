---
title: "Robotics 学习笔记"
description: "Robotics 学习笔记"
date: 2024-11-09T13:44:00+11:00
lastmod: 2024-11-09T13:44:00+11:00
categories:
  - 学习
tags:
  - AI
---

## Problem Framework

### Markov Decision Process (MDP)

- Discrete time step, can be continuous space of action and state
- We don't know the exact outcome of the action
- Once the action is performed, we know exactly what happened
- The agent's state is known (fully observed) -- observation and the state is the same here

Formally defined as a 4-tuples (S, A, T, R):
- State Space
- Action Space
- Transition Function
- Reward Function

### Partially Observable Markov Decision Process (POMDP)

- Almost the same as MDP, except: the effect of the action are not known exactly before the action is performed (non-deterministic action effects)
- In addition, the agent's state is not known exactly (partially observed)

- **State Space (not known), instead, we have "Belief" -- distribution over the state space**
- Action Space
- **Observation Space**
- Transition Function
- **Observation Function**
- Reward Function

A POMDP can be viewed as an MDP in the belief space. (The belief is 1 at a particular thing.)

### Reinforcement Learning (RL)

- The agent learns by trying and evaluating states and actions
- An RL Agent is an MDP agent where the transition and/or reward functions are not initially known
- Problem-wise, it's essentially a POMDP, where partial observability is caused by incomplete information about the underlying MDP problem

## Solving

### MDP

Online:
- Value Iteration
- Policy Iteration

Offline:
- Real-Time Dynamic Programming (RTDP)
- Monte Carlo Tree Search (MCTS)

### POMDP

- Offline planners
- Online solvers
- Learning-based Particle Filter
- Learning-based Solvers

### RL

