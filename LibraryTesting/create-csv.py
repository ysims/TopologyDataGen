low_30_ripser = [
    "./data/30-low/1_stats_ripser.txt",
    "./data/30-low/2_stats_ripser.txt",
    "./data/30-low/3_stats_ripser.txt",
    "./data/30-low/4_stats_ripser.txt",
    "./data/30-low/5_stats_ripser.txt",
]

high_30_ripser = [
    "./data/30-high/6_stats_ripser.txt",
    "./data/30-high/7_stats_ripser.txt",
    "./data/30-high/8_stats_ripser.txt",
    "./data/30-high/9_stats_ripser.txt",
    "./data/30-high/10_stats_ripser.txt",
]

low_50_ripser = [
    "./data/50-sub-low/11_stats_ripser.txt",
    "./data/50-sub-low/12_stats_ripser.txt",
    "./data/50-sub-low/13_stats_ripser.txt",
    "./data/50-sub-low/14_stats_ripser.txt",
    "./data/50-sub-low/15_stats_ripser.txt",
]

high_50_ripser = [
    "./data/50-sub-high/16_stats_ripser.txt",
    "./data/50-sub-high/17_stats_ripser.txt",
    "./data/50-sub-high/18_stats_ripser.txt",
    "./data/50-sub-high/19_stats_ripser.txt",
    "./data/50-sub-high/20_stats_ripser.txt",
]

low_30_gudhi_vr = [
    "./data/30-low/1_stats_gudhi_vr.txt",
    "./data/30-low/2_stats_gudhi_vr.txt",
    "./data/30-low/3_stats_gudhi_vr.txt",
    "./data/30-low/4_stats_gudhi_vr.txt",
    "./data/30-low/5_stats_gudhi_vr.txt",
]

high_30_gudhi_vr = [
    "./data/30-high/6_stats_gudhi_vr.txt",
    "./data/30-high/7_stats_gudhi_vr.txt",
    "./data/30-high/8_stats_gudhi_vr.txt",
    "./data/30-high/9_stats_gudhi_vr.txt",
    "./data/30-high/10_stats_gudhi_vr.txt",
]

low_50_gudhi_vr = [
    "./data/50-sub-low/11_stats_gudhi_vr.txt",
    "./data/50-sub-low/12_stats_gudhi_vr.txt",
    "./data/50-sub-low/13_stats_gudhi_vr.txt",
    "./data/50-sub-low/14_stats_gudhi_vr.txt",
    "./data/50-sub-low/15_stats_gudhi_vr.txt",
]

high_50_gudhi_vr = [
    "./data/50-sub-high/16_stats_gudhi_vr.txt",
    "./data/50-sub-high/17_stats_gudhi_vr.txt",
    "./data/50-sub-high/18_stats_gudhi_vr.txt",
    "./data/50-sub-high/19_stats_gudhi_vr.txt",
    "./data/50-sub-high/20_stats_gudhi_vr.txt",
]

low_30_gudhi_alpha = [
    "./data/30-low/1_stats_gudhi_alpha.txt",
    "./data/30-low/2_stats_gudhi_alpha.txt",
    "./data/30-low/3_stats_gudhi_alpha.txt",
    "./data/30-low/4_stats_gudhi_alpha.txt",
    "./data/30-low/5_stats_gudhi_alpha.txt",
]

high_30_gudhi_alpha = [
    "./data/30-high/6_stats_gudhi_alpha.txt",
    "./data/30-high/7_stats_gudhi_alpha.txt",
    "./data/30-high/8_stats_gudhi_alpha.txt",
    "./data/30-high/9_stats_gudhi_alpha.txt",
    "./data/30-high/10_stats_gudhi_alpha.txt",
]

low_50_gudhi_alpha = [
    "./data/50-sub-low/11_stats_gudhi_alpha.txt",
    "./data/50-sub-low/12_stats_gudhi_alpha.txt",
    "./data/50-sub-low/13_stats_gudhi_alpha.txt",
    "./data/50-sub-low/14_stats_gudhi_alpha.txt",
    "./data/50-sub-low/15_stats_gudhi_alpha.txt",
]

high_50_gudhi_alpha = [
    "./data/50-sub-high/16_stats_gudhi_alpha.txt",
    "./data/50-sub-high/17_stats_gudhi_alpha.txt",
    "./data/50-sub-high/18_stats_gudhi_alpha.txt",
    "./data/50-sub-high/19_stats_gudhi_alpha.txt",
    "./data/50-sub-high/20_stats_gudhi_alpha.txt",
]

ripser = [low_30_ripser, high_30_ripser, low_50_ripser, high_50_ripser]
gudhi_vr = [low_30_gudhi_vr, high_30_gudhi_vr, low_50_gudhi_vr, high_50_gudhi_vr]
gudhi_alpha = [
    low_30_gudhi_alpha,
    high_30_gudhi_alpha,
    low_50_gudhi_alpha,
    high_50_gudhi_alpha,
]

low_30_gudhi_alpha_mem = []
low_30_gudhi_alpha_time = []
high_30_gudhi_alpha_mem = []
high_30_gudhi_alpha_time = []
low_50_gudhi_alpha_mem = []
low_50_gudhi_alpha_time = []
high_50_gudhi_alpha_mem = []
high_50_gudhi_alpha_time = []


for stats in low_30_gudhi_alpha:
    with open(stats) as f:
        temp = f.read().splitlines()
        low_30_gudhi_alpha_mem.append(temp[0])
        low_30_gudhi_alpha_time.append(temp[1])

for stats in high_30_gudhi_alpha:
    with open(stats) as f:
        temp = f.read().splitlines()
        high_30_gudhi_alpha_mem.append(temp[0])
        high_30_gudhi_alpha_time.append(temp[1])

for stats in low_50_gudhi_alpha:
    with open(stats) as f:
        temp = f.read().splitlines()
        low_50_gudhi_alpha_mem.append(temp[0])
        low_50_gudhi_alpha_time.append(temp[1])

for stats in high_50_gudhi_alpha:
    with open(stats) as f:
        temp = f.read().splitlines()
        high_50_gudhi_alpha_mem.append(temp[0])
        high_50_gudhi_alpha_time.append(temp[1])


import csv

with open("gudhi_alpha.csv", "w", newline="") as csvfile:
    datawriter = csv.writer(csvfile)
    datawriter.writerow(low_30_gudhi_alpha_mem + low_30_gudhi_alpha_time)
    datawriter.writerow(high_30_gudhi_alpha_mem + high_30_gudhi_alpha_time)
    datawriter.writerow(low_50_gudhi_alpha_mem + low_50_gudhi_alpha_time)
    datawriter.writerow(high_50_gudhi_alpha_mem + high_50_gudhi_alpha_time)
