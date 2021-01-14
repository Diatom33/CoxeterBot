import re
from typing import Callable, Dict, Tuple, Union

from mwparserfromhell.wikicode import Wikicode

def parse(params) -> Dict[str, str]:
    # A dictionary of parsed parameter names and values.
    parseFieldList: Dict[str, str] = {}

    # For each of the template's parameters:
    for param in params:
        name: Wikicode = param.name
        code: Wikicode = param.value

        # Compares the param name to the list of parsers.
        for key, parser in parsers.items():
            if name.matches(key):
                # If the parser is a string, simply replaces the name.
                if isinstance(parser, str):
                    newName, newValue = stringFormat(parser, code)
                # If the parser is a function, applies it.
                else:
                    newName, newValue = parser(code)

                # Adds the new name and new value to the dictionary.
                parseFieldList[newName] = newValue

    return parseFieldList

# We should remove italics and bold, but preserve links.
def stringFormat(name: str, code: Wikicode) -> Tuple[str, str]:
    return name, str(code).rstrip()

# Cleans up a CD.
def cd(code: Wikicode) -> Tuple[str, str]:
    # Removes all graphical CDs.
    for template in code.filter_templates():
        if template.name.matches(["CDD", "Coxeter-Dynkin Diagram"]):
            code.remove(template)

    # If the CDs were parenthesized, empty parentheses () will remain, so we remove them.
    code.replace('()', '')

    return stringFormat('Coxeter diagram', code)

parsers: Dict[str, Union[str, Callable[[str], Tuple[str, str]]]] = {
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