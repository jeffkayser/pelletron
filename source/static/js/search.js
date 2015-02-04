var SEARCH_INDEX_URL = '/search.json';
var SEARCH_LANGUAGE = 'english';
var search_index = null;
var search_stemmer = null;
var search_view = null;
var PUNCTUATION = /[\u2000-\u206F\u2E00-\u2E7F\\'!"#\$%&\(\)\*\+,\-\.\/:;<=>\?@\[\]\^_`\{\|\}~]/g;

function init_search(lang) {
    if(lang === undefined) {
        lang = SEARCH_LANGUAGE;
    }
    load_index(SEARCH_INDEX_URL);
    search_stemmer = new Snowball(lang);
}

function load_index(url) {
    $.getJSON(url, function(data) { search_index = data; });
}

function strip_punctuation(text) {
    return text.replace(PUNCTUATION, ' ');
}

function stem(word) {
    if(search_stemmer == null) {
        return word;
    }
    search_stemmer.setCurrent(word);
    search_stemmer.stem();
    return search_stemmer.getCurrent();
}

function search(text) {
    if(search_index == null) {
        return;
    }

    text = strip_punctuation(text).trim();
    if(text == '') {
        update_search_ui(null);
    }

    words = text.split(/\s+/);
    var stemmed = words.map(stem);

    var results = {};
    var found_indexes = [];
    for(var index in stemmed) {
        var word = stemmed[index];
        if(word in search_index.words) {
            var hit = search_index.words[word];
            for(var page in hit) {
                if(page in found_indexes) {
                    continue;
                }
                found_indexes.push(page);
                var url = search_index.urls[parseInt(page)];
                results[url] = search_index.titles[parseInt(page)];
            }
        }
    }
    update_search_ui(results);
}
