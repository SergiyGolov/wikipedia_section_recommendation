# this file was adapted from filter_semantic_similar_sections function in wikipedia_section_recommendation_prototype/server/app.py file
# therefore we have replaced mongodb calls with get_XXX functions which loads data from disk once and keeps it in memory
# because we don't know in advance which category communites will be present, we load them one by one when needed for each new encountered
# category community

# the idea of the semantic filtering on the whole dataset is to avoid to load each time the semantic similar pairs for k=2 to 20
# for each semantic filtering level for each article and build a semantic similar section graph each time,
# but instead build one graph for each article for each semantic filtering level, by beginning with k=2 and then for k=3 to 20,
# we add new edges in the similarity graph if the section introduced with the new k is present in semantic similar pairs for the current
# semantic filtering level in the current category community
# otherwise it would take hundreds of hours to apply the semantic filtering over the whole dataset, now it takes "only" 7-8 hours

# "sentences" in this file corresponds to "section contents" in the report

from common import *
import community as community_louvain
import networkx as nx
import re
import nltk
from collections import Counter
pattern_non_letters = re.compile('[\W_0-9]+')
sno = nltk.stem.SnowballStemmer('english')
stopwords = set(nltk.corpus.stopwords.words('english'))

# these are the default minimum cosine similarity thresholds for each semantic filtering level
# based on 3-quantiles over cosine sim distribution among all category communities
semantic_filtering_level_default_min_cosine_sim_map = {
    1: 0.6228756904602051,
    2: 0.554182292450042,
    3: 0.5,
}

category_community={}

def load_files_in_memory():
    # we load at beginning those files because we're sure that they will be needed
    print("\tLoading files in memory")
    processed_communities=set()
    with open(f"../data/semantic_similarity/processed_communities", "r", encoding="utf8") as f_in:
        for line in f_in:
            processed_communities.add(int(line))
    
    with open("../data/categories_splitted_into_communities.json", "r", encoding="utf8") as f_in:
        for line in f_in:
            json_line=json.loads(line)
            community_id=json_line['community_id']
            if community_id not in processed_communities:
                continue
            categories=json_line['categories']
            for category in categories:
                category_community[category]=community_id

cosine_sim_thresholds_by_community={}

def get_cosine_sim_thresholds_by_community(community_id):
    if community_id not in cosine_sim_thresholds_by_community.keys():
        try:
            with open(f"../data/semantic_similarity/community_{community_id}/cosine_sim_thresholds.json", "r", encoding="utf8") as f_in:
                cosine_sim_thresholds_by_community[community_id]=[]
                for line in f_in:
                    json_line=json.loads(line)
                    cosine_sim_thresholds_by_community[community_id].append(json_line)
        except FileNotFoundError:
            cosine_sim_thresholds_by_community[community_id]=None

    return cosine_sim_thresholds_by_community[community_id]

sentence_counter_by_section_by_community={}

def get_sentence_counter_by_section_by_community(section,community_id):
    # gets count of unique sentences for given section in given category community
    if community_id not in sentence_counter_by_section_by_community.keys():
        sentence_counter_by_section_by_community[community_id]={}
        with open(f"../data/semantic_similarity/community_{community_id}/sentence_counter_by_section.json", "r", encoding="utf8") as f_in:
            for line in f_in:
                json_line=json.loads(line)
                section_line=json_line['section']
                del json_line['section']
                sentence_counter_by_section_by_community[community_id][section_line]=json_line

    if section not in sentence_counter_by_section_by_community[community_id].keys():
        return None
    
    return sentence_counter_by_section_by_community[community_id][section]

section_articles_by_community={}

def get_section_articles_by_community(community_id):
    # gets articles in which section appears in given category community
    if community_id not in section_articles_by_community.keys():
        section_articles_by_community[community_id]={}
        with open(f"../data/semantic_similarity/community_{community_id}/section_articles.json", "r", encoding="utf8") as f_in:
            for line in f_in:
                json_line=json.loads(line)
                section_articles_by_community[community_id][json_line['section']]=set(json_line['articles'])

    return section_articles_by_community[community_id]

