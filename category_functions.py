import requests
import time
from tqdm import tqdm
import json
from os.path import exists
from pathlib import Path
import json
import json
from pathlib import Path
from wdcuration import today_in_quickstatements, query_wikidata

HERE = Path(__file__).parent.resolve()


def render_quickstatements_for_category(
    category, category_entries, P279_value=False, P31_value=False, P17_value=False
):
    statements = ""

    if P279_value:
        qids = [v for v in category_entries.values()]
        formatted_qids = "{wd:" + " wd:".join(qids) + "}"
        query = (
            """      SELECT   (REPLACE(STR(?item), ".*Q", "Q") AS ?qid)  WHERE {    """
            f"VALUES ?item {formatted_qids} ."
            f"MINUS {{ ?item wdt:P279* wd:{P279_value} . }} "
            """   
      }
      
      """
        )
        p279_query_results = query_wikidata(query)
        p279_missing_items = [a["qid"] for a in p279_query_results]

    for k, v in category_entries.items():
        today = today_in_quickstatements()
        category_for_url = category.replace(" ", "_")

        if P279_value:
            if v in p279_missing_items:
                statements += f'{v}|P279|{P279_value}|S4656|"https://en.wikipedia.org/wiki/Category:{category_for_url}"|S813|{today}\n'
        if P31_value:
            statements += f'{v}|P31|{P31_value}|S4656|"https://en.wikipedia.org/wiki/Category:{category_for_url}"|S813|{today}\n'
        if P17_value:
            statements += f'{v}|P17|{P17_value}|S4656|"https://en.wikipedia.org/wiki/Category:{category_for_url}"|S813|{today}\n'

    return statements


def extract_ids_from_category(category, get_subcategories=False, save_json=True):
    category_with_prefix = f"Category:{category}"

    if not get_subcategories:
        pages = get_pages_under_category(category_with_prefix)
        non_category_pages = [a for a in pages if "Category:" not in a]
        non_category_pages = [a for a in non_category_pages if "List of" not in a]
        non_category_pages = [a for a in non_category_pages if "list of" not in a]
        non_category_pages = [a for a in non_category_pages if "culture" not in a]

        pages_with_wikidata_ids = {}

        for pages in tqdm(chunks(non_category_pages, 50)):
            pages_with_wikidata_ids.update(get_ids_from_pages(pages))
            time.sleep(0.2)

        print(pages_with_wikidata_ids)

        if save_json:
            category_file_name = category.lower()
            category_file_name = category_file_name.replace(" ", "_")
            HERE.joinpath(f"{category_file_name}.json").write_text(
                json.dumps(pages_with_wikidata_ids, indent=4, sort_keys=True)
            )
        return pages_with_wikidata_ids


def get_ids_from_pages(pages):
    """
    Returns a dictionary with page titles as keys and Wikidata QIDs as values
    """
    url = "https://en.wikipedia.org/w/api.php?action=query"
    params = {
        "format": "json",
        "prop": "pageprops",
        "ppprop": "wikibase_item",
        "redirects": "1",
        "titles": "|".join(pages),
    }
    r = requests.get(url, params)
    print(r)
    data = r.json()
    print(data)
    id_dict = {}
    for key, values in data["query"]["pages"].items():
        title = values["title"]
        qid = values["pageprops"]["wikibase_item"]
        id_dict[title] = qid

    return id_dict


def get_pages_under_category(category_name):
    url = "https://en.wikipedia.org/w/api.php?action=query"
    params = {
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category_name,
        "cmlimit": "500",
    }
    r = requests.get(url, params)
    data = r.json()
    pages = []
    for response in data["query"]["categorymembers"]:
        pages.append(response["title"])
    while "continue" in data:
        params.update(data["continue"])
        r = requests.get(url, params)
        data = r.json()
        for response in data["query"]["categorymembers"]:
            pages.append(response["title"])
    return pages


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
