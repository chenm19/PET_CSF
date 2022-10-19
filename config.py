import numpy as np
import os

from data_prepare_const import LABEL_ID

class Config:
    N_dim = 160
    L = np.identity(N_dim)


class Start:
    def __init__(self, class_name=None, pet_data_path="data/PET/", csf_data_path="data/CSF/"):
        assert class_name in ["CN", "SMC", "EMCI", "LMCI", "AD"], "param class_name must in ['CN', 'SMC', 'EMCI', 'LMCI', 'AD'], but got \"{}\"!".format(class_name)
        self.class_name = class_name
        csf_data = np.load(os.path.join(csf_data_path, "CSF_{}.npy".format(self.class_name)))
        Am = np.random.rand(Config.N_dim)  # 0.11 * np.ones([Config.N_dim])
        Ao = np.random.rand(Config.N_dim)   # 0.12 * np.ones([Config.N_dim])
        Af = np.load(os.path.join(pet_data_path, "PET-A_{}.npy".format(self.class_name)))
        ACSF = np.expand_dims(csf_data[0], axis=0)  # 0.14 * np.ones(1)
        Tm = np.random.rand(Config.N_dim)   # 0.15 * np.ones([Config.N_dim])
        Tp = np.random.rand(Config.N_dim)   # 0.16 * np.ones([Config.N_dim])
        To = np.random.rand(Config.N_dim)   # 0.17 * np.ones([Config.N_dim])
        Tf = np.load(os.path.join(pet_data_path, "PET-T_{}.npy".format(self.class_name)))
        TCSF = np.expand_dims(csf_data[1] - csf_data[2], axis=0)  # 0.19 * np.ones(1)
        TpCSF = np.expand_dims(csf_data[2], axis=0)  # 0.20 * np.ones(1)
        N = np.load(os.path.join(pet_data_path, "PET-N_{}.npy".format(self.class_name)))
        self.all = np.concatenate([Am, Ao, Af, ACSF, Tm, Tp, To, Tf, TCSF, TpCSF, N])

# class Start:
#     Am = np.random.rand(Config.N_dim)  # 0.11 * np.ones([Config.N_dim])
#     Ao = np.random.rand(Config.N_dim)   # 0.12 * np.ones([Config.N_dim])
#     Af = np.random.rand(Config.N_dim)   # 0.13 * np.ones([Config.N_dim])
#     ACSF = np.random.rand(1)  # 0.14 * np.ones(1)
#     Tm = np.random.rand(Config.N_dim)   # 0.15 * np.ones([Config.N_dim])
#     Tp = np.random.rand(Config.N_dim)   # 0.16 * np.ones([Config.N_dim])
#     To = np.random.rand(Config.N_dim)   # 0.17 * np.ones([Config.N_dim])
#     Tf = np.random.rand(Config.N_dim)   # 0.18 * np.ones([Config.N_dim])
#     TCSF = np.random.rand(1)  # 0.19 * np.ones(1)
#     TpCSF = np.random.rand(1)  # 0.20 * np.ones(1)
#     N = np.random.rand(Config.N_dim)   # 0.21 * np.ones([Config.N_dim])
#     all = np.concatenate([Am, Ao, Af, ACSF, Tm, Tp, To, Tf, TCSF, TpCSF, N])



