import numpy as np


class Config:
    N_dim = 160
    L = np.identity(N_dim)


class Start:
    Am = np.random.rand(Config.N_dim)  # 0.11 * np.ones([Config.N_dim])
    Ao = np.random.rand(Config.N_dim)   # 0.12 * np.ones([Config.N_dim])
    Af = np.random.rand(Config.N_dim)   # 0.13 * np.ones([Config.N_dim])
    ACSF = np.random.rand(1)  # 0.14 * np.ones(1)
    Tm = np.random.rand(Config.N_dim)   # 0.15 * np.ones([Config.N_dim])
    Tp = np.random.rand(Config.N_dim)   # 0.16 * np.ones([Config.N_dim])
    To = np.random.rand(Config.N_dim)   # 0.17 * np.ones([Config.N_dim])
    Tf = np.random.rand(Config.N_dim)   # 0.18 * np.ones([Config.N_dim])
    TCSF = np.random.rand(1)  # 0.19 * np.ones(1)
    TpCSF = np.random.rand(1)  # 0.20 * np.ones(1)
    N = np.random.rand(Config.N_dim)   # 0.21 * np.ones([Config.N_dim])
    all = np.concatenate([Am, Ao, Af, ACSF, Tm, Tp, To, Tf, TCSF, TpCSF, N])



