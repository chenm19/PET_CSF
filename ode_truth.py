import os

import matplotlib.pyplot as plt
import numpy as np

import time
from scipy.integrate import odeint
from tqdm import tqdm

from parameters import *
from config import Start, Config
from utils import MultiSubplotDraw
from data_prepare_const import LABEL_LIST

"""
# Chen asked me to add these comments here - if you need :) 
CSF_CN counts=153.0 avg=[203.15882353  64.9379085   27.99281046]
CSF_SMC counts=78.0 avg=[204.64102564  63.8974359   35.9025641 ]
CSF_EMCI counts=41.0 avg=[190.7804878   79.9902439   34.88780488]
CSF_LMCI counts=108.0 avg=[184.77314815  87.7         34.23425926]
CSF_AD counts=307.0 avg=[144.74918567 119.13485342  47.93029316]
CSF counts: [153.  78.  41. 108. 307.]
PET-A counts: [81. 42. 88. 35. 19.]
PET-T counts: [78. 42. 83. 30. 32.]
PET-N counts: [92. 43. 80. 39. 11.]
"""


def get_now_string():
    return time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))


class ConstTruth:
    def __init__(self, **params):
        assert "csf_folder_path" in params and "pet_folder_path" in params, "please provide the save folder paths"
        csf_folder_path, pet_folder_path = params["csf_folder_path"], params["pet_folder_path"]
        self.class_num = len(LABEL_LIST)
        if "x" not in params:
            self.x = [2 * item for item in range(self.class_num)]
        else:
            self.x = params.get("x")
        self.y = {}
        self.lines = ["APET", "TPET", "NPET", "ACSF", "TpCSF", "TCSF", "TtCSF"]
        for one_line in self.lines:
            self.y[one_line] = []
        for i, class_name in enumerate(LABEL_LIST):
            csf_data = np.load(os.path.join(csf_folder_path, "CSF_{}.npy".format(class_name)))
            pet_data_a = np.load(os.path.join(pet_folder_path, "PET-A_{}.npy".format(class_name)))
            pet_data_t = np.load(os.path.join(pet_folder_path, "PET-T_{}.npy".format(class_name)))
            pet_data_n = np.load(os.path.join(pet_folder_path, "PET-N_{}.npy".format(class_name)))
            self.y["APET"] = self.y["APET"] + [np.mean(pet_data_a)]
            self.y["TPET"] = self.y["TPET"] + [np.mean(pet_data_t)]
            self.y["NPET"] = self.y["NPET"] + [np.mean(pet_data_n)]

            self.y["ACSF"] = self.y["ACSF"] + [csf_data[0]]
            self.y["TtCSF"] = self.y["TtCSF"] + [csf_data[1]]
            self.y["TpCSF"] = self.y["TpCSF"] + [csf_data[2]]
            self.y["TCSF"] = self.y["TCSF"] + [csf_data[1] - csf_data[2]]


