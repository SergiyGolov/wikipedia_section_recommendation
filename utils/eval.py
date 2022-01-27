from common import *
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from scipy.stats import kendalltau


def recall_fun(recommended_sections, real_sections):
    return len(set(recommended_sections).intersection(set(real_sections)))/len(real_sections)


def precision_fun(recommended_sections, real_sections):
    return len(set(recommended_sections).intersection(set(real_sections)))/len(recommended_sections)


def plot(x, ys, xlabel, ylabels, ylabel, title, markers, colors, linestyles, ylim=(0, 1), xlim=(1, 20), yticks=None, invert_x=False):
    """
    Plots given x and y data.
    """
    fig, ax = plt.subplots()

    fig.set_figwidth(12)
    fig.set_figheight(8)

    for i in range(len(ys)):
        ax.plot(x, ys[i], label=ylabels[i], marker=markers[i],
                color=colors[i], linestyle=linestyles[i])

    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.set_ylim(ymin=ylim[0], ymax=ylim[1])
    ax.set_xlim(xmin=xlim[0], xmax=xlim[1])

    if invert_x:
        ax.invert_xaxis()

    ax.set_xticks(x)
    if not yticks:
        ax.set_yticks([(i/10)*(ylim[1]-ylim[0])+ylim[0] for i in range(11)])
    else:
        ax.set_yticks(yticks)
    ax.grid()
    ax.legend(loc=9, bbox_to_anchor=(0.5, -0.125))
    plt.show()


def load_results(result_file_name, rec_section_dict_key):
    # rec_section_dict_key="_1" for results provided by initial paper's author, and rec_section_dict_key="section" in our case
    precision = {}
    recall = {}

    for k in range(1, 21):
        precision[k] = []
        recall[k] = []

    with open(result_file_name) as f:
        for line in tqdm(f):
            result_dict = json.loads(line)
            sections = result_dict['sections']
            nb_sections = len(sections)
            recs = [x[rec_section_dict_key] for x in result_dict['recs']]
            for k in range(1, 21):
                precision[k].append(precision_fun(
                    set(recs[:k]), set(sections)))
                recall[k].append(recall_fun(set(recs[:k]), set(sections)))

    return precision, recall


def plot_results(precision, recall, title, min_k=1):

    mean_precision = {}
    mean_recall = {}
    f1_score = {}
    
    for k in range(min_k, 21):
        mean_precision[k] = sum(precision[k])/len(precision[k])
        mean_recall[k] = sum(recall[k])/len(recall[k])
        f1_score[k] = 2*(mean_precision[k]*mean_recall[k]) / \
            (mean_precision[k]+mean_recall[k])

    print("Mean precision")
    for k, v in mean_precision.items():
        print(f"{k}: {round(v,3)}")
    print("\nMean recall")
    for k, v in mean_recall.items():
        print(f"{k}: {round(v,3)}")

    print("\nF1 score")
    for k, v in f1_score.items():
        print(f"{k}: {round(v,3)}")

    x = list(range(min_k, 21))

    ys = [[v for v in mean_precision.values()], [v for v in mean_recall.values()],[v for v in f1_score.values()]]
    xlabel = "Recommendation list length"
    ylabel = "Score"
    ylabels = ["Precision", "Recall",  "F1 score"]
    
    colors = ['tab:blue', 'tab:green', "tab:red"]
    markers = ['s', 's', 's']
    linestyles = ['-', '-', '-']
    print(title)
    plot(x, ys, xlabel, ylabels, ylabel, "", markers, colors, linestyles,xlim=(min_k,20))



def load_epfl_results_and_plot():
    precision, recall = load_results(
        "../data/epfl_paper/recs_probabilistic_by_article.json", "_1")
    plot_results(precision, recall, "Results provided by paper's authors")


def load_results_and_plot(folder_name):
    precision, recall = load_results(
        f"../data/results/{folder_name}/recs_by_article.json", "section")
    plot_results(precision, recall, folder_name)


