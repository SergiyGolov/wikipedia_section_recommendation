In order to build the dataset you'll need:
- A SQL file containing information about Wikipedia pages: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz
- A SQL file containing category links: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz
- A XML file containing the content of Wikipedia pages: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
- A TTL file containing types for DBpedia entities: https://databus.dbpedia.org/dbpedia/mappings/instance-types/ download the "en, specific" file

Once that you have imported the SQL files, redefine if needed the MYSQL variables in the ../utils/dataset_building.py file

Then you'll need to download https://github.com/SergiyGolov/wikiextractor and install it locally as specified in its README (we have corrected a bug that occurred while parsing list elements of Wikipedia articles with an HTML output, therefore if you'll download it from pip it won't work).