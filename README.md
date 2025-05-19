# IdentifierNameNormalization
Normalize identifier names (split, expand, and standardize). I need this too for my masters thesis, but I don't see such tools on the internet, so I guess I will build one myself. There are several libraries such as *inflection*, that can split a hardword into softwords. But I need more than that.

## What does it do, How to use this?
Just look at **Pipelines.ipynb**. Here is a short explanation: 

This projects can help you break down programming names into semantic componets, for example: the name "avgName_foryou" will be broken down to something that looks like this:

    [{'substring': 'avg', 'type': 'abbreviation', 'expansion': 'average'},
     {'substring': 'Name', 'type': 'dictionary', 'expansion': 'name'},
     {'substring': 'for', 'type': 'dictionary', 'expansion': 'for'},
     {'substring': 'you', 'type': 'dictionary', 'expansion': 'you'}]
Then you can choose to concatenate the things you want, like the original standardized name "avg_name_for_you", or the normalized name "average_name_for_you". 

Other functionalities:

A. The HardwordParser can identify the naming convention of a name by calling 

    hard_word_parser.classify_naming_convention(<identifier_name>)
B. Both SoftwordParsers can identify the type of the softword (see explanation for all possible types...)

C. The SemanticSoftwordParser can show the reasoning process for the softword it just parsed. Call 

    semantic_parser.get_reasoning_process()

**Why/How does it work? Please look at the Explanation section below.**

# Threats to Validity
The first thing I notice, is that my framework of softword decomposition does not work for "made up words". Words such as "jsonify", which means change something to json format. Since this is a semantic parser, we are supoose to be able to identify such cases, since as human we understand this phrase. Or words such as "tokenizer", means the tool that tokenize something, (tokenize also is a made up word that means to convert something into tokens...). Other examples are "configurator", "validator".

But my consideration here is that we are building this parser so that we can analyze the usage of natural language in my masters thesis. So in my thesis we didn't focus on the case of made up words in programming languages. Maybe this can be an interesting direction. But from a parsing word perspective, it is technically correct to parse jsonify to json (technical term) + ify (unidentifiable). 

