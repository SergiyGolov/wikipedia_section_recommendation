var saved_recommendations = {}
var saved_filtered_sections_map={}
saved_recommendations[String(initial_k) + "_" + String(initial_semantic_filtering_level)] = initial_recommendations;
var recommendations = initial_recommendations;
var filtered_sections_map=initial_filtered_sections_map;
saved_filtered_sections_map[String(initial_k) + "_" + String(initial_semantic_filtering_level)] = initial_filtered_sections_map;

document.getElementById("k_slider").addEventListener("change", (e) => update_slider_number(e, "k"));
document.getElementById("k_number").addEventListener("change", (e) => update_slider_number(e, "k"));
document.getElementById("semantic_filtering_level_slider").addEventListener("change", (e) => update_slider_number(e, "semantic_filtering_level"));
document.getElementById("semantic_filtering_level_number").addEventListener("change", (e) => update_slider_number(e, "semantic_filtering_level"));
document.getElementById("checkboxShowFilteredSections").addEventListener("change", (e) => toggleShowFilteredSections(e));

var recommend_button = document.getElementById("recommend");

function update_slider_number(e, id_prefix) {

    if (e.srcElement.id == `${id_prefix}_slider`) {
        document.getElementById(`${id_prefix}_number`).value = e.target.value;
    } else if (e.srcElement.id == `${id_prefix}_number`) {
        document.getElementById(`${id_prefix}_slider`).value = e.target.value;
    }
    recommend();
}

var showFilteredSections=false;

document.getElementById("checkboxShowFilteredSections").click();


function toggleShowFilteredSections(e){
    showFilteredSections=e.srcElement.checked;
    clear_old_recommendations();
    show_recommendations(recommendations)
}

function recommend() {
    clear_old_recommendations();
    show_loading();

    let k = document.getElementById("k_number").value;;
    let semantic_filtering_level = document.getElementById("semantic_filtering_level_number").value;
    let saved_recommendations_key = String(k) + "_" + String(semantic_filtering_level);

    if (saved_recommendations_key in saved_recommendations) {
        filtered_sections_map=saved_filtered_sections_map[saved_recommendations_key];
        show_recommendations(saved_recommendations[saved_recommendations_key]);
    } else {
        let categories = category_ids.join(",");
        fetch(`${server_ip}/recommend?categories=${categories}&k=${k}&semantic_filtering_level=${semantic_filtering_level}`)
            .then(response => response.json())
            .then(rawData => {
                let new_recommendations = rawData['recommendations'];
                let new_filtered_sections_map=rawData['filtered_sections_map'];
                saved_recommendations[saved_recommendations_key] = new_recommendations;
                saved_filtered_sections_map[saved_recommendations_key]=new_filtered_sections_map;
                filtered_sections_map=new_filtered_sections_map;
                show_recommendations(new_recommendations);
            })
            .catch(err => console.log(err));
    }
}

function clear_old_recommendations() {
    let recommendation_list = document.getElementById("recommendations_list");
    Array.from(recommendation_list.children).forEach(x => _remove(x));

    let recommendations_markup = document.getElementById("recommendations_markup");
    recommendations_markup.innerHTML = "";
}

function show_loading() {
    document.getElementById("recommendations_markup").innerHTML = "Loading...";
    document.getElementById("loading").innerHTML = "Loading...";
    document.getElementById("k_slider").disabled=true;
    document.getElementById("k_number").disabled=true;
    document.getElementById("semantic_filtering_level_slider").disabled=true;
    document.getElementById("semantic_filtering_level_number").disabled=true;
}




function show_recommendations(new_recommendations) {
    recommendations = new_recommendations;
    document.getElementById("loading").innerHTML = "";
    document.getElementById("k_slider").disabled=false;
    document.getElementById("k_number").disabled=false;
    document.getElementById("semantic_filtering_level_slider").disabled=false;
    document.getElementById("semantic_filtering_level_number").disabled=false;
    let recommendation_list = document.getElementById("recommendations_list");
    for (section of recommendations) {
        let li = _el("li");
        if (showFilteredSections && section in filtered_sections_map){
            li.innerHTML = section+" <small>("+filtered_sections_map[section].join(", ")+")</small>";
        }else{
            li.innerHTML = section;
        }
        _append(recommendation_list, [li]);
    }

    let recommendations_markup = document.getElementById("recommendations_markup");
    let markup_str = "\n";
    new_recommendations.forEach(section => markup_str += `==${section}==\n\n`);
    category_names.forEach(category => markup_str += `[[Category:${category}]]\n`);
    recommendations_markup.innerHTML = markup_str;
}

// function change_url() {
//     let url_k = document.getElementById("k_number").value;
//     let url_categories = category_ids.join(",");
//     let url_cosine_threshold = document.getElementById("cosine_threshold_number").value;
//     recommend_button.setAttribute("href", `http://127.0.0.1:5000/recommend_page?categories=${url_categories}&k=${url_k}&cosine_threshold=${url_cosine_threshold}`);
// }