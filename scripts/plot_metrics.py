
import numpy as np
import seaborn as sns
import pandas

table_header = """
\\begin{table*}[t]
\\centering
\\begin{tabular}{  |c|c|c|c|c|c|c|c| }
\\hline
& Fleet size & Capacity $\\nu$ & Pick-ups/h & Ignored/h & Waiting time [s] & Delay [s] & Occupancy \\
\\hline
\\hline
"""
# 1    &      &  &  & & & & \\
# \hline
# 2    &      &  &  & & & & \\
# \hline
# 3    &      &  &  & & & & \\
# \hline

line_tp = "{} & {} & {} & {} & {} & {} & {} & {} \\\\"


table_footer = """
\hline
\\end{tabular}
\\caption{Experimental results with varying number of vehicles and capacity for the middle area of Manhattan and XX mean requests per hour.}
\\label{tab:1}
\\end{table*}
"""

instances = [(500, 1), (500, 2), (500, 3), (500, 4),
             (125, 4), (250, 4), (375, 4), (625, 4),
             (750, 4), (1000, 4), (500, 4)]


def create_latex_table(df):
    lines = list()
    for i, (n_vecs, cap) in enumerate(instances):
        st = subtable(df, n_vecs, cap)
        pickups = np.mean(st["n_pickups"])
        ignored = np.mean(st["n_ignored"])
        waiting_time = np.mean(st["mean_waiting_time"])
        delay = np.mean(st["mean_delay"])
        occupancy = np.mean(st["mean_passengers"])
        line = line_tp.format(
            i, n_vecs, cap, pickups, ignored,
            waiting_time, delay, occupancy)
        lines.append(line)
    inner_lines = "\n\\hline\n".join(line for line in lines)
    return table_header + inner_lines + table_footer


def subtable(df, n_vecs, cap):
    return df[(df["capacity"] == cap) & (df["n_vehicles"] == n_vecs)]


if __name__ == "__main__":
    sns.set_context("poster")
    df = pandas.read_csv("data/metrics.csv")
    print create_latex_table(df)