# Explanation
## Table of Contents
- [Naming conventions](#naming-conventions)
- [Hardword to Softword](#hardword-to-softword)
- [Interprete softwords](#interprete-softwords)
- [Identify Dictionary words](#identify-dictionary-words)
- [Identify abbreviations](#identify-abbreviations)
- [Identify abbreviations](#identify-abbreviations)
- [Abbreviations/acronym, domain specific terms, dictionary words](#abbreviationsacronym-domain-specific-terms-dictionary-words)
- [Identify typos](#identify-typos)
- [Heuristic Softword Parser](#heuristic-softword-parser)
- [Semantic Softword Parser](#semantic-softword-parser)



## Naming conventions
There are several naming conventions, I will take the one from python style guild (https://peps.python.org/pep-0008/#descriptive-naming-styles). I used a different system of naming though... Regarding the regex of naming conventions, there are reddit posts that discuss about it, but whether or not to include numbers in the name is still debatable. So I wrote my own version of regex based on their discussion, that allows numbers in the names. (Although names cannot start with number.)

    lowercase & lowercase single letter: ^[a-z][a-z0-9]*$ -> because we can't be sure if it's snake case or camel case
    snake_case:                          ^[a-z][a-z0-9]*(_[a-z0-9]+)+$  -> strating from the second word, allows words starting with numbers such as "my_8na9me10"
    camelCase:                           ^[a-z][a-z0-9]*([A-Z][a-z0-9]*)+$ -> allows substring of capitalized letters such as "calculateVCDiemnsion", each word must start with a letter
    PascalCase:                          ^(?=.*[a-z])([A-Z][a-z0-9]*)+$  -> allows single word such as "Hello", allows substring of capitalized letters such as "VCDiemnsion", but must contain at least one single lowercase that's not the first letter, else it's screaming case. 
    SCREAMING_SNAKE_CASE:                ^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$ -> allows uppercase & uppercase single letter such as "SCREAMING"

    
And any name that does not match the above naming conventions will be considered as "irregular". Common irregulars cases are:

    "__init", "hello__", "he__llo": begin/ends with underscore, have two or more underscore together. 
    "myname_IS_SamYiin_helloWorld": mix of naming conventions.

Names that are unpleasant but still considered as valid:

    "todaYisawOndErFuLday" -> this is a camelCase
    "m2n3m423_888" -> this is snake case...
    "To4267day" -> this is a PascalCase, if you agree that na32me_bad is a snake case, then you would agree to this....

I have compared the definition of the 5 classes I defined, they are mutually exclusive (there cannot be a name that is in both class), and they are complementary (all the names must belong to one of the classes (of course, because I have the "other" class that takes every unidentifiable names....). There can be a totally different definition on internet if you don't think number should exist in identifier names, but I guess just take the "0-9" out of the regex and it would work...
    
## Identifier Names to Hardwords
This notion is introduced by Lawrie in his paper *Quantifying identifier quality: An analysis of trends* (2007). **Hard words** are substrings of an identifier that are clearly separated by explicit word markers, such as underscores or camelCase conventions. **Soft words** are conceptual components within a hard word. A hard word might contain multiple soft words if it encodes multiple concepts without explicit word markers. For example, in the identifier "hashtable_entry", there are two hard words: "hashtable" and "entry". The hard word "hashtable" is further composed of the soft words "hash" and "table", while entry is a single soft word. This sction we will talk about how to split identifier names to hard words. 

First of all, no standard English word contains number or underscore in them, so if we see number or underscore, it is an indicator for split. (Although there are some phrases that have meaning after combined with a number, like "unit64")

    [A-Za-z]+|\d+

After we split the name by underscores and numbers, each part will be a combination of upper and lower letters, here our rule is *"Split before each capital letter that is followed by a lowercase letter or capital letter that is preceded by a lowercase letter"*. 

    (?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])

For example: 
1. "helloWorld" will be "hello" and "World"
2. "HelloWorld" should be splitted to "Hello" and "World"
3. "VCDimension" should be "VC" and "Dimension".
4. “helloWORLD" should be "hello" and "WORLD"

Python library *inflection* uses the logic regarding underscore and combination of upper and lower letters, but it doesn't keep the original capitalization, neither does it split numbers. We need the original caitalization for the masters thesis. So I guess I will just write one parser myself.  

## Interprete Hard Words
By our definition above, hard words will contain either all English Letters or all numbers. (Because we splitted it by numbers and underscores). Now a hard word can be a concatenation of one or more of the following semantic components (soft words):

    numbers 
    single letters
    dictionary words
    abbreviation (We call it "abbreviation" but it's combination of  common abbreviations/acronyms and technical/domain specific terms)
    typo of dictionary word (typo of abbreviation would be unidentifiable term...)
    unidentifiable terms

We generalize the process of hard word interpretation into two steps: **split** and **expansion**. 
1. Split the softword into semantic components (soft words). In this step we decide the type and number of components inside a hard word.  
2. Based on the split in step 1, expand each semantic components if necessary: single letter and dictionary word stays as is, expand abbreviations and fix typos.

The most probable **interpretation** of a hard word is the most likely "combination" of **split and expansion**. (Technically we can have a math definition here with that conditional probability and Cartesian product and stuff...)

I will give four sets of examples, the first set of examples is when the split and expansion are very clear (to our "common sense"):

    filename = split: "file" (dictionary) + "name" (dictionary). | expansion: they are both dictionary words. | result: "file name"
    stepx = split: "step" (dictionary) + "x"(single letter). | expansion: combination of a dictionary word and a single letter. | result: "step x"
    
The second set of examples is when the split is not clear (thus the result is not clear):

    e = split: "e" (single letter). | expansion: it's a single letter. | result: "e"
    e = split: "e" (abbreviation). | expansion: abbreviation of "exception". | result: "exception"

    nowhere = split: "now" (dictionary) + "here" (dictionary). | expansion: two dictionary words. | result: "now here"
    nowhere = split: "no" (dictionary) +  where" (dictionary). | expansion: two dictionary words. | result: "no where"

    args = split: "args" (abbreviation). | expansion: abbreviation of "arguments". | result: "arguments"
    args = split: "arg"(abbreviation) + "s" (single letter). | expansion: "arg" is abbreviation of "argument". | result: "argument s"

The third set of examples is when the split is clear, but the expansion is not clear (thus the result is not clear):

    alt = split: "alt" (abbreviation). | expansion: abbreviation of "alternative". | result: "alternative"
    alt = split: "alt" (abbreviation). | expansion: abbreviation of "alternate". | result: "alternate"

The fourth set of examples is more tricky: the result is the same, but there might be different splits and expansions: 

    regex = split: "reg"(abbreviation) + "ex" (abbreviation). | expansion: abbreviation of "regular" and "expression". | result: "regular expression"
    regex = split: "regex"(abbreviation). | expansion: abbreviation of "regular expression". | result: "regular expression"

    kwargs = split: "kw" (abbreviation) + "args" (abbreviation) | expansion: abbreviation of "keyword" and "arguments". | result: "keyword arguments"
    kwargs = split: "kwargs"(abbreviation). | expansion: abbreviation of "keyword arguments". | result: "keyword arguments"
Obviously, it can also be that neither the split and the expansion are clear, and thus in most cases the result are not clear. 
    
**Previous attempts**:
1. In "A large-scale investigation of local variable names in java programs: Is longer name better for broader scope variable?" 2021, Aman use the method: given a hard word, generate all possible two-term-concatenation, see if we can find concatenation of two dictionary words (their dictionary also includes 200 common abbreviations). (Limitation: what if the soft word is concatenation of more than two words? They claimed that such case doesn't exist in their data).
2. In "Quantifying identifier quality: An analysis of trends" 2007, Lawrie used A greedy algorithm to identify hard words. It looks for the longest prefix and the longest suffix that are ’on a list’. The list of abbreviations includes domain abbreviations (e.g., alt for altitude) and programming abbreviations (e.g., txt for text and msg for message). (Limitation: This list of only about 200 common abbreviations, clearly does not contain all abbreviation used in the analyzed code. )
3. In "Learning natural coding conventions" 2014, Allamanis used The aggressive splitting algorithm GenTest, which systematically generates all possible splits of an identifier and then scores them based on a set of features. The features and exact weightings can be found in the work of Lawrie et al. (Limitation: This is a more general approach than Aman, but it still limits to concatenation of two components.)
4. In "Investigating naming convention adherence in java references" 2015, Butler tokenised the names with INTT. (Limitation: tokenization is certainly a better approach, not so much critisism here... The only thing we want to improve is adding common sense: for example, "throwable" should not be splitted to "throw" and "able")

**My theory**:

I argue that chosing the most probably **interpretation** (aka **split and expansion**) is a semantic task. It based on "common sense", which is a complex judgement based on the given context -- the project, the file name, the function of the identifier in the code, the convention of community, etc.... Simple algorithm can not capture the omplexity. So I decided that I will let LLM decide the most probable interpretation. 


## Identify Dictionary words
I use my own project in which I built a multi-purpose dictionary. The repo name is EnglishDictionary. For the concern of this project, the dictionary we use is ENABLE, you can check out the full info in the *EnglishDictionary* repo. 

## Expanding abbreviations
Difficulty: the relationship of abbreviations to expansions is many-to-many. There are cases where the same word has multiple abbreviations, such as “configuration”which is abbreviated as “config”, “conf”, or even “cfg”. At the same time the abbreviation “pos”can signify “position”or “positive”. Although we can never be certain, a common approach is to take context into consideration. For example, "pos" in "bomb_pos" is more likely to mean "position" than "positive". 

**Previous attempts**:
1. In "Statistical unigram analysis for source code repository” 2017, Xu built a Naive Bayes model to predict the original word behind an abbreviation.they search for potential candidate within a certain **radius** of the abbreviation, e.g., the method or class in which the abbreviation is used or data flow or control flow neighborhood of the abbreviation. And then compare if the abbreviation is a sub string of the found word (variables it interacts with).
2. In " large-scale investigation of local variable names in java programs: Is longer name better for broader scope variable?" 2021, Aman built a dictionary of 201 common abbreviations by referencing https://www.abbreviations.com/.
3. In "When are names similar or the same? introducing the code names matcher library" 2022, Munk consider one word being abbreviation of the other if the first word is a prefix of the other, coupled with the requirement that the shorter one be at least 3 letters long.
4. In "Reanalysis of empirical data on java local variables with narrow and broad scope" 2023, Feitelson scanned 10,000 names, ended up with 199 word-abbreviation pairs. (for example,“regexp”which is an abbreviation of“regular expression”)
5. In "The impact of vocabulary normalization" 2015, Binkley mirror the process of statistical machine translation, exploits co-occurrence data to select the best of several possible expansions
6. In "Investigating naming convention adherence in java references" 2015, Butler used the library MDSC, a freely available multi-dictionary spell checking library for identifier names, contains lists of abbreviations, acronyms and words from the SCOWL word lists with additional lists of technical terms, abbreviations and acronyms taken from their own work and the AMAP project.

## The "abbreviation" catagory: Abbreviations/acronym, techical/domain specific terms, dictionary words
A more accurate name for the "abbreviation" catagory should be "identifiable non-dictionary words (excluding typos)" because sometimes a domain specific term might not be an abbreviation nor a dictionary word (For example "java"). Some-other-times, a domain specific term starts as an acronyme of real english words, but they got very popular so people start to just treat them as a new word (this happends in real language too.) (For example "sql"). Some_other-other-times, a domain specific term might even have abbreviation of themselves. (For example, "js" for "javascript"). This Includes things like strings that represent types in programming (e.g. "tuple").  

Even in natural language, sometimes an abbreviation becomes so pervalent it just being considered as a dictionary word. (After all, dictionary is just a set of strings that "some" group of people aggreed upon --Sam). So there is always this blurry line between abbreviations and dictionary words.

If we take a step further, we also need to ask the question: what is an abbreviation? If you go to https://www.abbreviations.com/, and type any random string, it is almost always an abbreviation for something (for simplicity, let's not differentiate abbreviations and acronyms). (So basically abbreviations are also just a set of strings that some group of people in certain domain agree upon. The more common the abbreviation, the larger the group. -- Wise man Sam again. )

Anyways, so in short, to avoid answering all these complicated questions, I will define here that Domain specific term is considered abbreviation in my dictionary - even when they themsleves have abbreviation. Because sometimes they started with being acronymes of real english word.

## Identify typos
**Previous attempts**:
1. In "How developers choose names" 2022: Feitelson identify typos by names with a Levenshtein distance less than equals 2. This means that if one name can be transformed into an dictionary word by up to 2 single-letter edits (insertion, deletion, or substitution), then it's the typo of the dictionary word (Given that we already ruled out the possibility of single letter, dictionary word, abbreviation.) (This approach is pretty good, but since we are passing things to LLM already, we will not use this approach, LLM can identify typos using common sense, which should be more common sense than this algorithm.)

## Heuristic Softword Parser
I did some heuristics preprocessing in my own masters thesis to save money... (you don't have to, you can just pass everything to LLM). 
1. I prepared three dictionary to first identify English dictionary words, (very) common abbreviations and strings that represents programming types like "list". This part is taken directly from my EnglishDictionary project. Here is the link to it: https://github.com/samyiin/EnglishDictionary.git. 
2. We then filter out all the single letters and lable them as single letter (they might be abbreviation but I argue that most of the time they are too ambiguous to expand)
3. For each hard word, either they are in the set {single letter, dictionary, common abbreviation}, or if we can generate a split so that the first substring and the second substring are both in the set, then we conclude that this is the correct parse. 
4. Only for the rest of the unidentifiable hard words, we pass them to LLM. In our case, we only pass the hardword as the context for the unidentifiable hardword, technically you can also pass in other context like the entire project, which should largely increase the accuracy. But money money....

This approach reduced the amount of request from 160k down to 7k... So worth a try. (consider 7.5k is 6 dollars, 160k is around a hundred dollars..)

## Semantic Softword Parser
I basically pass this thinking process to LLM and tell it to parse according to certain format. Thanks to openai's function calling method, we can make sure the output of LLM is always accords to the given format. The trick here is to use function calling ability of Openai's assistant api, so that it will always return a json format defined by me. We are not actually calling any function, just need the formatting of output. I also find out that telling the model to reason before calling the function will greatly increase the accuracy of the results. (The semantic_softword_parser will check certain aspect of the results and if it's wrong then it will make the call again until success). I didn't put nunbers as an option because by definition above any number will be a hard word by itself, and we can handle it algorithmicly. 

The prompt is in *Utils/sys_msg.txt* and the function definition is in *Utils/function.txt*. The cheapest model that is smart enough is gpt-4.1-mini. The gpt-4.1-nano or gpt-4o-mini are not smart enough for the task. 


