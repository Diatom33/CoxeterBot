from typing import Dict, Optional

from mwparserfromhell.wikicode import Wikicode

def parse(params) -> Dict[str, str]:
    # A dictionary of parsed parameter names and values.
    parseFieldList: Dict[str, str] = {}

    # For each of the template's parameters:
    for param in params:
        name: Wikicode = param.name
        code: Wikicode = param.value

        # Compares the param name to the list of parsers.
        newName = getFieldName(str(name))
        if newName is not None:
            if newName in parsers:
                newCode = (parsers[newName])(code)
            else:
                newCode = code

            # Adds the new name and new value to the dictionary.
            parseFieldList[newName] = stringFormat(newCode)

    # Adds default values for missing fields.
    return addDefaults(parseFieldList)

# Translates a wiki infobox name to a human-readable field name.
# We call the former "wiki fields", the latter simply "fields".
def getFieldName(wikiField: str) -> Optional[str]:
    wikiField = wikiField.lower().strip()

    if wikiField in fieldTranslator:
        return fieldTranslator[wikiField]
    return None

# We should remove italics and bold, but preserve links.
def stringFormat(code: Wikicode) -> str:
    return str(code).strip()

# Cleans up a CD.
def cd(code: Wikicode) -> Wikicode:
    # Removes all graphical CDs.
    for template in code.filter_templates():
        if template.name.matches(["CDD", "Coxeter-Dynkin Diagram"]):
            code.remove(template)

    # If the CDs were parenthesized, empty parentheses () will remain, so we remove them.
    try:
        code.replace('()', '')
    # The code throws an error if it doesn't find any matches, but we don't care.
    except ValueError:
        pass

    return code

# Cleans up a field by simply adding uppercase.
def uppercase(code: Wikicode) -> str:
    return str(code).title()

def addDefaults(fieldList: Dict[str, str]) -> Dict[str, str]:
    # First removes empty attributes.
    for name, value in tuple(fieldList.items()):
        if value == '':
            del fieldList[name]

    for name, replace in defaults.items():
        if name not in fieldList:
            fieldList[name] = replace

    return fieldList

defaults: Dict[str, str] = {
    'Space': 'Spherical'
}

fieldTranslator: Dict[str, str] = {
    'dimension': "Dimensions",
    'dim': "Dimensions",
    'dimensions': "Dimensions",
    'rank': "Dimensions",
    'type': "Type",
    'space': "Space",
    'acronym': "Bowers style acronym",
    'obsa': "Bowers style acronym",
    'bsa': "Bowers style acronym",
    'ubsa': "Bowers style acronym",

    'csymbol': 'Coxeter diagram',
    'cox': 'Coxeter diagram',
    'coxeter': 'Coxeter diagram',
    'cd': 'Coxeter diagram',
    'cdd': 'Coxeter diagram',
    'schlafli': 'Schläfli symbol',
    'schläfli': 'Schläfli symbol',
    'taper': 'Tapertopic notation',
    'tapertopic': 'Tapertopic notation',
    'bracket': 'Bracket notation',
    'symmetry': 'Symmetry',
    'army': 'Army',
    'reg': 'Regiment',
    'regiment': 'Regiment',
    'company': 'Company',

    'pieces': 'Number of pieces',
    'loc': 'Level of complexity',
    'convex': 'Convex',
    'conv': 'Convex',
    'orientable': 'Orientable',
    'orient': 'Orientable',
    'nature': 'Nature',
    'nat': 'Nature',

    'dual': 'Dual',
    'conjugate': 'Conjugate',
    'conj': 'Conjugate'
}

parsers = {
    'Coxeter diagram': cd,
    'Convex': uppercase,
    'Orientable': uppercase,
    'Nature': uppercase
}