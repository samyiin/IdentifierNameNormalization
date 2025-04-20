from Utils.EnglishDictionary import EnglishDictionary

class HeuristicParser:
    SINGLE_LETTER = "single_letter"
    DICTIONARY_WORD = "dictionary"
    ABBREVIATION = "abbreviation"
    TYPO = "typo"
    UNIDENTIFIABLE = "unidentifiable"
    UNKNOWN = "unknown"

    def __init__(self):
        self.my_dictionary = EnglishDictionary()

    def get_type(self, word):
        if len(word) == 1:
            return self.SINGLE_LETTER
        # prioritize if it's on the abbreviation list,
        # because we manually checked the abbrev list, they are actually abbrev
        elif self.my_dictionary.is_abbrev(word) or self.my_dictionary.is_program_type(word):
            return self.ABBREVIATION
        elif self.my_dictionary.is_english(word):
            return self.DICTIONARY_WORD
        else:
            return self.UNKNOWN

    def expand_softword(self, softword):
        if self.my_dictionary.is_abbrev(softword):
            expansion = self.my_dictionary.expand_abbrev(softword)
        elif self.my_dictionary.is_program_type(softword):
            expansion = self.my_dictionary.expand_program_type(softword)
        else:
            expansion = softword
        return expansion.strip()

    def parse(self, softword):
        """
        Assume the softword only contains english letters
        :param softword:
        :return:
        """
        # Direct match without splitting
        word_type = self.get_type(softword)

        # if the softword is identifiable: directly identify
        if word_type != "unknown":
            expansion = self.expand_softword(softword)
            interpretation = {
                "softword": softword,
                "interpretation": {
                    "split": [
                        {
                            "substring": softword,
                            "type": word_type,
                            "expansion": expansion
                        }
                    ],
                    "result": expansion
                }
            }
            return interpretation

        # if the softword is not identifiable, then see if there are two concatenated identifiable terms
        for i in range(1, len(softword)):
            first = softword[:i]
            second = softword[i:]

            first_type = self.get_type(first)
            second_type = self.get_type(second)

            # Only keep splits where both parts are recognizable (not "unknown")
            if first_type != "unknown" and second_type != "unknown":
                first_expansion = self.expand_softword(first)
                second_expansion = self.expand_softword(second)

                interpretation = {
                    "softword": softword,
                    "interpretation": {
                        "split": [
                            {
                                "substring": first,
                                "type": first_type,
                                "expansion": first_expansion
                            },
                            {
                                "substring": second,
                                "type": second_type,
                                "expansion": second_expansion
                            }
                        ],
                        "result": first_expansion + " " + second_expansion
                    }
                }
                # Greedy return the first seen interpretation
                return interpretation
        return None


