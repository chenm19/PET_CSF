import os

import matplotlib.pyplot as plt
import numpy as np

import time
from scipy.integrate import odeint
from tqdm import tqdm

from parameters import *
from config import Start, Config
from utils import MultiSubplotDraw


def get_now_string():
    return time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))


class ADTruth:
    def __init__(self, class_name):
        self.n = Config.N_dim
        self.L = Config.L
        self.t = np.linspace(0, 10 - 0.1, 100)
        self.class_name = class_name
        self.y0 = Start(class_name).all
        # print("ODE size: {}".format(self.y0.shape))
        self.y = odeint(self.pend, self.y0, self.t)
        self.output = self.get_output()
        # print("output has {} curves".format(len(self.output)))
        self.output_names = ["$A_{PET}$", "$T_{PET}$", "$N_{PET}$", "$A_{CSF}$", "$T_{pCSF}$", "$T_{CSF}$", "$T_{tCSF}$"]
        self.output_names_rest = ["$A_{o}Sum$", "$T_{o}Sum$"]
        self.colors = ["red", "green", "blue", "cyan", "orange", "purple", "brown", "gray", "olive"]

    def get_output(self):
        Am = self.y[:, 0: self.n]
        Ao = self.y[:, self.n: self.n * 2]
        Af = self.y[:, self.n * 2: self.n * 3]
        Tm = self.y[:, self.n * 3 + 1: self.n * 4 + 1]
        Tp = self.y[:, self.n * 4 + 1: self.n * 5 + 1]
        To = self.y[:, self.n * 5 + 1: self.n * 6 + 1]
        Tf = self.y[:, self.n * 6 + 1: self.n * 7 + 1]
        N = self.y[:, self.n * 7 + 3: self.n * 8 + 3]

        ACSF = np.expand_dims(k_sA * np.sum(Am, axis=1), axis=0)
        TCSF = np.expand_dims(k_sT * np.sum(Tm, axis=1), axis=0)
        TpCSF = np.expand_dims(k_sTp * np.sum(Tp, axis=1), axis=0)
        APET = np.swapaxes(Af, 0, 1)
        TPET = np.swapaxes(Tf, 0, 1)
        NPET = np.swapaxes(N, 0, 1)
        TtCSF = TpCSF + TCSF
        Ao_sum = np.expand_dims(np.sum(Ao, axis=1), axis=0)
        To_sum = np.expand_dims(np.sum(To, axis=1), axis=0)
        APET_average = np.expand_dims(np.mean(APET, axis=0), axis=0)
        TPET_average = np.expand_dims(np.mean(TPET, axis=0), axis=0)
        NPET_average = np.expand_dims(np.mean(NPET, axis=0), axis=0)
        # return [APET, TPET, NPET, ACSF, TpCSF, TCSF, TtCSF, Ao_sum, To_sum]
        return [APET_average, TPET_average, NPET_average, ACSF, TpCSF, TCSF, TtCSF, Ao_sum, To_sum]

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
        m = MultiSubplotDraw(row=3, col=3, fig_size=(24, 20), tight_layout_flag=True, show_flag=True, save_flag=save_flag,
                             save_path=save_path, save_dpi=400)
        for name, data, color in zip(self.output_names, self.output[:len(self.output_names)], self.colors[:len(self.output_names)]):

            m.add_subplot(
                y_lists=data,
                x_list=self.t,
                color_list=[color],
                line_style_list=["solid"],
                fig_title=name,
                legend_list=[name],
                line_width=2
            )
        # print(len(self.output[:len(self.output_names)]))
        # print(len(self.colors[:len(self.output_names)]))
        # print(len(["solid"] * len(self.output_names)))
        m.add_subplot(
            y_lists=np.concatenate(self.output[:len(self.output_names)], axis=0),
            x_list=self.t,
            color_list=self.colors[:len(self.output_names)],
            line_style_list=["solid"] * len(self.output_names),
            fig_title="Seven Curves in all",
            legend_list=self.output_names,
            line_width=2
        )
        m.add_subplot(
            y_lists=np.concatenate(self.output[-len(self.output_names_rest):], axis=0),
            x_list=self.t,
            color_list=self.colors[:len(self.output_names_rest)],
            line_style_list=["solid"] * len(self.output_names_rest),
            fig_title="Rest Curves in all",
            legend_list=self.output_names_rest,
            line_width=2
        )
        plt.suptitle("{} Class ODE Solution".format(self.class_name), fontsize=40)
        m.draw()
        print("Save flag: {}. Figure is saved to {}".format(save_flag, save_path))


def run():
    time_string = get_now_string()
    print("Time String (as folder name): {}".format(time_string))
    for one_class_name in tqdm(["CN", "SMC", "EMCI", "LMCI", "AD"]):
        truth = ADTruth(one_class_name)
        truth.draw(time_string=time_string)


if __name__ == "__main__":
    run()
    # truth.draw()
