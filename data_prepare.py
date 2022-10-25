# import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import pickle
import os

from data_prepare_const import *
from utils import MultiSubplotDraw

def one_time_deal_PET(data_path_list=None):
    if not data_path_list:
        data_path_list = ["data/271amyloid.csv", "data/271tau.csv", "data/271fdg.csv"]
    data_a = pd.read_csv(data_path_list[0])
    data_t = pd.read_csv(data_path_list[1])
    data_n = pd.read_csv(data_path_list[2])
    data_a = data_a[COLUMN_NAMES + TITLE_NAMES]
    data_t = data_t[COLUMN_NAMES + TITLE_NAMES]
    data_n = data_n[COLUMN_NAMES + TITLE_NAMES]

    class_number = 5

    for type_name, df in zip(["PET-A", "PET-T", "PET-N"], [data_a, data_t, data_n]):
        save_path = "data/PET/{}_{{}}.npy".format(type_name)
        collection = np.zeros((class_number, 160))
        counts = np.zeros(class_number)
        for index, row in df.iterrows():
            label = None
            for one_key in LABELS:
                if row["DX"] in LABELS[one_key]:
                    label = one_key
                    counts[LABEL_ID[label]] += 1
                    break

            if not label:
                # print("key not found: \"{}\"".format(row["DX"]))
                continue
            for i in range(160):
                collection[LABEL_ID[label]][i] += float(row[COLUMN_NAMES[i]])
        for one_key in LABELS:
            if counts[LABEL_ID[one_key]] != 0:
                avg = collection[LABEL_ID[one_key], :] / counts[LABEL_ID[one_key]]
                # print(type_name, "avg({})".format(collection[LABEL_ID[one_key], :].shape))
                np.save(save_path.format(one_key), avg)
                print(one_key, np.mean(avg))
        print(type_name, "counts:", counts)


def one_time_deal_PET_all(data_path_list=None):
    if not data_path_list:
        data_path_list = ["data/Amyloid_Full.xlsx", "data/FDG_Full.xlsx"]
    full_names = ["Node {}".format(i) for i in range(1, 161)]
    data_a = pd.read_excel(data_path_list[0])
    # data_t = pd.read_csv(data_path_list[1])
    data_n = pd.read_excel(data_path_list[1])
    data_a = data_a[full_names + TITLE_NAMES]
    # data_t = data_t[COLUMN_NAMES + TITLE_NAMES]
    data_n = data_n[full_names + TITLE_NAMES]

    class_number = 5

    for type_name, df in zip(["PET-A", "PET-N"], [data_a, data_n]):
        save_path = "data/PET/{}_full_{{}}.npy".format(type_name)
        collection = np.zeros((class_number, 160))
        counts = np.zeros(class_number)
        for index, row in df.iterrows():
            label = None
            for one_key in LABELS:
                if row["DX"] in LABELS[one_key]:
                    label = one_key
                    counts[LABEL_ID[label]] += 1
                    break

            if not label:
                print("key not found: \"{}\"".format(row["DX"]))
                continue
            for i in range(160):
                collection[LABEL_ID[label]][i] += float(row[full_names[i]])
        for one_key in LABELS:
            if counts[LABEL_ID[one_key]] != 0:
                avg = collection[LABEL_ID[one_key], :] / counts[LABEL_ID[one_key]]
                # print(type_name, "avg({})".format(collection[LABEL_ID[one_key], :].shape))
                np.save(save_path.format(one_key), avg)
                print(one_key, np.mean(avg))
        print(type_name, "counts:", counts)

def one_time_build_ptid_dictionary(dictionary_path=None):
    if not dictionary_path:
        dictionary_path = "data/MRI_information_All_Measurement.xlsx"
    df = pd.read_excel(dictionary_path)[["PTID", "DX"]]
    dic = dict()
    for index, row in df.iterrows():
        if len(row["PTID"]) < 2:
            continue
        ptid = row["PTID"].split("_")[-1]
        assert len(ptid) == 4
        dx = row["DX"]
        if dx not in LABELS and str(dx) != "nan":
            print("DX: \"{}\" not matches any!".format(dx))
            continue
        dic[ptid] = dx
    with open("data/CSF/ptid_dictionary.pkl", "wb") as f:
        pickle.dump(dic, f)
    return dic


