# wikipedia_section_recommendation

Github repository for the master thesis project "Recommending ordered sections with similar section filtering to help structuring Wikipedia articles". This project consisted in improving an already existing Wikipedia section recommendation algorithm: https://github.com/epfl-dlab/WCNPruning (from "Structuring Wikipedia Articles with Section Recommendations" paper)

## Prerequisite
- python 3.9 if you want to run notebooks from the `2-semantic_similarity_data_building` (`torch` which is used by `sentence_transformers` does not work with python 3.10 for now), otherwise python 3.10 should be fine.
- pip in order to install the required modules in `requirements.txt`
- the files needed to reproduce the method with up-to-date data are listed in `1-dataset_building/README.md`
- instructions on how to run the prototype are in `wikipedia_section_recommendation_prototype/README.md`

## Results
Results can be downloaded at https://drive.switch.ch/index.php/s/Ps50a63xD0OCzww and the zip archive should be extracted in the `data` folder (i.e. you should have a `data/results` folder)

Results of the original paper from 2017 can be downloaded here: https://figshare.com/articles/dataset/Structuring_Wikipedia_Articles_with_Section_Recommendations/6157583 and should be extracted in the `./data/epfl_paper` folder.

The evaluation of those results are shown in the following notebooks:

- `3-experiments_eval/2-eval.ipynb` for the method reproduction and improvement part
- `3-experiments_eval/4-eval_semantic_filtering.ipynb` for the semantic similar sections filtering part
- `3-experiments_eval/6-eval_section_ordering.ipynb` for the section ordering part

## Reproduction with 2021 data (i.e. the one from results and report)
The XML and SQL dumps from March 2021 that we used are no more available, therefore we provide our intermediate data.

You can skip the notebooks from the `1-dataset_building` folder, download https://drive.switch.ch/index.php/s/e7p4wjavPudjZUC (i.e. the output that we had after running the `1-dataset_building` folder) and extract its content in the `data` folder and run notebooks from the `2-semantic_similarity_data_building` folder and then run experiment notebooks from `3-experiments_eval` folder.

You can also skip the notebooks from the `1-dataset_building` and `2-semantic_similarity_data_building` folders, download https://drive.switch.ch/index.php/s/DDGNUFjmc9NvV8g (i.e. the output that we had after running the `1-dataset_building` and `2-semantic_similarity_data_building` folders) and extract its content in the `data` folder and then run experiment notebooks from `3-experiments_eval` folder

## Reproduction of 2017 paper
The files needed for the 2017 paper reproduction can be downloaded here: https://figshare.com/articles/dataset/WCNPruning_input_set/6157445 and should be extracted in the `./data/epfl_paper` folder. If you want to reproduce the results with their precomputed category section counts this is enough.

If you want to compute yourself the category section counts without running notebooks from the `1-dataset_building` folder (otherwise, see instructions in `1-dataset_building/README.md`), you'll need to download https://drive.switch.ch/index.php/s/e7p4wjavPudjZUC and put its content in the `data` folder, because you'll need the `article_sections_2017_filtered.json` file.

## Report
The report describing our method in detail can be downloaded here: https://drive.switch.ch/index.php/s/c83FmfIPkyph5jr