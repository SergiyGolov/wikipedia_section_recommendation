from tqdm.notebook import tqdm
import json

# General purpose

def write_tuple_list_to_file(tuple_list, file_name):
    # writes a list of tuples in a file with each tuple in tab separated values format, one line by tuple
    with open(file_name, "w+") as file:
        for tup in tuple_list:
            file.write("\t".join([str(x) for x in tup])+"\n")


def read_tuple_list_from_file(tuple_types, file_name):
    # reads a list of tuples from a file and converts each tuple element into a type specified by tuple_types tuple
    # e.g. if tuple_types = (int,str) the tuples' elements will be converted into those types
    tuple_list = []
    with open(file_name, "r") as file:
        for line in file:
            line_tuple = line.strip().split("\t")
            if len(line_tuple) != len(tuple_types):
                raise Exception(
                    "The desired types of each tuple element should be defined in order to parse them")
            tuple_list.append(tuple(tuple_type(x)
                              for tuple_type, x in zip(tuple_types, line_tuple)))

    return tuple_list

def dump_json(obj, file):
    # dumps an object into file in json format
    with open(file, "w+") as f:
        f.write(json.dumps(obj))

def load_json(file,object_hook=None):
    # load an object from json format file, calls object_hook to e.g. convert dictionnary keys from str to int, because by default dict keys are always str when json.loads is called
    return json.loads(open(file).read(),object_hook=object_hook)

# used to load article_sections.json which was dumped as single dict into one line, this dict has article ids as int keys and by default json module 
# converts all dict keys to str
article_sections_object_hook=lambda d: {int(article_id):sections for article_id,sections in d.items()}

def load_all_article_sections(article_sections_filename):
    article_sections={}
    with open(article_sections_filename) as f:
        for line in f:
            json_line=json.loads(line)
            article_sections[json_line['article_id']]=json_line['sections']

    return article_sections

def get_all_articles(articles_categories_file):
    print("\tGetting all article ids...")
    article_ids = set()
    with open(articles_categories_file) as f:
        for line in f:
            split_line = line.split()
            article_id = int(split_line[0])
            article_ids.add(article_id)

    return article_ids

def get_category_title_to_id_map():
    return {category_title: category_id for category_id,
            category_title in read_tuple_list_from_file((int, str), "../data/category_ids_titles.tsv")}


def get_processed_communities():
    # used to get communities which were already processed in the similar section detection part, useful if the notebook stopped and restarted afterwards. 
    # also used to know which communities have to be loaded for the evaluation and mongodb import for prototype
    processed_communities=set()
    try:
        with open(f"../data/semantic_similarity/processed_communities", "r") as f_in:
            for line in f_in:
                processed_communities.add(int(line))
    except FileNotFoundError:
        pass

    return processed_communities