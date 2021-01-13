import re

def parse(field, value):
    if field in parsers:
        parser = parsers[field]        
        if type(parser) is not str:
            return parser(value)            
        field = parser        
    return stringFormat(field, value)
        
# We should remove italics and bold, but preserve links.
def stringFormat(field, value):
    return f"**{field.title()}:** {value}"
        
# Cleans up a CD.
def cd(value):
    match = re.search('\(?{ *{ *(CD|Coxeter-Dynkin +Diagram)', value)
    
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
    'obsa': "BSA",
    'bsa': "BSA",
    'ubsa': "BSA",
    'csymbol': cd,
    'cox': cd,
    'coxeter': cd,
    'schlafli': 'Schläfli symbol',
    'schläfli': 'Schläfli symbol',
    'symmetry': 'Symmetry',
    'army': 'Army',
    'reg': 'Regiment',
    'regiment': 'Regiment',
    'company': 'Company'
}