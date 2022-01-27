#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib
from statistics import quantiles
import nltk
nltk.download('stopwords')
from flask import Flask, request, jsonify, render_template
from collections import Counter
from pymongo import MongoClient
from collections import Counter
import community as community_louvain
import networkx as nx
import re
import json
pattern_non_letters = re.compile('[\W_0-9]+')
sno = nltk.stem.SnowballStemmer('english')
stopwords = set(nltk.corpus.stopwords.words('english'))

# client = MongoClient(host="mongodb_wikipedia_section_recommendation:27017")
client = MongoClient()
db = client.wikipedia

app = Flask(__name__)
app.jinja_env.filters['url_decode'] = lambda x: urllib.parse.unquote(x)

# these are the default minimum cosine similarity thresholds for each semantic filtering level
semantic_filtering_level_default_min_cosine_sim_map = {
    1: 0.6228756904602051,
    2: 0.554182292450042,
    3: 0.5,
}


@app.route('/', methods=['GET'])
def homepage():
    return render_template('home.html')


@app.route('/select', methods=['GET'])
def select():
    return render_template('select_categories.html', server_ip=request.host)


@app.route('/category_children', methods=['GET'])
def get_category_children():
    parent = request.args.get('parent', 'Main_topic_classifications')
    return jsonify({'children': list(db.category_graph.find({'parent': parent}, {'_id': False}))})


@app.route('/search_category', methods=['GET'])
def search_category():
    query = request.args.get('query', 'Main_topic_classifications')
    categories = [{'category': x['category'], 'category_id':x['category_id']}
                  for x in list(db.category_section_counts.find({"$text": {"$search": query}}))]
    return jsonify({'categories': categories})


@app.route('/search_article', methods=['GET'])
def search_article():
    query = request.args.get('query', 'Wikipedia')
    articles = [{'article': x['article_search'], 'category_ids':[{'category': category, 'category_id': map_category_titles_to_ids([category])[0]} for category in x['categories']]}
                for x in list(db.article_categories.find({"$text": {"$search": query}}))]
    return jsonify({'articles': articles})


@app.route('/recommend_page', methods=['GET'])
def recommend_page():
    categories, semantic_filtering_level, k = get_recommendation_parameters_from_request(
        request)
    recommendations,filtered_sections_map,_ = recommend_sections(
        categories, semantic_filtering_level, k)
    
    category_names = [urllib.parse.quote(
        x) for x in map_category_ids_to_titles(categories)]
    
    recommendations = [urllib.parse.quote(x) for x in recommendations]
    filtered_sections_map={urllib.parse.quote(k):[urllib.parse.quote(x) for x in v] for k,v in filtered_sections_map.items()}

    return render_template('recommendations.html', recommendations=recommendations, categories=category_names, k=k, semantic_filtering_level=semantic_filtering_level, category_ids=categories, server_ip=request.host,filtered_sections_map=filtered_sections_map)


@app.route('/recommend', methods=['GET'])
def recommend_api_call():
    categories, semantic_filtering_level, k = get_recommendation_parameters_from_request(
        request)

    recommendations,filtered_sections_map,semantic_similar_sections_list = recommend_sections(
        categories, semantic_filtering_level, k)

    return jsonify({'recommendations': recommendations,'filtered_sections_map':filtered_sections_map,'semantic_similar_sections':semantic_similar_sections_list})


def get_recommendation_parameters_from_request(request):
    k = int(request.args.get('k', -1))

    semantic_filtering_level = int(
        request.args.get('semantic_filtering_level', 0))
    
    categories = [int(category_id) for category_id in request.args.get(
        'categories', '39597549,40591124,27642486,43646685,55371380,41429323').split(',')]

    # if no rec list size specified, set k to most common article length among selected categories
    if k == -1:
        counter = Counter()
        for category_id in categories:
            result =db.category_article_lengths.find_one({'category_id': category_id})
            if result:
                for article_length in result['article_lengths']:
                    length = article_length['length']
                    count = article_length['count']
                    counter[length] += count

        k, _ = counter.most_common(1)[0]

    return categories, semantic_filtering_level, k


def recommend_sections(categories, semantic_filtering_level, k):

    sections_counter = Counter()
    for category_id in categories:
        result = db.category_section_counts.find_one(
            {'category_id': category_id})
        if result:
            for d in result['recs'][:30]:
                sections_counter[d['section']] += d['probability']

    recs = [section for section,
            probability in sections_counter.most_common(k)]
            
    filtered_sections_map={}
    semantic_similar_sections_list=[]
    if semantic_filtering_level > 0:
        recs,filtered_sections_map,semantic_similar_sections_list = filter_semantic_similar_sections(
            recs, categories, semantic_filtering_level)

    recs = order_sections(recs, categories)

    return recs,filtered_sections_map,semantic_similar_sections_list