class ADSolver:
    def __init__(self, class_name, const_truth=None):
        self.n = Config.N_dim
        self.L = Config.L
        self.t = np.linspace(0, 10 - 0.1, 100)
        self.class_name = class_name
        self.const_truth = const_truth
        self.y0 = Start(class_name).all
        # print("ODE size: {}".format(self.y0.shape))
        self.y = odeint(self.pend, self.y0, self.t)
        self.lines = ["APET", "TPET", "NPET", "ACSF", "TpCSF", "TCSF", "TtCSF"]
        self.output = self.get_output()
        # print("output has {} curves".format(len(self.output)))
        self.output_names = ["$A_{PET}$", "$T_{PET}$", "$N_{PET}$", "$A_{CSF}$", "$T_{pCSF}$", "$T_{CSF}$", "$T_{tCSF}$"]
        self.output_names_rest = ["$A_{m} Avg$", "$T_{m} Avg$", "$A_{o} Avg$", "$T_{o} Avg$", "$T_{p} Avg$"]
        self.colors = ["red", "green", "blue", "cyan", "orange", "purple", "brown", "gray", "olive"]

    def get_output(self):
        Am = self.y[:, 0: self.n]
        Ao = self.y[:, self.n: self.n * 2]
        Af = self.y[:, self.n * 2: self.n * 3]
        ACSF = self.y[:, self.n * 3: self.n * 3 + 1]
        Tm = self.y[:, self.n * 3 + 1: self.n * 4 + 1]
        Tp = self.y[:, self.n * 4 + 1: self.n * 5 + 1]
        To = self.y[:, self.n * 5 + 1: self.n * 6 + 1]
        Tf = self.y[:, self.n * 6 + 1: self.n * 7 + 1]
        TCSF = self.y[:, self.n * 7 + 1: self.n * 7 + 2]
        TpCSF = self.y[:, self.n * 7 + 2: self.n * 7 + 3]
        N = self.y[:, self.n * 7 + 3: self.n * 8 + 3]

        ACSF = np.expand_dims(ACSF[:, 0], axis=0)  # np.expand_dims(k_sA * np.sum(Am, axis=1), axis=0)
        TCSF = np.expand_dims(TCSF[:, 0], axis=0)  # np.expand_dims(k_sT * np.sum(Tm, axis=1), axis=0)
        TpCSF = np.expand_dims(TpCSF[:, 0], axis=0)  # np.expand_dims(k_sTp * np.sum(Tp, axis=1), axis=0)
        APET = np.expand_dims(np.mean(np.swapaxes(Af, 0, 1), axis=0), axis=0)
        TPET = np.expand_dims(np.mean(np.swapaxes(Tf, 0, 1), axis=0), axis=0)
        NPET = np.expand_dims(np.mean(np.swapaxes(N, 0, 1), axis=0), axis=0)
        TtCSF = TpCSF + TCSF
        Am_avg = np.expand_dims(np.mean(Am, axis=1), axis=0)
        Tm_avg = np.expand_dims(np.mean(Tm, axis=1), axis=0)
        Ao_avg = np.expand_dims(np.mean(Ao, axis=1), axis=0)
        To_avg = np.expand_dims(np.mean(To, axis=1), axis=0)
        Tp_avg = np.expand_dims(np.mean(Tp, axis=1), axis=0)

        # APET_average = np.expand_dims(np.mean(APET, axis=0), axis=0)
        # TPET_average = np.expand_dims(np.mean(TPET, axis=0), axis=0)
        # NPET_average = np.expand_dims(np.mean(NPET, axis=0), axis=0)
        # return [APET, TPET, NPET, ACSF, TpCSF, TCSF, TtCSF, Ao_sum, To_sum]
        return [APET, TPET, NPET, ACSF, TpCSF, TCSF, TtCSF, Am_avg, Tm_avg, Ao_avg, To_avg, Tp_avg]

    def pend(self, y, t):
        Am = y[0: self.n]
        Ao = y[self.n: self.n * 2]
        Af = y[self.n * 2: self.n * 3]
        ACSF = y[self.n * 3: self.n * 3 + 1]
        Tm = y[self.n * 3 + 1: self.n * 4 + 1]
        Tp = y[self.n * 4 + 1: self.n * 5 + 1]
        To = y[self.n * 5 + 1: self.n * 6 + 1]
        Tf = y[self.n * 6 + 1: self.n * 7 + 1]
        TCSF = y[self.n * 7 + 1: self.n * 7 + 2]
        TpCSF = y[self.n * 7 + 2: self.n * 7 + 3]
        N = y[self.n * 7 + 3: self.n * 8 + 3]
        
        sum_func = np.sum
        matmul_func = np.matmul
        Am_ = k_p1Am + k_p2Am * (To ** n_TA) / (K_mTA ** n_TA + To ** n_TA) - k_dAm * Am - n_a1A * k_a1A * (Am ** n_a1A) - n_a2A * k_a2A * Af * (Am ** n_a2A) + n_aA * k_diA * Ao - n_cA * k_cA * (Am ** n_cA) * Ao - k_sA * Am + d_Am * matmul_func(self.L, Am)
        Ao_ = - k_dAo * Ao + k_a1A * (Am ** n_a1A) + k_a2A * Af * (Am ** n_a2A) - k_diA * Ao - k_cA * (Am ** n_cA) * Ao + d_Ao * matmul_func(self.L, Ao)
        Af_ = k_cA * (Am ** n_cA) * Ao
        ACSF_ = k_sA * sum_func(Am) - k_yA * ACSF
        Tm_ = k_pTm - k_dTm * Tm - (k_ph1 + k_ph2 * (Ao ** n_AT) / (K_mAT ** n_AT + Ao ** n_AT)) * Tm + k_deph * Tp - n_a1T * k_a1T * (Tm ** n_a1T) * (Tp ** n_a1Tp) - n_a2T * k_a2T * Tf * (Tm ** n_a2T) * (Tp ** n_a2Tp) + n_aT * k_diT * To - n_cT * k_cT * (Tm ** n_cT) * (Tp ** n_cTp) * To - k_sT * Tm + d_Tm * matmul_func(self.L, Tm)
        Tp_ = -k_dTp * Tp + (k_ph1 + k_ph2 * (Ao ** n_AT) / (K_mAT ** n_AT + Ao ** n_AT)) * Tm - k_deph * Tp - n_a1Tp * k_a1T * (Tm ** n_a1T) * (Tp ** n_a1Tp) - n_a2Tp * k_a2T * Tf * (Tm ** n_a2T) * (Tp ** n_a2Tp) + n_aTp * k_diT * To - n_cTp * k_cT * (Tm ** n_cT) * (Tp ** n_cTp) * To - k_sTp * Tp + d_Tp * matmul_func(self.L, Tp)
        To_ = - k_dTo * To + k_aT * (Tm ** n_aT) * (Tp ** n_aTp) - k_diT * To - k_cT * (Tm ** n_cT) * (Tp ** n_cTp) * To + d_To * matmul_func(self.L, To)
        Tf_ = k_cT * (Tm ** n_cT) * (Tp ** n_cTp) * To
        TCSF_ = k_sT * sum_func(Tm) - k_yT * TCSF
        TpCSF_ = k_sTp * sum_func(Tp) - k_yTp * TpCSF
        N_ = k_AN * (Ao ** n_AoN + Af ** n_AfN) / (K_mAN ** n_AN + Ao ** n_AoN + Af ** n_AfN) + k_TN * (To ** n_ToN + Tf ** n_TfN) / (K_mTN ** n_TN + To ** n_ToN + Tf ** n_TfN)
        # for item in [Am_, Ao_, Af_, ACSF_, Tm_, Tp_, To_, Tf_, TCSF_, TpCSF_, N_]:
        #     print(item.shape)
        dy = np.concatenate([Am_, Ao_, Af_, ACSF_, Tm_, Tp_, To_, Tf_, TCSF_, TpCSF_, N_])
        # print(dy.shape)

        return dy

    def draw(self, save_flag=True, time_string="test"):

        folder_path = "figure/{}/".format(time_string)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        save_path = os.path.join(folder_path, "{}.png".format(self.class_name))
        m = MultiSubplotDraw(row=3, col=3, fig_size=(24, 18), tight_layout_flag=True, show_flag=True, save_flag=save_flag,
                             save_path=save_path, save_dpi=400)
        for name, data, color, line_string in zip(self.output_names, self.output[:len(self.output_names)], self.colors[:len(self.output_names)], self.lines):
            # print(line_string, len(data))
            # print(data)
            ax = m.add_subplot(
                y_lists=data,
                x_list=self.t,
                color_list=[color],
                line_style_list=["solid"],
                fig_title=name,
                legend_list=[name],
                line_width=2,
            )
            if self.const_truth:
                x = self.const_truth.x
                y = self.const_truth.y[line_string]
                # print(len(x), len(y))
                ax.scatter(x=x, y=y, s=100, facecolor="red", alpha=0.5, marker="o", edgecolors='black', linewidths=1, zorder=10)
        # print(len(self.output[:len(self.output_names)]))
        # for item in self.output[:len(self.output_names)]:
        #     print("xx:", len(item), item.shape)
        # print(len(self.colors[:len(self.output_names)]))
        # print(len(["solid"] * len(self.output_names)))
        m.add_subplot(
            y_lists=np.concatenate(self.output[:len(self.output_names)], axis=0),
            x_list=self.t,
            color_list=self.colors[:len(self.output_names)],
            line_style_list=["solid"] * len(self.output_names),
            fig_title="Seven Target Curves",
            legend_list=self.output_names,
            line_width=2,
        )
        m.add_subplot(
            y_lists=np.concatenate(self.output[-len(self.output_names_rest):], axis=0),
            x_list=self.t,
            color_list=self.colors[:len(self.output_names_rest)],
            line_style_list=["solid"] * len(self.output_names_rest),
            fig_title="Rest Curves",
            legend_list=self.output_names_rest,
            line_width=2,
        )
        # plt.suptitle("{} Class ODE Solution".format(self.class_name), fontsize=40)
        m.draw()
        print("Save flag: {}. Figure is saved to {}".format(save_flag, save_path))


def run():
    time_string = get_now_string()
    print("Time String (as folder name): {}".format(time_string))

    class_name = "CN"
    ct = ConstTruth(
        csf_folder_path="data/CSF/",
        pet_folder_path="data/PET/"
    )
    truth = ADSolver(class_name, ct)
    truth.draw(time_string=time_string)


if __name__ == "__main__":
    run()
    # truth.draw()
