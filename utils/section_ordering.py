from common import *

def get_category_top_sections(folder_name,categories):
    category_top_sections={}
    with open(f"../data/results/{folder_name}/recs_by_category_top30.json") as f:
        for line in f:
            line_dict = json.loads(line)
            category=line_dict['category']
            if category not in categories:
                continue
            recs=line_dict['recs']
            if len(recs)==0:
                continue
            category_top_sections[category]=set([x['section'] for x in recs])

    return category_top_sections

def get_order_values_by_category(category_top_sections,article_sections,category_articles,test_set):
    order_values_by_category={}
    print("Computing order values for categories")
    for category,top_sections in tqdm(category_top_sections.items()):
        
        section_order_numbers_beginning={}
        section_order_numbers_end={}
        
        for article in category_articles[category]:
            if article in test_set:
                continue
            if article in article_sections.keys():
                sections=article_sections[article]
                n=len(sections)
                idx_beginning=0
                for section in sections:
                    idx_end=idx_beginning+1
                    if section in top_sections:
                        if section not in section_order_numbers_beginning.keys():
                            section_order_numbers_beginning[section]=[]
                            section_order_numbers_end[section]=[]
                        section_order_numbers_beginning[section].append(idx_beginning/n)
                        section_order_numbers_end[section].append(idx_end/n)
                    idx_beginning+=1
                
        order_values_by_category[category]={}
        for section in section_order_numbers_beginning.keys():
            number_values=len(section_order_numbers_beginning[section])
            sum_values_beginning=sum(section_order_numbers_beginning[section])
            sum_values_end=sum(section_order_numbers_end[section])
            order_values_by_category[category][section]={'number_values':number_values,'sum_values_beginning':sum_values_beginning,'sum_values_end':sum_values_end}

    return order_values_by_category


def get_category_articles(wcnoutput_file,article_sections):
    category_articles={}
    with open(wcnoutput_file) as f:
        for line in f:
            line_dict = json.loads(line)
            category = line_dict['category']
            articles=[article for article in line_dict['articles'] if article in article_sections.keys()]
            category_articles[category]=articles

    return category_articles

def order_sections(sections, categories,order_values_by_category,ignore_context=False,ignore_end_order_value=False):

    if ignore_context:
        categories=['ignore_context']

    section_order_values_map = {}

    for section in sections:
        number_values = 0
        sum_values_beginning = 0
        sum_values_end = 0
        
        for category in categories:
            if category not in order_values_by_category.keys():
                continue
            if section in order_values_by_category[category].keys():
                result=order_values_by_category[category][section]
                number_values += result['number_values']
                sum_values_beginning += result['sum_values_beginning']
                sum_values_end += result['sum_values_end']
        
        mean_beginning = sum_values_beginning/number_values
        mean_end = sum_values_end/number_values

        if ignore_end_order_value:
            section_order_values_map[section] = mean_beginning
        else:
            section_order_values_map[section] = (mean_beginning+mean_end)/2

    return [(section,order_value) for section, order_value in sorted(section_order_values_map.items(), key=lambda section_order_value_tuple:section_order_value_tuple[1])]

def apply_section_ordering_on_results(folder_name,ignore_context=False,ignore_end_order_value=False):
    print("Loading initial files")
    filtered_result_file_name=f"../data/results/{folder_name}/filtered_recs_by_article.json"
    file_name="ordered_recs_by_article"
    if ignore_context:
        file_name+="_ignore_context"
    if ignore_end_order_value:
        file_name+="_ignore_end_order_value"
    ordered_sections_result_file_name=f"../data/results/{folder_name}/{file_name}.json"

    nb_articles=0
    with open(filtered_result_file_name, "r", encoding="utf8") as f_in:
        for line in f_in:
            nb_articles+=1

    categories=set()
    test_set=set()

    with open(filtered_result_file_name, "r", encoding="utf8") as f:
        for line in f:
            result_dict = json.loads(line)
            article=result_dict['article']
            test_set.add(article)
            for category in result_dict['categories']:
                categories.add(category)
    
    category_top_sections=get_category_top_sections(folder_name,categories)
    if ignore_context:
        all_top_sections=set().union(*category_top_sections.values())
        category_top_sections={'ignore_context':all_top_sections}

    article_sections=load_json("../data/article_sections_filtered.json", object_hook=article_sections_object_hook)
    
    wcnoutput_file="../data/gini_articles_scores_0985_no_unknown_type.json"
    if not ignore_context:
        category_articles=get_category_articles(wcnoutput_file,article_sections)
    else:
        category_articles={'ignore_context':list(article_sections.keys())}

    order_values_by_category=get_order_values_by_category(category_top_sections,article_sections,category_articles,test_set)

    print("Ordering sections for results")
    with open(ordered_sections_result_file_name, "a+",encoding="utf8") as f_out:
        with open(filtered_result_file_name, "r", encoding="utf8") as f_in:
            for line in tqdm(f_in,total=nb_articles):
                result_dict = json.loads(line)
                article=result_dict['article']
                categories=result_dict['categories']
                sections=result_dict['sections']
                recs=result_dict['recs']

                if len(recs)<2:
                    continue
                
                ordered_result={'sections':sections,'categories':categories,'article':article}

                ordered_result['ordered_recs']=[]
                ordered_result['unordered_recs']=[]

                #we also order sections before semantic filtering

                semantic_filtering_level=0

                ordered_recs_with_order_values=order_sections(recs, categories,order_values_by_category,ignore_context=ignore_context,ignore_end_order_value=ignore_end_order_value)

                ordered_recs=[]

                for section, order_value in ordered_recs_with_order_values:
                    ordered_recs.append({'section':section,'order_value':order_value})

                ordered_result['ordered_recs'].append({'semantic_filtering_level':semantic_filtering_level,'recs':ordered_recs})
                ordered_result['unordered_recs'].append({'semantic_filtering_level':semantic_filtering_level,'recs':recs})


                for filtered_recs in result_dict['filtered_recs']:
            
                    k=filtered_recs['k']
                    if k!=20:
                        continue
                    semantic_filtering_level=filtered_recs['semantic_filtering_level']
                    recs_filtered=filtered_recs['recs_filtered']

                    if len(recs_filtered)<2:
                        continue

                    ordered_recs_with_order_values=order_sections(recs_filtered, categories,order_values_by_category,ignore_context=ignore_context,ignore_end_order_value=ignore_end_order_value)

                    ordered_recs=[]

                    for section, order_value in ordered_recs_with_order_values:
                        ordered_recs.append({'section':section,'order_value':order_value})

                    ordered_result['ordered_recs'].append({'semantic_filtering_level':semantic_filtering_level,'recs':ordered_recs})
                    ordered_result['unordered_recs'].append({'semantic_filtering_level':semantic_filtering_level,'recs':recs_filtered})
                f_out.write(json.dumps(ordered_result, ensure_ascii=False)+"\n")


