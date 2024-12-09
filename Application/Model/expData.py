import matplotlib.pyplot as plt # Math plotting library


#%% Plotting gathered experiment data - summary



def plot_summary(avg_accs, avg_confs, clrs, lbls, accs=0, accs2=0, accs3=0
                 , avg_conf=0, avg_confs2=0, avg_confs3=0):
    plt.figure(dpi=600)
    eps = range(1,len(avg_accs)+1)

    if accs == 0:
        plt.plot(eps, avg_accs,'black', label="Test Accuracy")
        for x in range(len(avg_accs)):
            plt.vlines(x=(x+1), ymin=avg_confs[x][0], ymax=avg_confs[x][1],
                       colors='b', ls='-', lw=2, label="Conf. Interval")  
            plt.scatter(x=(x+1), y=avg_accs[x], marker="o", color=clrs[x],
                        zorder=4, label=lbls[x])
    elif isinstance(accs, list):
        plt.plot(eps, accs,'black', label="Test Acc. Baseline")
        plt.plot(eps, accs2,'brown', label="Test Acc. w/ 3* POS")
        plt.plot(eps, accs3,'orange', label="Test Acc. w/ 3* NEG")
        for x in range(len(avg_accs)):
            plt.vlines(x=(x+1), ymin=avg_conf[x][0], ymax=avg_conf[x][1],
                       colors='b', ls='-', lw=2, label="Conf. Interval")  
            plt.scatter(x=(x+1), y=avg_accs[x], marker="o", color=clrs[x],
                        zorder=4, label=lbls[x])
        for x in range(len(avg_accs)):
            plt.vlines(x=(x+1), ymin=avg_confs2[x][0], ymax=avg_confs2[x][1],
                       colors='b', ls='-', lw=2, label="Conf. Interval")  
            plt.scatter(x=(x+1), y=avg_accs2[x], marker="o", color=clrs[x],
                        zorder=4, label=lbls[x])
        for x in range(len(avg_accs)):
            plt.vlines(x=(x+1), ymin=avg_confs3[x][0], ymax=avg_confs3[x][1],
                       colors='b', ls='-', lw=2, label="Conf. Interval")  
            plt.scatter(x=(x+1), y=avg_accs3[x], marker="o", color=clrs[x],
                        zorder=4, label=lbls[x])
        
    
    plt.legend()
    clear_plot_lbl_duplicates()
    plt.ylabel("Acc. %")
    plt.xlabel("Experiment No.")
    plt.show()
    
def clear_plot_lbl_duplicates():
    # Hold unique vals
    # https://stackoverflow.com/questions/13588920/stop-matplotlib-repeating-labels-in-legend
    h_, l_ = [], []
    # Get plt values
    h, l = plt.gca().get_legend_handles_labels()
    # remove duplicates
    for hx, lx in zip(h, l):
      if lx not in l_:
        l_.append(lx)
        h_.append(hx)
    plt.legend(h_, l_, bbox_to_anchor=(1.05, 1), loc="upper left")
  
    
# Baseline - No 3* in training
# 5* pos, 4* pos, 3* pos, 3* neg, 2* neg, 1* neg - avg accuracies
avg_accs = [82.54, 74.0, 47.63, 51.60, 72.95, 84.55]
avg_confs = [[80.69, 84.39],[70.12, 77.86],[45.19, 50.06],
                 [49.16, 54.03],[70.78, 75.11],[82.79, 86.31]]

# Baseline - 3* as POS in training
# 5* pos, 4* pos, 3* pos, 3* neg, 2* neg, 1* neg - avg accuracies
avg_accs2 = [83.36, 78.07, 59.14, 41.29, 62.92, 80.78]
avg_confs2 = [[81.55, 85.18],[74.42, 81.72],[56.74, 61.54],
                 [38.89, 43.70],[60.56, 65.28],[78.86, 82.71]]

# Baseline - 3* as NEG in training
# 5* pos, 4* pos, 3* pos, 3* neg, 2* neg, 1* neg - avg accuracies
avg_accs3 = [79.24, 66.47, 39.21, 61.65, 75.24, 84.68]
avg_confs3 = [[77.26, 81.22],[62.31, 70.63],[36.83, 41.59],
                 [59.28, 64.02],[73.13, 77.34],[82.92, 86.43]]

# Model Accs
avg_accs_m = [78.62, 76.46, 76.56]
avg_confs_m = [[76.62, 80.62],[74.39, 78.53],[74.49, 78.63]]
lbls_m = ["Test Acc. Model no 3*", "Test Acc. Model w/ 3* POS", "Test Acc. Model w/ 3* NEG"]
clrs_m = ["red", "darkred", "lime"]

clrs = ["red", "darkred", "lime", "green", "yellow", "gold"]
lbls = ["5* POS in test set", "4* POS in test set", "3* POS in test set",
        "3* NEG in test set", "2* NEG in test set", "1* NEG in test set"]


#plot_summary(avg_accs, avg_confs, clrs, lbls, avg_accs, avg_accs2, avg_accs3,
             #avg_confs, avg_confs2, avg_confs3)
#plot_summary(avg_accs, avg_confs, clrs, lbls)
#plot_summary(avg_accs2, avg_confs2, clrs, lbls)
#plot_summary(avg_accs3, avg_confs3, clrs, lbls)

plot_summary(avg_accs_m, avg_confs_m, clrs_m, lbls_m)