semantic_similar_section_pairs_by_community={}

def get_semantic_similar_section_pairs(community_id,min_cosine_threshold,sections):
    if community_id not in semantic_similar_section_pairs_by_community.keys():
        # the idea is to not load pairs of similar sections whose same_article_appearance is above threshold for sem filter lvl 3
        # because those pairs will often be iterated on
        max_same_article_appearance_threshold = 0.005
        
        semantic_similar_section_pairs_by_community[community_id]=[]
        # we pass "" instead of section title just to load file content in memory
        get_sentence_counter_by_section_by_community("",community_id)

        # pairs of semantical similar sections are represented with ids instead of titles therefore we need to map ids to titles
        id_section_map={}
        for section,result in sentence_counter_by_section_by_community[community_id].items():
            id_section_map[result['id']]=section

        section_articles=get_section_articles_by_community(community_id)
        with open(f"../data/semantic_similarity/community_{community_id}/similar_section_pairs.json", "r", encoding="utf8") as f_in:
            for line in f_in:
                json_line=json.loads(line)
                json_line['section_A']=id_section_map[json_line['section_A']]
                json_line['section_B']=id_section_map[json_line['section_B']]
                section_B=json_line['section_B']
                section_A=json_line['section_A']

                nb_possible_different_articles = len(
                section_articles[section_A].union(section_articles[section_B]))
                nb_different_articles_both_sections = len(
                    section_articles[section_A].intersection(section_articles[section_B]))

                same_article_appearance = nb_different_articles_both_sections / \
                    nb_possible_different_articles

                # we don't keep pairs in memory which will be ignored by filtering algo
                if same_article_appearance > max(max_same_article_appearance_threshold, 1/nb_possible_different_articles) and min(len(section_articles[section_A]),len(section_articles[section_B]))>1  and not check_stemmed_sections(section_A, section_B):
                    continue

                semantic_similar_section_pairs_by_community[community_id].append(json_line)

    semantic_similar_section_pairs=[]
    for x in semantic_similar_section_pairs_by_community[community_id]:
        if x['mean_score']>=min_cosine_threshold and x['section_A'] in sections and x['section_B'] in sections:
            semantic_similar_section_pairs.append(x)

    return semantic_similar_section_pairs

# key: section, value: set of stemmed words in section title
sections_set_stemmed_words = {}

def stemm_section(section):
    cleaned_section = pattern_non_letters.sub(" ", section)
    splitted_cleaned_section = cleaned_section.split()
    if len(splitted_cleaned_section) == 0:
        sections_set_stemmed_words[section] = set()
    else:
        splitted_cleaned_section = [word.lower()
                                    for word in splitted_cleaned_section]
        sections_set_stemmed_words[section] = set(
            [sno.stem(word) for word in splitted_cleaned_section if word not in stopwords])

# even if a pair of sections has a high same article appearance, if they share same stemmed words we add this pair in similarity graph
# e.g. "Works" and "Work" or "Life" and "Early life"
def check_stemmed_sections(section_A, section_B):
    if section_A not in sections_set_stemmed_words.keys():
        stemm_section(section_A)
    if section_B not in sections_set_stemmed_words.keys():
        stemm_section(section_B)

    return sections_set_stemmed_words[section_A] <= sections_set_stemmed_words[section_B] or sections_set_stemmed_words[section_B] <= sections_set_stemmed_words[section_A]