def filter_semantic_similar_sections(recs, categories, semantic_filtering_level):

    if len(recs) < 2:
        return recs,{}

    community_ids = set()
    for category_id in categories:
        result = db.category_community.find_one({'category_id': category_id})
        if result:
            community_ids.add(result['community_id'])
    if len(community_ids) == 0:
        return recs,{}

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

    def check_stemmed_sections(section_A, section_B):
        if section_A not in sections_set_stemmed_words.keys():
            stemm_section(section_A)
        if section_B not in sections_set_stemmed_words.keys():
            stemm_section(section_B)

        return sections_set_stemmed_words[section_A] <= sections_set_stemmed_words[section_B] or sections_set_stemmed_words[section_B] <= sections_set_stemmed_words[section_A]
    
    sentence_counter_by_section_global = Counter()

    g = nx.Graph()

    for community_id in community_ids:

        results = db.cosine_sim_thresholds_by_community.find(
            {'community_id': community_id})
        if results:
            semantic_filtering_level_min_cosine_sim_map = {3: 0.5}
            for result in results:
                semantic_filtering_level_min_cosine_sim_map[result['semantic_filtering_level']
                                                            ] = result['min_cosine_sim']
        else:
            semantic_filtering_level_min_cosine_sim_map = semantic_filtering_level_default_min_cosine_sim_map
        min_cosine_threshold = semantic_filtering_level_min_cosine_sim_map[
            semantic_filtering_level]

        section_id_map = {}

        sentence_counter_by_section = {}
        section_articles = {}
        for section in recs:
            result = db.sentence_counter_by_section_by_community.find_one(
                {'community_id': community_id, 'section': section})
            if result:
                section_id_map[section] = result['id']
                sentence_counter_by_section[section] = result['nb_sentences']
                sentence_counter_by_section_global[section] += sentence_counter_by_section[section]

            result = db.section_articles_by_community.find_one(
                {'community_id': community_id, 'section': section})
            if result:
                section_articles[section] = set(result['articles'])

        id_section_map = {v: k for k, v in section_id_map.items()}

        section_ids = [section_id_map[x]
                       for x in recs if x in section_id_map.keys()]

        results = list(db.semantic_similar_section_pairs.find({'community_id': community_id, '$and': [{'section_A': {
                       '$in': section_ids}}, {'section_B': {'$in': section_ids}}], 'mean_score': {'$gte': min_cosine_threshold}}))
        
        for result in results:
            section_A = id_section_map[result['section_A']]
            section_B = id_section_map[result['section_B']]
            nb_similar_sentences = result['nb_similar_sentences']
            mean_score = result['mean_score']
            normalized_nb_similar_sentences = nb_similar_sentences / \
                (sentence_counter_by_section[section_A]
                * sentence_counter_by_section[section_B])

            nb_possible_different_articles = len(
                section_articles[section_A].union(section_articles[section_B]))
            nb_different_articles_both_sections = len(
                section_articles[section_A].intersection(section_articles[section_B]))

            same_article_probability = nb_different_articles_both_sections / \
                nb_possible_different_articles

            max_same_article_probability_threshold = 0.001

            # we allow more sections to be grouped together at semantic_filtering_level=3
            if semantic_filtering_level == 3:
                max_same_article_probability_threshold = 0.005

            if same_article_probability > max(max_same_article_probability_threshold, 1/nb_possible_different_articles) and min(len(section_articles[section_A]),len(section_articles[section_B]))>1  and not check_stemmed_sections(section_A, section_B):
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

    partition = community_louvain.partition_at_level(dendo, 0)

    com_sections = {}
    for section, com in partition.items():
        if com not in com_sections.keys():
            com_sections[com] = set()
        com_sections[com].add(section)

    
    filtered_sections_map={}
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
        filtered_sections_map[kept_section]=list(similar_sections_set-set([kept_section]))
        semantic_similar_sections_list.append(sections_relevance)
    
    return [section for section in recs if section not in filtered_sections],filtered_sections_map,semantic_similar_sections_list


def map_category_ids_to_titles(category_id_list):
    category_titles=[]
    for category_id in category_id_list:
        result =db.category_section_counts.find_one({'category_id': category_id})
        if result:
            category_titles.append(result['category'])
    return category_titles


def map_category_titles_to_ids(category_list):
    return [db.category_section_counts.find_one({'category': category})['category_id'] for category in category_list]


def order_sections(sections, categories):

    if len(sections) == 1:
        return sections

    section_order_values_map = {}

    for section in sections:
        number_values = 0
        sum_values_beginning = 0
        sum_values_end = 0

        for category_id in categories:

            result = db.section_ordering.find_one(
                {'section': section, 'category_id': category_id})
            if result:
                number_values += result['number_values']
                sum_values_beginning += result['sum_values_beginning']
                sum_values_end += result['sum_values_end']

        mean_beginning = sum_values_beginning/number_values
        mean_end = sum_values_end/number_values

        section_order_values_map[section] = (mean_beginning+mean_end)/2

    return [section for section, order_value_midpoint in sorted(section_order_values_map.items(), key=lambda section_order_value_midpoint_tuple:section_order_value_midpoint_tuple[1])]


if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')
