import re
from src.py.template import Template

def parse(fieldList: dict[str, str]):
    parseFieldList = {}

    for field, value in fieldList.items():
        if field in parsers:
            parser = parsers[field]
            if type(parser) is str:
                field = parser
            else:
                field, value = parser(value)
            parseFieldList[field] = value

    return parseFieldList
        
# We should remove italics and bold, but preserve links.
def stringFormat(field: str, value: str):
    return field, value
        
# Cleans up a CD.
def cd(value: str):
    regex = r'\(?' + Template.regex("CDD", "Coxeter-Dynkin Diagram")
    match = re.search(regex, value)
    
    if match is not None:
        value = value[:match.span()[0]].rstrip()
        
    return stringFormat('Coxeter diagram', value)

parsers = {
    'dimension': "Dimensions",
    'dim': "Dimensions",
    'dimensions': "Dimensions",
    'rank': "Dimensions",
    'type': "Type",
    'space': "Space",
    'acronym': "BSA",
    'obsa': "Bowers Style Acronym",
    'bsa': "Bowers Style Acronym",
    'ubsa': "Bowers Style Acronym",
    'csymbol': cd,
    'cox': cd,
    'coxeter': cd,
    'cd': cd,
    'cdd': cd,
    'schlafli': 'Schläfli symbol',
    'schläfli': 'Schläfli symbol',
    'symmetry': 'Symmetry',
    'army': 'Army',
    'reg': 'Regiment',
    'regiment': 'Regiment',
    'company': 'Company'
}