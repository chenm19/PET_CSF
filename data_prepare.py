# import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import pickle
import os

from data_prepare_const import *


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
        counts[LABEL_ID[label]] += 1
        for i in range(3):
            collection[LABEL_ID[label]][i] += float(row[COLUMN_NAMES_CSF[i]])
    for one_key in LABELS:
        if counts[LABEL_ID[one_key]] != 0:
            avg = collection[LABEL_ID[one_key], :] / counts[LABEL_ID[one_key]]
            np.save("data/CSF/CSF_{}".format(one_key), avg)
    print(counts)

if __name__ == "__main__":
    # one_time_deal_PET()
    # d = one_time_build_ptid_dictionary()
    one_time_deal_CSF()
    pass