def filter_semantic_similar_sections(recs,community_ids, semantic_filtering_level,sentence_counter_by_section_global):
    recs_set=set(recs)
    for community_id in community_ids:

        results = get_cosine_sim_thresholds_by_community(community_id)
        if results:
            semantic_filtering_level_min_cosine_sim_map = {3: 0.5}
            for result in results:
                semantic_filtering_level_min_cosine_sim_map[result['semantic_filtering_level']
                                                            ] = result['min_cosine_sim']
        else:
            semantic_filtering_level_min_cosine_sim_map = semantic_filtering_level_default_min_cosine_sim_map

        min_cosine_threshold = semantic_filtering_level_min_cosine_sim_map[
            semantic_filtering_level]

        sentence_counter_by_section = {}
        
        for section in recs:
            result = get_sentence_counter_by_section_by_community(section,community_id)
            if result:
                sentence_counter_by_section[section] = result['nb_sentences']

        section_articles=get_section_articles_by_community(community_id)

        pairs=get_current_article_similar_pairs(community_id,min_cosine_threshold,recs_set)
    
        for pair in pairs:
            section_A = pair['section_A']
            section_B = pair['section_B']
            nb_similar_sentences = pair['nb_similar_sentences']
            mean_score = pair['mean_score']
            
            normalized_nb_similar_sentences = nb_similar_sentences / \
                (sentence_counter_by_section[section_A]
                * sentence_counter_by_section[section_B])

            nb_possible_different_articles = len(
                section_articles[section_A].union(section_articles[section_B]))
            nb_different_articles_both_sections = len(
                section_articles[section_A].intersection(section_articles[section_B]))

            same_article_appearance = nb_different_articles_both_sections / \
                nb_possible_different_articles

            max_same_article_appearance_threshold = 0.001

            # we allow more sections to be grouped together at semantic_filtering_level=3 even if they appear more in same articles
            if semantic_filtering_level == 3:
                max_same_article_appearance_threshold = 0.005

            if same_article_appearance > max(max_same_article_appearance_threshold, 1/nb_possible_different_articles) and min(len(section_articles[section_A]),len(section_articles[section_B]))>1  and not check_stemmed_sections(section_A, section_B):
                continue

            if normalized_nb_similar_sentences > 1/(sentence_counter_by_section[section_A]*sentence_counter_by_section[section_B]) or min(sentence_counter_by_section[section_A], sentence_counter_by_section[section_B]) == 1:

                if not g.get_edge_data(section_A, section_B):
                    g.add_edge(section_A, section_B, normalized_nb_similar_sentences_list=[
                            normalized_nb_similar_sentences])
                else:
                    g.get_edge_data(section_A, section_B)[
                        'normalized_nb_similar_sentences_list'].append(normalized_nb_similar_sentences)

    
    for section_A, section_B in g.edges:

        normalized_nb_similar_sentences_list = g.get_edge_data(
            section_A, section_B)['normalized_nb_similar_sentences_list']
        normalized_nb_similar_sentences = sum(
            normalized_nb_similar_sentences_list)/len(normalized_nb_similar_sentences_list)
        g.get_edge_data(section_A, section_B)[
            'normalized_nb_similar_sentences'] = normalized_nb_similar_sentences

    mean_normalized_nb_similar_sentences_by_section = {}
    
    for section_A in g.nodes:
        normalized_nb_similar_sentences_list = []

        for section_B in g.neighbors(section_A):
            normalized_nb_similar_sentences_list.append(g.get_edge_data(
                section_A, section_B)['normalized_nb_similar_sentences'])

        mean_normalized_nb_similar_sentences_by_section[section_A] = sum(
            normalized_nb_similar_sentences_list)/len(normalized_nb_similar_sentences_list)

    filtered_sections = set()

    dendo = community_louvain.generate_dendrogram(
        g, weight="normalized_nb_similar_sentences", random_state=42, resolution=1)

    # we use first pass of Louvain community detection which gives us smaller communities than by default
    partition = community_louvain.partition_at_level(dendo, 0)

    # key: similar section community id, value: set of sections
    com_sections = {}
    for section, com in partition.items():
        if com not in com_sections.keys():
            com_sections[com] = set()
        com_sections[com].add(section)

    semantic_similar_sections_list=[]

    for similar_sections in com_sections.values():
        sections_relevance = {}
        similar_sections_set = set(similar_sections)

        for section_A in similar_sections:
            normalized_nb_similar_sentences_list = []
            for section_B in g.neighbors(section_A):
                normalized_nb_similar_sentences_list.append(g.get_edge_data(
                    section_A, section_B)['normalized_nb_similar_sentences'])

            sections_relevance[section_A] = sum(normalized_nb_similar_sentences_list)/len(
                normalized_nb_similar_sentences_list)*sentence_counter_by_section_global[section_A]

        filtered_sections |= similar_sections_set
        kept_section = sorted(similar_sections, key=lambda section: -
                            sections_relevance[section])[0]
        filtered_sections.remove(kept_section)
        
        semantic_similar_sections_list.append(sections_relevance)
    

    return [section for section in recs if section not in filtered_sections],semantic_similar_sections_list


