from common import *
import pathlib
import random
from collections import Counter


def get_train_test_sets(article_ids, train_ratio, test_ratio):
    print(
        f"\tSpliting article ids into train ({train_ratio}) and test ({test_ratio}) set...")
    article_ids_list = list(article_ids)
    random.shuffle(article_ids_list)
    train_set = set(article_ids_list[:int(train_ratio*len(article_ids))])
    test_set = set(article_ids_list[int(train_ratio*len(article_ids)):-1])

    return train_set,  test_set


def get_epfl_test_set_articles_and_sections():
    test_set = set()
    article_sections = {}
    print("\tGetting epfl test set from their results file...")
    with open("../data/epfl_paper/recs_probabilistic_by_article.json") as f:
        for line in f:
            line_dict = json.loads(line)
            article_id = int(line_dict['aid'])
            test_set.add(article_id)
            article_sections[article_id] = line_dict['sections']

    return test_set, article_sections


def get_article_sections(all_articles,article_sections_file="../data/article_sections_filtered.json"):
    print("\tGetting article sections...")

    # load whole filtered article sections json, delete articles which are not in all_articles
    article_sections = load_json(
        article_sections_file, object_hook=article_sections_object_hook)

    articles_to_delete = set(article_sections.keys())-all_articles
    for article_id in articles_to_delete:
        del article_sections[article_id]

    section_id_map = {}

    # change sections to ids, to lower memory usage
    i = 0
    for _, sections in article_sections.items():
        for section in sections:
            if section not in section_id_map.keys():
                section_id_map[section] = i
                i += 1

    for article, sections in article_sections.items():
        article_sections[article] = [section_id_map[section]
                                     for section in sections]

    # returns section_id -> section map, to use it for writing results on disk
    id_section_map = {section_id: section for section,
                      section_id in section_id_map.items()}

    return article_sections, id_section_map


def get_category_id_to_title_map():
    return {category_id: category_title for category_id,
            category_title in read_tuple_list_from_file((int, str), "../data/category_ids_titles.tsv")}


def get_categories_of_articles(test_set_articles, articles_categories_file):
    # used to know for which categories we need to compute the category section counts, i.e. we're not interested in 
    # categories to which no article from the test set belongs

    category_title_to_id_map = get_category_title_to_id_map()

    article_categories = {}

    print("\tGetting categories of test set articles")
    pbar = tqdm(total=len(test_set_articles))
    with open(articles_categories_file) as f:
        for line in f:
            split_line = line.split()
            article_id = int(split_line[0])
            if article_id in test_set_articles:
                category = split_line[2]
                # for the epfl reproduction which has 2017 data, we don't have some categories which were renamed in our category->id file,
                # therefore we use the name as identifier in such cases
                if category in category_title_to_id_map.keys():
                    category = category_title_to_id_map[category]
                if article_id not in article_categories.keys():
                    article_categories[article_id] = set()
                article_categories[article_id].add(category)
                pbar.update(1)

    article_categories = {article: list(
        categories) for article, categories in article_categories.items()}
    return article_categories


def count_sections(articles_in_category, article_sections, sections_counter):
    for article in articles_in_category:
        for section_id in article_sections[article]:
            sections_counter[section_id] += 1/len(articles_in_category)


def get_category_section_counts(article_categories, wcnoutput_file, train_set, article_sections, include_test_set=False, top_k=30):

    category_title_to_id_map = get_category_title_to_id_map()

    category_section_counts = {}

    test_set_categories = set().union(*article_categories.values())

    print("\tGetting category section counts")
    pbar = tqdm(total=len(test_set_categories))

    with open(wcnoutput_file) as f:
        for line in f:
            line_dict = json.loads(line)
            category = line_dict['category']

            # for the epfl reproduction which has 2017 data, we don't have some categories which were renamed in our category->id file, therefore we use the name as identifier in such cases
            if category in category_title_to_id_map.keys():
                category = category_title_to_id_map[category]

            if category in test_set_categories:
                articles = line_dict['articles']
                if include_test_set:
                    articles_in_category = articles
                else:
                    articles_in_category = [
                        article for article in articles if article in train_set]

                articles_in_category = [
                    article for article in articles_in_category if article in article_sections.keys()]

                counter = Counter()
                count_sections(articles_in_category, article_sections, counter)
                category_section_counts[category] = Counter(
                    {section: probability for section, probability in counter.most_common(top_k)})

                pbar.update(1)

    return category_section_counts


def get_epfl_category_section_counts(article_categories):
    category_title_to_id_map = get_category_title_to_id_map()

    test_set_categories = set().union(*article_categories.values())

    print("\tGetting epfl category section counts")
    pbar = tqdm(total=len(test_set_categories))
    category_section_counts = {}
    with open("../data/epfl_paper/recs_probabilistic_by_category_top30.json") as f:
        for line in f:
            line_dict = json.loads(line)
            category = line_dict['category']
            if category in category_title_to_id_map.keys():
                category = category_title_to_id_map[category]
            if category in test_set_categories:
                category_section_counts[category] = Counter(
                    {x['_1']: x['_2'] for x in line_dict['recs']})
                pbar.update(1)

    return category_section_counts


def recommend_sections(article, article_categories, category_section_counts):
    categories = article_categories[article]
    categories = [
        category for category in categories if category in category_section_counts.keys()]
    # it is possible that all the categories to which a given article belongs were not pure enough after pruning algorithm
    if len(categories) == 0:
        return None
    sections_counter = Counter(category_section_counts[categories[0]])
    for category in categories[1:]:
        sections_counter += category_section_counts[category]

    return sections_counter


