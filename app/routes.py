# -*- coding: utf-8 -*-
from flask import render_template, redirect, abort, url_for, request
from app import app
from app.models import Exhibit, Author, Typology, Technology, Museum, authors, technologies, FullTextIndex
from app.search import except_field, update_techs

FIELDS = ["query", "page", "name", "author", "museum", "technology", "typology", "pplace", "fplace"]
PER_PAGE = 10


@app.route('/')
def hello():
    return redirect(url_for('search_page'))


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('query')
    field = request.args['field']
    suggestions = {
        'query': Exhibit.query.filter(Exhibit.name.like('%{}%'.format(search))).limit(5).with_entities(Exhibit.name),
        # 'query': Exhibit.query.filter(FullTextIndex(Exhibit.fulltext, search)).limit(5).with_entities(Exhibit.name),
        'name': Exhibit.query.filter(Exhibit.name.like('%{}%'.format(search))).limit(5).with_entities(Exhibit.name),
        # 'author': Author.query.filter(Author.surname.like('%{}%'.format(search))).limit(5).with_entities(Author.surname),
        'author': Author.query.filter(Author.concat.like("%{}%".format("%".join(search.split())))).limit(5),
        'museum': Museum.query.filter(Museum.name.like('%{}%'.format(search))).limit(5).with_entities(Museum.name),
        'typology': Typology.query.filter(Typology.name.like('%{}%'.format(search))).limit(20).with_entities(Typology.name),
        'technology': Technology.query.filter(Technology.name.like('%{}%'.format(' '.join(search.split(",")[-1].split())))).limit(5),
        'pplace': Exhibit.query.filter(Exhibit.production_place.like('%{}%'.format(search))).distinct().limit(5)\
        .with_entities(Exhibit.production_place),
        'fplace': Exhibit.query.filter(Exhibit.find_place.like('%{}%'.format(search))).distinct().limit(5)\
        .with_entities(Exhibit.find_place),
        # 'epoch': (Exhibit.query.filter(Exhibit.epoch.like('%{}%'.format(search))).distinct(), 'epoch', 5),
    }
    if field != 'technology':
        if field != 'author':
            results = [str(item[0]) for item in suggestions[field]]
        else:
            results = [str(item) for item in suggestions[field]]
    else:
        if ',' in search:
            results = [search.rsplit(',', maxsplit=1)[0] + ', ' + str(item) for item in suggestions[field]]
        else:
            results = [str(item) for item in suggestions[field]]
    return {"matching_results": results}


@app.route('/search', methods=['GET', 'POST'])
def search_page():
    data = {field: request.args[field] for field in FIELDS 
    if field in request.args and request.args[field] != ""}
    page = data.pop('page', 1)
    try:
        page = int(page)
    except:
        abort(404)
    results = Exhibit.query
    if "query" in data:
        results = results.filter(FullTextIndex(Exhibit.fulltext, data["query"]))
    if 'name' in data:
        results = results.filter(Exhibit.name.like("%{}%".format(data['name'])))
    if 'author' in data:
        results = results.join(authors)\
        .join(Author, (authors.columns.author_id == Author.id) & (Author.concat.like("%{}%".format("%".join(data['author'].split())))))
        # print(data['author'].split())
    if 'technology' in data:
        techs = data['technology'].replace(',','').split()
        filt = Technology.name.like("%{}%".format(techs[0]))
        for tech in data['technology'].split()[1:]:
            filt |= Technology.name.like("%{}%".format(tech))
        results = results.join(technologies).join(Technology, (technologies.columns.technology_id == Technology.id) & filt)
    if 'museum' in data:
        results = results.filter(Exhibit.museum.has(Museum.name.like("%{}%".format(data['museum']))))
    if 'typology' in data:
        results = results.filter(Exhibit.typology.has(Typology.name.like("%{}%".format(data['typology']))))
    if 'pplace' in data:
        results = results.filter(Exhibit.production_place.like("%{}%".format(data['pplace'])))
    if 'fplace' in data:
        results = results.filter(Exhibit.find_place.like("%{}%".format(data['fplace'])))
    # if 'epoch' in data:
        # results = results.filter(Exhibit.epoch.like("%{}%".format(data['epoch'])))
    # print(results)
    # if "query" in data:
        # results = results.order_by(-FullTextIndex(Exhibit.fulltext, data["query"]))
    results = results.paginate(page, PER_PAGE, False)
    
    return render_template('search.html', args=data, results=results)
