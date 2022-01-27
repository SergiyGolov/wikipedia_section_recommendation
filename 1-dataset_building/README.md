In order to build the dataset you'll need:
- A SQL file containing information about Wikipedia pages: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz
    - import it in your SQL DB
- A SQL file containing category links: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz
    - import it in your SQL DB
- A XML file containing the content of Wikipedia pages: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
    - this file should be placed in the `../data` folder, DO NOT extract it
- A TTL file containing types for DBpedia entities: https://databus.dbpedia.org/dbpedia/mappings/instance-types/ download the "en, specific" file
    - this file should be placed in the `../data` folder

Once that you have imported the SQL files, redefine if needed the MYSQL variables in the `../utils/dataset_building.py` file

Then you'll need to download https://github.com/SergiyGolov/wikiextractor and install it locally as specified in its README (we have corrected a bug that occurred while parsing list elements of Wikipedia articles with an HTML output, therefore if you'll download it from pip it won't work).

If you also want to reproduce the results from 2017 by extracting the article's sections yourself before computing the category section counts, you'll first need to download files from https://figshare.com/articles/dataset/WCNPruning_input_set/6157445 and extract them in the `../data/epfl_paper` folder. Then you'll need to download Wikipedia's 2017 dump here: http://itorrents.org/torrent/D567CE8E2EC4792A99197FB61DEAEBD70ADD97C0.torrent and put it in the `../data` folder. Finally you'll have to set the `reproducion_2017` variable to `True` in `6-get_section_content.ipynb` and `7-filter_sections.ipynb`.

If the `.jar` files from this folder do not work for you, you can build them yourself:
- build https://github.com/SergiyGolov/WCNPruning (we added the possibility to change the gini threshold by command line) to obtain `wcnpruning-0.0.1-jar-with-dependencies.jar`
- build https://github.com/SergiyGolov/GraphCyclesRemoval (we fixed a bug where the output of the program was empty) to obtain `cycles_removal.jar`
