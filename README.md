# wikipedia_section_recommendation

Github repository for the master thesis project "Recommending ordered sections with similar section filtering to help structuring Wikipedia articles". This project consisted in improving an already existing Wikipedia section recommendation algorithm: https://github.com/epfl-dlab/WCNPruning (from "Structuring Wikipedia Articles with Section Recommendations" paper)

- The report is available in the root of this repository: [report.pdf](https://github.com/SergiyGolov/wikipedia_section_recommendation/blob/main/report.pdf)
- The presentation slides are also available in the root of this repository [presentation.pdf](https://github.com/SergiyGolov/wikipedia_section_recommendation/blob/main/presentation.pdf)

The notebooks and folders have numbers as prefixes which indicates in which order they need to be executed. Run the notebooks in order, one at a time (i.e. free memory of a notebook before running the next).

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


## Reproduction of 2017 paper
The files needed for the 2017 paper reproduction can be downloaded here: https://figshare.com/articles/dataset/WCNPruning_input_set/6157445 and should be extracted in the `./data/epfl_paper` folder. If you want to reproduce the results with their precomputed category section counts, this is enough.

If you also want to reproduce the results from 2017 by extracting the article's sections yourself before computing the category section counts, you'll also need to download Wikipedia's 2017 dump here: http://itorrents.org/torrent/D567CE8E2EC4792A99197FB61DEAEBD70ADD97C0.torrent and put it in the `./data` folder. Finally you'll have to set the `reproducion_2017` variable to `True` in `1-dataset_building/6-get_section_content.ipynb` and `1-dataset_building/7-filter_sections.ipynb`.
