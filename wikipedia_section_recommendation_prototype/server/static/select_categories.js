var tomSelectCategories=new TomSelect('#tom-select-it-categories', {
  labelField: 'category',
  valueField: 'category',
  searchField: 'category',
  load: searchCategories,
  onChange: selectedCategory,
  onClear: clearSelectCategory
});

function clearSelectCategory() {
  selected_category = -1;
  let add_category_search = document.getElementById("add_category_search");
  add_category_search.disabled = true;
}

function selectedCategory(value) {
  let add_category_search = document.getElementById("add_category_search");
  if (value != "") {
    add_category_search.disabled = false;
    selected_category = value;
  } else {
    add_category_search.disabled = true;
    selected_category = -1;
  }
}

function add_selected_category(){
  add_category();
  selected_category = -1;
}

document.getElementById("add_category_search").addEventListener("click", () => add_selected_category());

function searchCategories(query, callback) {
  fetch(`${server_ip}/search_category?query=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(json => {
      callback(json['categories']);
      json['categories'].forEach(x => category_id_map[x['category']] = x['category_id']);
    }).catch(() => {
      callback();
    });
}

var tomSelectArticle=new TomSelect('#tom-select-it-articles', {
  labelField: 'article',
  valueField: 'article',
  searchField: 'article',
  load: searchArticles,
  onChange: selectedArticle,
  onClear: clearSelectArticle
});

function clearSelectArticle() {
  selectedArticle = -1;
  let add_article_search = document.getElementById("add_article_search");
  add_article_search.disabled = true;
}

function selectedArticle(value) {
  let add_article_search = document.getElementById("add_article_search");
  if (value != "") {
    add_article_search.disabled = false;
    selected_article = value;
  } else {
    add_article_search.disabled = true;
    selected_article = -1;
  }
}

document.getElementById("add_article_search").addEventListener("click", () => add_categories_of_selected_article());

function searchArticles(query, callback) {
  fetch(`${server_ip}/search_article?query=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(json => {
      callback(json['articles']);
      for (article_dict_key in json['articles']){
        article_dict=json['articles'][article_dict_key];
        article_categories[article_dict['article']]=[];
        for (category_id_dict_key in article_dict['category_ids']){
          category_id_dict=article_dict['category_ids'][category_id_dict_key];
          category_id_map[category_id_dict['category']] = category_id_dict['category_id']
          article_categories[article_dict['article']].push(category_id_dict['category']);
        }
      }
      
    }).catch(() => {
      callback();
    });
}

function add_categories_of_selected_article(){
  if (selected_article!=-1){
    for (selected_article_categories_key in article_categories[selected_article]){
      selected_category=article_categories[selected_article][selected_article_categories_key];
      add_category();
    }
    selected_category = -1;
  }
}

var container = document.getElementById("finder_container");
emitter = finder(container, remoteSource, {
  createItemContent: createItemContent
});

var category_id_map = {}
var article_categories={}
var selected_categories = [];
var selected_categories_li = []
var selected_category = -1;
var selected_article=-1;

var regex = RegExp("_", "g");
var reverseRegex = RegExp(" ", "g");

var recommend_button = document.getElementById("recommend");
var clear_button = document.getElementById("clear");
clear_button.addEventListener("click", () => remove_all_categories());


function change_url() {
  let url_categories = selected_categories.map(x => category_id_map[x]).join(",");
  recommend_button.setAttribute("href", `${server_ip}/recommend_page?categories=${url_categories}`);
}

function remove_category(category) {
  selected_categories = selected_categories.filter(el => el != category);
  selected_categories_li.forEach(x => {
    if (x.innerHTML.replace(reverseRegex, "_").startsWith(category)) {
      _remove(x);
    }
  });
  selected_categories_li = selected_categories_li.filter(x => !x.innerHTML.startsWith(category));
  if (selected_categories.length == 0) {
    recommend_button.classList.add("disabled");
    clear_button.classList.add("disabled");
  }
  change_url();
}

function remove_all_categories() {
  selected_categories.forEach(category => remove_category(category));
}

function add_category() {
  if (!selected_categories.includes(selected_category) && selected_category != "" && selected_category != -1) {
    let selected_categories_element = document.getElementById("selected_categories");
    let li_selected_category = _el("li");
    let this_selected_category = JSON.parse(JSON.stringify(selected_category));
    li_selected_category.innerHTML = selected_category.replace(regex, " ");
    let delete_button = _el("button");
    let space = _el("span");
    space.innerHTML = "&nbsp;";
    delete_button.innerHTML = "X";
    delete_button.classList.add("btn");
    delete_button.classList.add("btn-sm");
    delete_button.classList.add("btn-outline-danger");
    delete_button.addEventListener("click", () => remove_category(this_selected_category));
    _append(li_selected_category, [space, delete_button]);
    _append(selected_categories_element, [li_selected_category]);
    selected_categories_li.push(li_selected_category);
    selected_categories.push(selected_category);
    recommend_button.classList.remove("disabled");
    clear_button.classList.remove("disabled");
    change_url();
  }
}

//the code that follows was adapted from https://github.com/mynameistechno/finderjs/blob/master/example/example-async.js

// scroll to the right if necessary
emitter.on('column-created', function columnCreated() {
  container.scrollLeft = container.scrollWidth - container.clientWidth;
});

function remoteSource(parent, cfg, callback) {
  var loadingIndicator = createLoadingColumn();
  if (parent) {
    parent_name = parent['child'];

  } else {
    parent_name = "Main_topic_classifications";
  }
  // loading spinner
  cfg.emitter.emit('create-column', loadingIndicator);

  // xhr request
  fetch(`${server_ip}/category_children?parent=${parent_name}`)
    .then(response => response.json())
    .then(rawData => {

      // clear loading spinner
      _remove(loadingIndicator);

      children = rawData['children'].filter(x => x['child_has_section_counts'] || x['child_is_parent']);
      //sort by alphabetic order
      children = children.sort((a, b) => a['child'] < b['child'] ? -1 : 1);
      // execute callback
      callback(children);
    })
    .catch(err => console.log(err));
}

// item render
function createItemContent(cfg, item) {
  let frag = document.createDocumentFragment();
  let row = _el('div');

  _addClass(row, "d-flex");
  _addClass(row, "justify-content-between");
  let label = _el('div');

  _addClass(label, "align-self-center");

  row.appendChild(label);

  let category = item['child'];
  label.appendChild(_text(category.replace(regex, " ")));

  if (item['child_has_section_counts']) {
    category_id_map[item['child']] = item['child_id'];
    let button_col = _el("div");

    let this_selected_category = JSON.parse(JSON.stringify(category));
    let add_this_category_button = _el("button");
    add_this_category_button.addEventListener("click", () => {
      selected_category = this_selected_category;
      add_category();
    });
    _addClass(add_this_category_button, "btn");
    _addClass(add_this_category_button, "btn-secondary");
    _addClass(add_this_category_button, "btn-sm");
    button_col.appendChild(add_this_category_button);


    add_this_category_button.innerHTML = "Add";
    row.appendChild(button_col);
  }
  row.style.width = "100%";
  frag.appendChild(row);

  return frag;
}


function createLoadingColumn() {
  var div = _el('div.fjs-col.leaf-col');
  var row = _el('div.leaf-row');
  var text = _text('Loading...');
  var i = _el('span');

  _addClass(i, ['fa', 'fa-refresh', 'fa-spin']);
  _append(row, [i, text]);

  return _append(div, row);
}