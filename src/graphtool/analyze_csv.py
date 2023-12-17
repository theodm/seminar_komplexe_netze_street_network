
# read csv into pandas dataframe

import pandas as pd

# read csv in data/graphs/graph_infos.csv first line are headers
df = pd.read_csv("data/graphs/graph_infos.csv")

# print first 5 lines
print(df.head())

# matplotlib show scatter plot
# x axis: flaeche
# y axis: diameter
# label: name

import matplotlib.pyplot as plt

plt.scatter(df["flaeche"], df["avg_path_length_tt"], label=df["name"])
plt.xlabel("flaeche")
plt.ylabel("avg_path_length")

# f, diagram = plt.subplots(1)
#
# for i, e in df.iterrows():
#     diagram.plot(e["flaeche"], e["avg_path_length_tt"], 'bo')
#     plt.text(e["flaeche"] * (1 + 0.01), e["avg_path_length_tt"] * (1 + 0.01), e["name"], fontsize=12)

plt.show()