def get_current_article_similar_pairs(community_id,min_cosine_threshold,sections):
    # we save potential similar section pairs for the category communities to which article belongs when we start with k=2
    # for a given semantic filtering level into a temporary list of semantic similar pairs (current_article_similar_pairs)
    # each time we add a pair of similar section in the graph we delete this pair from this temporary list of semantic similar pair
    # thanks to this, when k progresses further, less pairs need to be checked inside this temporary list 
    # if they contain the newly introduced section as k progresses
    pairs=[]
    indexes_to_delete=set()
    for i,pair in enumerate(current_article_similar_pairs[community_id]):
        if pair['mean_score']>=min_cosine_threshold and pair['section_A'] in sections and pair['section_B'] in sections :
            pairs.append(pair)
            indexes_to_delete.add(i)

    current_article_similar_pairs[community_id]=[pair for i, pair in enumerate(current_article_similar_pairs[community_id]) if i not in indexes_to_delete]
    
    return pairs

def copy_pairs(pair_list,min_cosine_threshold=0.5,remove_pairs_under_threshold=False):
    # this is used to backup the temporary list of potential semantic similar pair for current article
    # in order to reuse this temporary list when we build a new graph for current article but with other semantic similarity level
    # we start with semantic similarity lvl 3 and progress to 2 and 1, this way we can avoid to copy similar section pairs that are used only for lvl 3
    # when we build the semantic similar graph for lvl 2 and then we avoid to copy pairs of lvl 2 when we build graph for lvl 1
    if remove_pairs_under_threshold:
        indexes_to_delete=set()
        pair_list_copy=[]
        for i,pair in enumerate(pair_list):
            if pair['mean_score']>=min_cosine_threshold:
                pair_list_copy.append(pair.copy())
            else:
                indexes_to_delete.add(i)

        pair_list=[pair for i, pair in enumerate(pair_list) if i not in indexes_to_delete]

        return pair_list_copy
    else:
        # 0.5 is the minimum cosine similarity score across all pairs in dataset, therefore if the threshold is 0.5 we copy everything
        if min_cosine_threshold!=0.5:
            return [pair.copy() for pair in pair_list if pair['mean_score']>=min_cosine_threshold]
        else:
            return [pair.copy() for pair in pair_list]

# we clear graph between each semantic filtering level for each article instead of creating new graph, it's faster that way
g = nx.Graph()

# temporary list of semantic similar pairs for category communities to which current article belongs
current_article_similar_pairs={}

