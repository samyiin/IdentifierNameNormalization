from nltk.corpus import words
import numpy as np
# This will give all conjugations of a verb
# https://pypi.org/project/word-forms/
from word_forms.word_forms import get_word_forms
import os
import pandas as pd


class EnglishDictionary:
    def __init__(self, root_dir="Utils/"):
        # This will only be called in the root directory of the project.
        # By default we use the NLTK dictionary
        self.abbrev_dict = None
        self.abbreviations_df = None

        self.program_type_names_dic = None
        self.program_type_names_df = None

        self.dictionary = set(words.words())
        self.source_directory = os.path.join(root_dir, 'EnglishDictionarySource/')
        irregular_verbs_csv = os.path.join(self.source_directory, 'irregular_verbs.csv')
        self.df_irregular_verbs = pd.read_csv(irregular_verbs_csv)
        # initialize with ENABLE
        self.load_dictionary()
        # initialize the list of common abbreviations
        self.load_abbreviation_list()
        # initialize the list of program type names
        self.load_program_type_list()

    # =================function 1: check dictionary words ==========================

    @staticmethod
    def _load_word_list(file_path):
        """Load a large word list from a file into a set."""
        with open(file_path, 'r') as f:
            return set(line.strip().lower() for line in f)

    def load_dictionary(self, dictionary_name="ENABLE"):
        """
        The default value is ENABLE, but there are other values
        :param dictionary_name: [ENABLE, dwyl-english_words, SCOWL, NLTK]
        :return:
        """
        if dictionary_name == "ENABLE":
            # Credit: https://github.com/dolph/dictionary.git
            word_list_path = os.path.join(self.source_directory, 'enable1.txt')
            self.dictionary = self._load_word_list(word_list_path)
        elif dictionary_name == "dwyl-english_words":
            # Credit: https://github.com/dwyl/english-words.git
            word_list_path = os.path.join(self.source_directory, 'words_alpha.txt')
            self.dictionary = self._load_word_list(word_list_path)
        elif dictionary_name == "SCOWL":
            # Credit: https://github.com/en-wl/wordlist.git
            '''
            clone and go to terminal
            make
            ./scowl word-list scowl.db > wl.txt
            :return:
            '''
            word_list_path = os.path.join(self.source_directory, 'wl.txt')
            self.dictionary = self._load_word_list(word_list_path)
        elif dictionary_name == "NLTK":
            import nltk
            nltk.download('words', download_dir=os.path.join(self.source_directory, 'nltk_data'))
            nltk.download('brown', download_dir=os.path.join(self.source_directory, 'nltk_data'))
            self.dictionary = set(words.words())
        else:
            raise ValueError("PARAMETER dictionary_name: [ENABLE, dwyl-english_words, SCOWL, NLTK]")

    def is_english(self, word):
        return (word in self.dictionary) or (word.lower().strip() in self.dictionary)


    # =================function 2: check abbreviations ==========================
    def load_abbreviation_list(self, abbreviation_list="my_list"):
        """
        So far I only have one abbreviation list
        :param abbreviation_list: ["my_list"]
        :return:
        """
        if abbreviation_list != "my_list":
            raise ValueError("Do not support other abbrev list yet...")
        self.abbreviations_df = pd.read_csv(os.path.join(self.source_directory, "abbreviations_my_list.csv"))
        self.abbreviations_df["abbreviation"] = self.abbreviations_df["abbreviation"].str.lower().str.strip()
        self.abbreviations_df["expansion"] = self.abbreviations_df["expansion"].str.lower().str.strip()

        # maps abbrev -> expansion
        self.abbrev_dict = dict(zip(self.abbreviations_df['abbreviation'], self.abbreviations_df['expansion']))

    def is_abbrev(self, word):
        return word.lower().strip() in self.abbrev_dict

    def expand_abbrev(self, word):
        if word.lower().strip() in self.abbrev_dict:
            return self.abbrev_dict[word.lower().strip()]
        else:
            return None

    # =================function 3: check type driven names ==========================
    def load_program_type_list(self, program_type="list1"):
        """
        So far I only have one abbreviation list
        :param program_type: ["my_list"]
        :return:
        """
        if program_type != "list1":
            raise ValueError("Do not support other abbrev list yet...")
        self.program_type_names_df = pd.read_csv(os.path.join(self.source_directory, "common_programming_type_name.csv"))
        self.program_type_names_df["type_string"] = self.program_type_names_df["type_string"].str.lower().str.strip()
        self.program_type_names_df["expansion"] = self.program_type_names_df["expansion"].str.lower().str.strip()

        # maps abbrev -> expansion
        self.program_type_names_dic = dict(zip(self.program_type_names_df['type_string'], self.program_type_names_df['expansion']))

    def is_program_type(self, word):
        return word.lower().strip() in self.program_type_names_dic

    def expand_program_type(self, word):
        if word.lower().strip() in self.program_type_names_dic:
            return self.program_type_names_dic[word.lower().strip()]
        else:
            return None

    # =================function 4: check word forms ==========================

    def word_forms(self, word):
        # Unused....
        return get_word_forms(word)

    def is_irregular_past_tense(self, verb):
        for index, row in self.df_irregular_verbs.iterrows():
            if verb == row['Past Simple'] or verb == row['-ed']:
                if verb != row['Base Form']:
                    return True
        return False