def load_multiple_results_and_compare_by_metric(folder_names,named_experiments):
    colors = [plt.cm.Set1(i) for i in range(len(folder_names))]
    markers = ['s']*len(folder_names)
    linestyles = ['-']*len(folder_names)

    mean_precision_by_folder = {}
    mean_recall_by_folder = {}
    f1_score_by_folder = {}

    for folder_name in folder_names:
        mean_precision_by_folder[folder_name]={}
        mean_recall_by_folder[folder_name]={}
        f1_score_by_folder[folder_name]={}

        precision, recall = load_results(f"../data/results/{folder_name}/recs_by_article.json", 'section')

        for k in range(1, 21):
            mean_precision_by_folder[folder_name][k] = sum(precision[k])/len(precision[k])
            mean_recall_by_folder[folder_name][k] = sum(recall[k])/len(recall[k])
            f1_score_by_folder[folder_name][k] = 2*(mean_precision_by_folder[folder_name][k]*mean_recall_by_folder[folder_name][k]) / \
                (mean_precision_by_folder[folder_name][k]+mean_recall_by_folder[folder_name][k])

    x = list(range(1, 21))
    ys = [[v for v in mean_precision_by_folder[folder].values()] for folder in folder_names]

    xlabel = "Recommendation list length"
    ylabels = [f"{named_experiment}" for named_experiment in named_experiments]
    ylabel = "Precision"
    plot(x, ys, xlabel, ylabels, ylabel, "Comparing precision between different experiments", markers, colors, linestyles,xlim=(1,20),ylim=(0.1,0.7))

    ys = [[v for v in mean_recall_by_folder[folder].values()] for folder in folder_names]
    ylabel = "Recall"
    plot(x, ys, xlabel, ylabels, ylabel, "Comparing recall between different experiments", markers, colors, linestyles,xlim=(1,20),ylim=(0.2,0.9))

    ys = [[v for v in f1_score_by_folder[folder].values()] for folder in folder_names]
    ylabel = "F1 score"
    plot(x, ys, xlabel, ylabels, ylabel, "Comparing F1 score between different experiments", markers, colors, linestyles,xlim=(1,20),ylim=(0.1,0.5))

def plot_comparison_semantic_levels_same_metric(results_by_semantic_filtering_level):
    min_k=1

    mean_precision_by_sem_lvl = {}
    mean_recall_by_sem_lvl = {}
    f1_score_by_sem_lvl = {}

    for sem_lvl in results_by_semantic_filtering_level.keys():
        mean_precision_by_sem_lvl[sem_lvl]={}
        mean_recall_by_sem_lvl[sem_lvl]={}
        f1_score_by_sem_lvl[sem_lvl]={}
        precision=results_by_semantic_filtering_level[sem_lvl]['precision']
        recall=results_by_semantic_filtering_level[sem_lvl]['recall']
        
        for k in range(min_k, 21):
            
            mean_precision_by_sem_lvl[sem_lvl][k] = sum(precision[k])/len(precision[k])
            mean_recall_by_sem_lvl[sem_lvl][k] = sum(recall[k])/len(recall[k])
            f1_score_by_sem_lvl[sem_lvl][k] = 2*(mean_precision_by_sem_lvl[sem_lvl][k]*mean_recall_by_sem_lvl[sem_lvl][k]) / \
                (mean_precision_by_sem_lvl[sem_lvl][k]+mean_recall_by_sem_lvl[sem_lvl][k])
    
    x = list(range(min_k, 21))
    
    ys = [[v for v in mean_precision_by_sem_lvl[sem_lvl].values()] for sem_lvl in mean_precision_by_sem_lvl.keys()]

    xlabel = "Recommendation list length after filtering"
    ylabels = [f"Semantic filtering level {sem_lvl}" for sem_lvl in f1_score_by_sem_lvl.keys()]
    
    colors = ['crimson','lightskyblue', 'royalblue', "darkblue"]
    markers = ['s']*4
    linestyles = ['-']*4
    ylabel = "Precision"
    plot(x, ys, xlabel, ylabels, ylabel, "Comparing precision between different semantic filtering levels", markers, colors, linestyles,xlim=(min_k,20),ylim=(0.1,0.7))
    
    ys = [[v for v in mean_recall_by_sem_lvl[sem_lvl].values()] for sem_lvl in mean_recall_by_sem_lvl.keys()]
    
    ylabel = "Recall"
    plot(x, ys, xlabel, ylabels, ylabel, "Comparing recall between different semantic filtering levels", markers, colors, linestyles,xlim=(min_k,20),ylim=(0.1,0.8))
    
    ys = [[v for v in f1_score_by_sem_lvl[sem_lvl].values()] for sem_lvl in f1_score_by_sem_lvl.keys()]
    ylabel = "F1-score"
    plot(x, ys, xlabel, ylabels, ylabel, "Comparing f1-score between different semantic filtering levels", markers, colors, linestyles,xlim=(min_k,20),ylim=(0.1,0.5))
        