def apply_semantic_filtering_on_results(folder_name):
    semantic_filtering_levels=[1,2,3]
    print(f"Applying semantic filtering on experiment {folder_name}")
    
    load_files_in_memory()
    
    result_file_name = f"../data/results/{folder_name}/recs_by_article.json"
    filtered_result_file_name=f"../data/results/{folder_name}/filtered_recs_by_article.json"

    # useful when the semantic filtering on whole dataset is interrupted
    processed_articles=set()
    try:
        with open(filtered_result_file_name, "r",encoding="utf8") as f_in:
            for line in f_in:
                json_line=json.loads(line)
                article=json_line['article']
                processed_articles.add(article)
    except FileNotFoundError:
        pass

    nb_articles=0
    with open(result_file_name, "r", encoding="utf8") as f_in:
        for line in f_in:
            nb_articles+=1

    with open(filtered_result_file_name, "a+",encoding="utf8") as f_out:
        with open(result_file_name, "r", encoding="utf8") as f_in:
            for line in tqdm(f_in,total=nb_articles):

                json_line=json.loads(line)
                article=json_line['article']
                if article in processed_articles:
                    continue
                
                categories=json_line['categories']
                sections=json_line['sections']
                recs=[x['section'] for x in json_line['recs']]

                recs_set=set(recs)

                if len(recs) < 2:
                    continue
                
                community_ids = set()
                for category in categories:
                    if category in category_community.keys():
                        community_ids.add(category_community[category])

                if len(community_ids) == 0:
                    continue

                current_article_similar_pairs.clear()

                sentence_counter_by_section_global = Counter()

                min_cosine_threshold_by_community_by_semantic_filtering_level={}
                
                for community_id in community_ids:

                    results = get_cosine_sim_thresholds_by_community(community_id)
                    if results:
                        min_cosine_threshold_by_community_by_semantic_filtering_level[community_id] = {3: 0.5}
                        for result in results:
                            min_cosine_threshold_by_community_by_semantic_filtering_level[community_id][result['semantic_filtering_level']
                                                                        ] = result['min_cosine_sim']
                    else:
                        min_cosine_threshold_by_community_by_semantic_filtering_level[community_id] = semantic_filtering_level_default_min_cosine_sim_map
                    
                    for section in recs:
                        result = get_sentence_counter_by_section_by_community(section,community_id)
                        if result:
                            sentence_counter_by_section_global[section] += result['nb_sentences']

                    # copy similar pairs containing sections for rec list of length 20
                    current_article_similar_pairs[community_id]=copy_pairs(get_semantic_similar_section_pairs(community_id,0.50,recs_set))
                
                similar_pairs_copy={}
                for community_id in community_ids:
                    # because we delete pairs from current_article_similar_pairs after inserting them into graph, 
                    # we backup them for next semantic filtering lvl
                    similar_pairs_copy[community_id]=copy_pairs(current_article_similar_pairs[community_id])

                filtered_result={'article':article,'categories':categories,'sections':sections,'recs':recs,'filtered_recs':[]}

                # we begin with semantic filtering lvl 3, then delete pairs which were similar only for this level, this reduces the number of pairs
                # on which levels under will have to iterate
                for semantic_filtering_level in reversed(semantic_filtering_levels):
                    g.clear()
                    
                    for k in range(2,21):
                        recs_filtered,semantic_similar_sections_list=filter_semantic_similar_sections(recs[:k],community_ids,semantic_filtering_level,sentence_counter_by_section_global)

                        filtered_result['filtered_recs'].append({'k':k,'recs_filtered':recs_filtered,'semantic_similar_sections':semantic_similar_sections_list,'semantic_filtering_level':semantic_filtering_level})

                    if semantic_filtering_level>1:
                        for community_id in community_ids:
                            min_cosine_threshold=min_cosine_threshold_by_community_by_semantic_filtering_level[community_id][semantic_filtering_level-1]
                            # we copy pairs from backup to tmp similar pair list, and remove pairs which have cosine sim under threshold of next 
                            # semantic filtering lvl
                            current_article_similar_pairs[community_id]=copy_pairs(similar_pairs_copy[community_id],min_cosine_threshold=min_cosine_threshold,remove_pairs_under_threshold=True)

                f_out.write(json.dumps(filtered_result, ensure_ascii=False)+"\n")
                