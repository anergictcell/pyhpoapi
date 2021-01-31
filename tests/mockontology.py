import os

from pyhpo.term import HPOTerm
from pyhpo.ontology import Ontology


def make_terms():
    root = HPOTerm()
    root.id = 'HP:0001'
    root.name = 'Test root'

    child_1_1 = HPOTerm()
    child_1_1.id = 'HP:0011'
    child_1_1.name = 'Test child level 1-1'
    child_1_1.is_a = root.id
    child_1_1.comment = 'Some comment'
    child_1_1.definition = 'Some definition'

    child_1_2 = HPOTerm()
    child_1_2.id = 'HP:0012'
    child_1_2.name = 'Test child level 1-2'
    child_1_2.is_a = root.id
    child_1_2.synonym = '"another name"'
    child_1_2.synonym = '"third name"'
    child_1_2.comment = 'Some comment'
    child_1_2.definition = 'Some definition'

    child_2_1 = HPOTerm()
    child_2_1.id = 'HP:0021'
    child_2_1.name = 'Test child level 2-1'
    child_2_1.is_a = child_1_1.id
    child_2_1.comment = 'Some comment'
    child_2_1.definition = 'Some definition'

    child_3 = HPOTerm()
    child_3.id = 'HP:0031'
    child_3.name = 'Test child level 3'
    child_3.is_a = child_2_1.id
    child_3.is_a = child_1_2.id
    child_3.comment = 'Some comment'
    child_3.definition = 'Some definition'

    child_4 = HPOTerm()
    child_4.id = 'HP:0041'
    child_4.name = 'Test child level 4'
    child_4.is_a = child_3.id
    child_4.comment = 'Some comment'
    child_4.definition = 'Some definition'

    child_1_3 = HPOTerm()
    child_1_3.id = 'HP:0013'
    child_1_3.name = 'Test child level 1-3'
    child_1_3.is_a = root.id
    child_1_3.comment = 'Some comment'
    child_1_3.definition = 'Some definition'

    return (
        root,
        child_1_1,
        child_1_2,
        child_2_1,
        child_3,
        child_4,
        child_1_3
    )


def make_ontology():
    # items = make_terms()
    folder = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        'data'
    )
    terms = Ontology(data_folder=folder)
    # for item in items:
    #     terms._append(item)

    # terms._connect_all()
    # for term in terms:
    #     term.information_content['gene'] = 1
    #     term.information_content['omim'] = 1
    #     term.information_content['orpha'] = 1
    #     term.information_content['decipher'] = 1

    return terms