def load_filtering_results_and_plot(folder_name):

    min_k=1
    results_by_semantic_filtering_level = {}
    nb_sections_after_filtering={}
    for semantic_filtering_level in [0, 1, 2, 3]:
        results_by_semantic_filtering_level[semantic_filtering_level] = {
            'precision': {},
            'recall': {}
        }
        nb_sections_after_filtering[semantic_filtering_level]={}

        for k in range(min_k, 21):
            results_by_semantic_filtering_level[semantic_filtering_level]['precision'][k] = []
            results_by_semantic_filtering_level[semantic_filtering_level]['recall'][k] = []
            nb_sections_after_filtering[semantic_filtering_level][k]=[]


    filtered_result_file_name=f"../data/results/{folder_name}/filtered_recs_by_article.json"
    result_file_name=f"../data/results/{folder_name}/recs_by_article.json"

    results_by_semantic_filtering_level[0]['precision'], results_by_semantic_filtering_level[0]['recall']=load_results(result_file_name, "section")

    with open(filtered_result_file_name, "r", encoding="utf8") as f:
        for line in tqdm(f):
            # one line by test set article
            result_dict = json.loads(line)
            sections = set(result_dict['sections'])
            
            already_evaluated_recs={}

            for filtered_recs in result_dict['filtered_recs']:
                # one element for each semantic filtering level, for each k before filtering (k from 2 to 20)

                initial_k=filtered_recs['k']
                semantic_filtering_level=filtered_recs['semantic_filtering_level']
                if semantic_filtering_level not in already_evaluated_recs.keys():
                    already_evaluated_recs[semantic_filtering_level]=[]

                recs_filtered=filtered_recs['recs_filtered']
                recs_filtered_set=set(recs_filtered)
                k_after_filtering=len(recs_filtered)

                nb_sections_after_filtering[semantic_filtering_level][initial_k].append(k_after_filtering)

                ignore=False
                for already_evaluated_rec in already_evaluated_recs[semantic_filtering_level]:
                    if recs_filtered_set == already_evaluated_rec:
                        ignore=True
                        break
                
                if ignore:
                    continue
                
                results_by_semantic_filtering_level[semantic_filtering_level]['precision'][k_after_filtering].append(precision_fun(recs_filtered_set, sections))
                results_by_semantic_filtering_level[semantic_filtering_level]['recall'][k_after_filtering].append(recall_fun(recs_filtered_set,sections))
                
                already_evaluated_recs[semantic_filtering_level].append(recs_filtered_set)
    
    for semantic_filtering_level in [1, 2, 3]:
        plot_results(results_by_semantic_filtering_level[semantic_filtering_level]['precision'], results_by_semantic_filtering_level[semantic_filtering_level]['recall'], folder_name+" after semantic filtering, semantic filtering level "+str(semantic_filtering_level),min_k=min_k)

    plot_comparison_semantic_levels_same_metric(results_by_semantic_filtering_level)

    print("Number of values used to compute averages")
    for semantic_filtering_level in [0,1,2,3]:
        print(f"semantic_filtering_level {semantic_filtering_level}")
        for k in range(1,21):
            print(f"\t{k}: {len(results_by_semantic_filtering_level[semantic_filtering_level]['precision'][k])}")

    x = list(range(2, 21))

    mean_nb_sections_after_filtering={}

    for semantic_filtering_level in [1, 2, 3]:
        mean_nb_sections_after_filtering[semantic_filtering_level]={}
        for k in range(2,21):
            mean_nb_sections_after_filtering[semantic_filtering_level][k]=sum(nb_sections_after_filtering[semantic_filtering_level][k])/len(nb_sections_after_filtering[semantic_filtering_level][k])

    ys = [list(mean_nb_sections_after_filtering[semantic_filtering_level].values()) for semantic_filtering_level in [1, 2, 3]]
    xlabel = "Recommendation list length before filtering"
    ylabel = "Mean recommendation list length after filtering"
    ylabels = ["semantic filtering level "+str(semantic_filtering_level) for semantic_filtering_level in [1, 2, 3]]
    colors = ['lightskyblue', 'royalblue', "darkblue"]
    markers = ['o']*3
    linestyles = ['-']*3
    title="Mean number of sections after filtering"
    plot(x, ys, xlabel, ylabels, ylabel, title, markers, colors, linestyles,xlim=(2,20),ylim=(2,20),yticks=list(range(2,21)))



