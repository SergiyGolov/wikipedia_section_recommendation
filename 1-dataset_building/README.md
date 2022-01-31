In order to build the dataset with up-to-date you'll need:
- A SQL file containing information about Wikipedia pages: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz
    - import it in your SQL DB
- A SQL file containing category links: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz
    - import it in your SQL DB
- A XML file containing the content of Wikipedia pages: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
    - this file should be placed in the `../data` folder, DO NOT extract it
- A TTL file containing types for DBpedia entities: https://databus.dbpedia.org/dbpedia/mappings/instance-types/ download the "en, specific" file
    - this file should be placed in the `../data` folder

If you want to build the dataset with data from March 2021 in order to reproduce the results that we've published, here are the files:
- `page.sql`: https://drive.switch.ch/index.php/s/8XMG1ELIXBK2T2y
- `categorylinks.sql`: https://drive.switch.ch/index.php/s/I1GrxpL5ndxycjb
- `pages-articles.xml.bz2`: https://drive.switch.ch/index.php/s/ug6QaLiZgn76Rwa
- `instance-types.ttl`: https://drive.switch.ch/index.php/s/Gp5BV9ul8LxYjeq

Importing the SQL files could take a while (some hours), see https://stackoverflow.com/questions/30387731/loading-enwiki-latest-categorylinks-sql-into-mysql/40379086#40379086 to speed it up.

Once that you have imported the SQL files, redefine if needed the MYSQL variables in the `../utils/dataset_building.py` file

Then you'll need to download https://github.com/SergiyGolov/wikiextractor and install it locally as specified in its README (we have corrected a bug that occurred while parsing list elements of Wikipedia articles with an HTML output, therefore if you'll download it from pip it won't work).

If the `.jar` files from this folder do not work for you, you can build them yourself:
- build https://github.com/SergiyGolov/WCNPruning (we added the possibility to change the gini threshold by command line) to obtain `wcnpruning-0.0.1-jar-with-dependencies.jar`
- build https://github.com/SergiyGolov/GraphCyclesRemoval (we fixed a bug where the output of the program was empty) to obtain `cycles_removal.jar`