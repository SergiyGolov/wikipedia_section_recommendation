#!/bin/sh
java -jar cycles_removal.jar ../data/category_graph_filtered.tsv ../data/category_graph_filtered_DAG.tsv

java -Xmx14336m -jar wcnpruning-0.0.1-jar-with-dependencies.jar ../data/category_graph_filtered_DAG.tsv ../data/article_categories_filtered.tsv ../data/article_types_no_duplicates.tsv 0.985

mv gini_articles_scores.json ../data/gini_articles_scores_0985.json

java -Xmx14336m -jar wcnpruning-0.0.1-jar-with-dependencies.jar ../data/category_graph_filtered_DAG.tsv ../data/article_categories_no_unknown_types.tsv ../data/article_types_no_duplicates.tsv 0.985

mv gini_articles_scores.json ../data/gini_articles_scores_0985_no_unknown_type.json

java -Xmx14336m -jar wcnpruning-0.0.1-jar-with-dependencies.jar ../data/category_graph_filtered_DAG.tsv ../data/article_categories_filtered.tsv ../data/article_types_no_duplicates.tsv 0.966

mv gini_articles_scores.json ../data/gini_articles_scores.json

java -Xmx14336m -jar wcnpruning-0.0.1-jar-with-dependencies.jar ../data/category_graph_filtered_DAG.tsv ../data/article_categories_no_unknown_types.tsv ../data/article_types_no_duplicates.tsv 0.966

mv gini_articles_scores.json ../data/gini_articles_scores_no_unknown_type.json
