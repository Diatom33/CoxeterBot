import re

from src.py.exceptions import TemplateError

# Class for reading the Infobox template.
class Template:
    templateRegex = "{{ *[i|I]nfobox +polytope( |\n)*\|"
    def __init__(self, text):
        self.text = text
        match = re.search(Template.templateRegex, self.text)

        if match is None:
            raise TemplateError("Infobox polytope not found.")

        self.index = match.span()[1] - 1
        self.nestLevel = 2

    # Gets all fields of the template.
    def getFields(self):
        fields = {}

        # While inside of the infobox template:
        while self.nestLevel >= 2:
            # Reads the field.
            # The current char should be '|'.
            self.skip()
            field = self.readWord()

            # Reads the equals sign.
            self.seekFor('=')
            self.skip()

            # Reads the contents.
            init = self.index
            char = self.getChar()
            while not (char == '|' and self.nestLevel == 2) :
                if char == '{' or char == '[':
                    self.nestLevel += 1
                elif char == '}' or char == ']':
                    self.nestLevel -= 1

                if self.nestLevel >= 2:
                    self.index += 1
                    char = self.getChar()
                else:
                    break

            end = self.index
            while self.text[end] in [' ', '\n']:
                end -= 1
                
            fields[field] = self.text[init:end]

        return fields

    # Gets the current character.
    def getChar(self):
        return self.text[self.index]

    # Skips unti a certain char is found.
    def seekFor(self, char):
        self.index = self.text.index(char, self.index)
        return self.index

    # Skips until the next non-space char.
    def skip(self):
        self.index += 1
        while self.getChar() == ' ':
            self.index += 1

    # Reads until ' ' or '=' is found.
    def readWord(self):
        init = self.index
        while self.getChar() not in [' ', '=']:
            self.index += 1

        return self.text[init:self.index]