def save_results(filename, results):
    with open(filename, "a+", encoding='utf8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False)+"\n")


def convert_section_counter_to_recs(sections_counter, id_section_map,top_k=20):
    recommended_sections = [section for section,
                            probability in sections_counter.most_common(top_k)]

    recommended_sections_probabilities = [
        probability for section, probability in sections_counter.most_common(top_k)]

    if id_section_map:
        recommended_sections = [id_section_map[section_id]
                                for section_id in recommended_sections]

    recs = [{'section': section, 'probability': probability} for section,
            probability in zip(recommended_sections, recommended_sections_probabilities)]

    return recs


def run_eval(test_set, article_sections, article_categories, category_section_counts, folder_name, id_section_map=None,save_article_recs=True):
    i = 0
    results = []
    category_id_to_title_map = get_category_id_to_title_map()

    pathlib.Path(
        f"../data/results/{folder_name}").mkdir(parents=True, exist_ok=True)
    result_file_name = f"../data/results/{folder_name}/recs_by_article.json"
    category_section_counts_file_name = f"../data/results/{folder_name}/recs_by_category_top30.json"

    results_by_category = []

    print("\tSaving category section counts on disk")
    for category_id, section_counter in tqdm(category_section_counts.items()):

        # for the epfl reproduction which has 2017 data, we don't have some categories which were renamed in our category->id file, therefore we use the name as identifier in such cases
        category = category_id

        if category_id in category_id_to_title_map.keys():
            category = category_id_to_title_map[category_id]

        recs = convert_section_counter_to_recs(section_counter, id_section_map,top_k=30)

        results_by_category.append({'category': category, 'recs': recs})

    save_results(category_section_counts_file_name, results_by_category)

    results_by_category.clear()
    if save_article_recs:
        print("\tRecommending sections for test set")
        for article_id in tqdm(test_set):

            # some article may have 0 sections after section filtering
            if article_id not in article_sections.keys():
                continue

            # in the epfl reproduction, there are some articles which are in the results file but not in the provided article_categories_sept17.tsv file
            # (which is strange because their WCNPruning program imports article ids from the article_categories file)
            if article_id not in article_categories.keys():
                continue

            sections_counter = recommend_sections(
                article_id, article_categories, category_section_counts)

            # it is possible that all the categories to which a given article belongs were not pure enough after pruning algorithm
            if not sections_counter:
                continue

            real_sections = article_sections[article_id]

            # for the epfl reproduction which has 2017 data, we don't have some categories which were renamed in our category->id file,
            # therefore we use the name as identifier in such cases (if category_id in category_id_to_title_map.keys() else category_id)
            categories = [category_id_to_title_map[category_id] if category_id in category_id_to_title_map.keys() else category_id
                        for category_id in article_categories[article_id]]

            if id_section_map:
                real_sections = [id_section_map[section_id]
                                for section_id in real_sections]

            recs = convert_section_counter_to_recs(sections_counter, id_section_map)

            result = {"article": article_id, "categories": categories,
                    "sections": real_sections, "recs": recs}

            results.append(result)
            i += 1
            if i % 1000 == 0:
                save_results(result_file_name, results)
                results.clear()
        save_results(result_file_name, results)

def get_test_set_from_results_file(get_test_set_from_file,results_file_article_key):
    test_set=set()
    with open(get_test_set_from_file, "r", encoding="utf8") as f_in:
        for line in f_in:
            json_line=json.loads(line)
            article=json_line[results_file_article_key]
            test_set.add(article)

    return test_set

def experiment(folder_name, articles_categories_file, wcnoutput_file, include_test_set=False,top_k=30,save_article_recs=True,article_sections_file="../data/article_sections_filtered.json",get_test_set_from_file=None,results_file_article_key="aid"):
    print(f"Running experiment {folder_name}")
    article_ids = get_all_articles(articles_categories_file)
    if get_test_set_from_file:
        test_set=get_test_set_from_results_file(get_test_set_from_file,results_file_article_key)
        train_set=article_ids-test_set
    else:
        train_set,  test_set = get_train_test_sets(article_ids, 0.8, 0.2)
    article_sections, id_section_map = get_article_sections(article_ids,article_sections_file=article_sections_file)
    if include_test_set:
        article_categories = get_categories_of_articles(
            test_set.union(train_set), articles_categories_file)
    else:
        article_categories = get_categories_of_articles(
            test_set, articles_categories_file)
    category_section_counts = get_category_section_counts(
        article_categories, wcnoutput_file, train_set, article_sections, include_test_set=include_test_set,top_k=top_k)
    run_eval(test_set, article_sections, article_categories,
             category_section_counts, folder_name, id_section_map=id_section_map,save_article_recs=save_article_recs)


def epfl_reproduction_provided_category_section_counts():
    folder_name = "epfl_reproduction_provided_category_section_counts"
    print("Running epfl reproduction with provided category section counts")
    epfl_test_set, test_set_article_sections = get_epfl_test_set_articles_and_sections()
    article_categories = get_categories_of_articles(
        epfl_test_set, "../data/epfl_paper/article_categories_sept17.tsv")
    precomputed_category_section_counts = get_epfl_category_section_counts(
        article_categories)
    run_eval(epfl_test_set, test_set_article_sections, article_categories,
             precomputed_category_section_counts, folder_name, id_section_map=None)
