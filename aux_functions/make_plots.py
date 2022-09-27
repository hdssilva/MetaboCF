import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from aux_functions.name_2lines import name_2lines
from sklearn.metrics import confusion_matrix
from matplotlib import rcParams

def plot_confusion_matrix(y_true, y_pred, labels, font_scale=1, figsize=(5,5), annot=False, annot_size = rcParams['font.size'], dpi=800,
                          title=None,
                          title_size=None, y_pos_title=1, save_dir=None, transparent=True, cbar_kws={"shrink": .70, "pad":0.02},
                          label_size=None, ticklabels_size=None, xticklabel_rotation=None, yticklabel_rotation=90, x_ha='center',
                          x_va='center', y_ha='center', y_va='center'):
    sns.set_theme(font_scale=font_scale)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_title(title, y=y_pos_title, size=title_size)
    
    cf= confusion_matrix(y_true, y_pred, labels=labels)
    cf_normalized = cf / cf.sum(axis=1)[:, np.newaxis]
    cf_normalized = np.nan_to_num(cf_normalized)
    if annot:
        group_counts = ["{0:0.0f}".format(value) for value in cf.flatten()]
        group_percentages = ["{0:.2%}".format(value) for value in cf_normalized.flatten()]
        box_labels = [f"{v2}\n{v1}".strip() for v1, v2 in zip(group_counts,group_percentages)]
        box_labels = np.asarray(box_labels).reshape(cf.shape[0],cf.shape[1])
        sns.heatmap(cf_normalized, annot=box_labels, annot_kws= {"size": annot_size}, fmt="", cmap='Blues', 
                    xticklabels=name_2lines(labels), yticklabels=name_2lines(labels), cbar_kws=cbar_kws)
    else:
        sns.heatmap(cf_normalized, fmt="", cmap='Blues', xticklabels=name_2lines(labels), 
                     yticklabels=name_2lines(labels), cbar_kws=cbar_kws)
    ax.set_xlabel('Predicted label', fontsize=label_size)
    ax.set_ylabel('True label', fontsize=label_size)
    plt.setp(ax.xaxis.get_majorticklabels(), ha=x_ha, va=x_va, fontsize = ticklabels_size, rotation=xticklabel_rotation)
    plt.setp(ax.yaxis.get_majorticklabels(), ha=y_ha, va=y_va, fontsize = ticklabels_size, rotation=yticklabel_rotation)
    if save_dir is not None:
        plt.savefig(save_dir, bbox_inches='tight', transparent=transparent)
    plt.show()
    
class OOMFormatter(matplotlib.ticker.ScalarFormatter):
    def __init__(self, order=0, fformat='%1.1f', offset=True, mathText=True):
        self.oom = order
        self.fformat = fformat
        matplotlib.ticker.ScalarFormatter.__init__(self,useOffset=offset,useMathText=mathText)
    def _set_order_of_magnitude(self):
        self.orderOfMagnitude = self.oom
    def _set_format(self, vmin=None, vmax=None):
        self.format = self.fformat
        if self._useMathText:
            self.format = r'$\mathdefault{%s}$' % self.format