def one_time_deal_CSF(csf_path=None, dictionary_pickle_path=None):
    if not csf_path:
        csf_path = "data/CSF_Bio_All_WF.csv"
    if not dictionary_pickle_path:
        dictionary_pickle_path = "data/CSF/ptid_dictionary.pkl"
    with open(dictionary_pickle_path, "rb") as f:
        ptid_dic = pickle.load(f)
    df = pd.read_csv(csf_path)[["RID", "ABETA", "TAU", "PTAU"]]
    class_list = list(LABELS.keys())
    counts = np.zeros(len(class_list))
    collection = np.zeros([len(class_list), 3])

    for index, row in df.iterrows():
        ptid_key = str(int(row["RID"])).zfill(4)
        if ptid_key not in ptid_dic:
            print("ptid key {} not found! Skip it!".format(ptid_key))
            continue
        label = ptid_dic[ptid_key]
        if not (np.isnan(row[COLUMN_NAMES_CSF[0]]) or np.isnan(row[COLUMN_NAMES_CSF[1]]) or np.isnan(row[COLUMN_NAMES_CSF[2]])):
            counts[LABEL_ID[label]] += 1
            for i in range(3):
                collection[LABEL_ID[label]][i] += float(row[COLUMN_NAMES_CSF[i]])
    for one_key in LABELS:
        if counts[LABEL_ID[one_key]] != 0:
            avg = collection[LABEL_ID[one_key], :] / counts[LABEL_ID[one_key]]
            np.save("data/CSF/CSF_{}".format(one_key), avg)
            print("CSF_{} counts={} avg={}".format(one_key, counts[LABEL_ID[one_key]], avg))
    print("CSF counts:", counts)


def percent_diff(base, data):
    diff = (data - base) / base
    diff_min = np.min(diff)
    diff_max = np.max(diff)
    diff_avg = np.mean(diff)
    diff_string = "min: {0}{1:.1f}%, avg: {2}{3:.1f}%, max: {4}{5:.1f}%".format(
        "+" if diff_min > 0 else "",
        diff_min * 100,
        "+" if diff_avg > 0 else "",
        diff_avg * 100,
        "+" if diff_max > 0 else "",
        diff_max * 100,
    )
    return diff_string


def one_time_compare(data_name_1, data_name_2, legend_format_list, title, path_format="data/PET/{}_{}.npy"):
    label_list = LABEL_LIST

    m = MultiSubplotDraw(row=5, col=1, fig_size=(25, 30), show_flag=True, save_flag=False, tight_layout_flag=False, title=title, title_size=40)
    for one_label in label_list:
        data1 = np.load(path_format.format(data_name_1, one_label))
        data2 = np.load(path_format.format(data_name_2, one_label))
        diff = percent_diff(data1, data2)
        m.add_subplot(
            y_lists=[data1, data2],
            x_list=range(1, 161),
            color_list=["r", "b"],
            legend_list=[item.format(one_label) for item in legend_format_list],
            line_style_list=["solid"] * 2,
            fig_title="{} ({})".format(one_label, diff),
        )

    m.draw()


if __name__ == "__main__":
    # one_time_deal_PET()
    # d = one_time_build_ptid_dictionary()
    # one_time_deal_CSF()
    # one_time_deal_PET()
    # one_time_deal_PET_all()
    one_time_compare("PET-A_full", "PET-A", ["PET-A_full_{}", "PET-A_{}"], "PET_A")
    one_time_compare("PET-N_full", "PET-N", ["PET-N_full_{}", "PET-N_{}"], "PET_N")
    pass