def kendall_tau(listA,listB):
    common_items=set(listA).intersection(set(listB))
    listA=[x for x in listA if x in common_items]
    listB=[x for x in listB if x in common_items]

    # this is possible if there are duplicate sections in the ground truth, and one of those duplicate section was in the recommendation list
    # in such a case, both lists don't have the same length
    if len(listA)!=len(listB):
        return None
    
    #transform A B C to 1 2 3 because kendalltau function works only with lists of indexes and not e.g. lists of sections
    section_index_map={}
    for index,section in enumerate(listA):
        section_index_map[section]=index
        
    listA=[section_index_map[section] for section in listA]
    listB=[section_index_map[section] for section in listB]
    
    tau,_=kendalltau(listA,listB)
    return tau

def get_mean_tau_ordering_results(folder_name,ignore_context=False,ignore_end_order_value=False):
    file_name="ordered_recs_by_article"
    if ignore_context:
        file_name+="_ignore_context"
    if ignore_end_order_value:
        file_name+="_ignore_end_order_value"
    ordered_sections_result_file_name=f"../data/results/{folder_name}/{file_name}.json"

    taus_after_ordering_by_semantic_filtering_level={}
    taus_before_ordering_by_semantic_filtering_level={}
    for semantic_filtering_level in range(4):
        taus_after_ordering_by_semantic_filtering_level[semantic_filtering_level]=[]
        taus_before_ordering_by_semantic_filtering_level[semantic_filtering_level]=[]

    with open(ordered_sections_result_file_name, "r", encoding="utf8") as f:
        for line in f:
            result_dict = json.loads(line)
            sections=result_dict['sections']
            for ordered_recs_result,unordered_recs_result in zip(result_dict['ordered_recs'],result_dict['unordered_recs']):
                semantic_filtering_level=ordered_recs_result['semantic_filtering_level']
                ordered_recs=[x['section'] for x in ordered_recs_result['recs']]
                unordered_recs=unordered_recs_result['recs']

                if len(set(sections).intersection(set(unordered_recs)))<2:
                    continue

                tau_before=kendall_tau(sections,unordered_recs)
                if not tau_before:
                    continue
                tau_after=kendall_tau(sections,ordered_recs)

                taus_before_ordering_by_semantic_filtering_level[semantic_filtering_level].append(tau_before)
                taus_after_ordering_by_semantic_filtering_level[semantic_filtering_level].append(tau_after)

    result={}
    for semantic_filtering_level in range(4):
        result[semantic_filtering_level]={}
        result[semantic_filtering_level]['nb_values']=len(taus_after_ordering_by_semantic_filtering_level[semantic_filtering_level])
        result[semantic_filtering_level]['mean_tau_before_ordering']=sum(taus_before_ordering_by_semantic_filtering_level[semantic_filtering_level])/len(taus_before_ordering_by_semantic_filtering_level[semantic_filtering_level])
        result[semantic_filtering_level]['mean_tau_after_ordering']=sum(taus_after_ordering_by_semantic_filtering_level[semantic_filtering_level])/len(taus_after_ordering_by_semantic_filtering_level[semantic_filtering_level])
        

    return result


