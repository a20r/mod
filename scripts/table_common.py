pm = " \\pm "

table_header = """
\\begin{table*}[t]
\\centering
\\begin{tabular}{  |c|c|c|c|c|c|c|c| }
\\hline
& Fleet size & Capacity $\\nu$ & Pick-ups/h & Ignored/h & Waiting time [s] & Delay [s] & Occupancy \\\\
\\hline
\\hline
"""

line_tp = "{} & {} & {} & {:.2f} $\\pm$ {:.2f} & {:.2f} $\\pm$ {:.2f} & {:.2f} $\\pm$ {:.2f} & {:.2f} $\\pm$ {:.2f} & {:.2f} $\\pm$ {:.2f} \\\\"

table_footer = """
\hline
\\end{tabular}
\\caption{Experimental results with varying number of vehicles and capacity for the middle area of Manhattan and XX mean requests per hour.}
\\label{tab:1}
\\end{table*}
"""
