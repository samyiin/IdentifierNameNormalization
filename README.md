# IdentifierNameNormalization
Normalize identifier names (split, expand, and standardize). I need this too for my masters thesis, but I don't see such tools on the internet, so I guess I will build one myself. There are several libraries such as *inflection*, that can split a hardword into softwords. But I don't see tools that can identify the naming convention of a variable name. 


# Explanation
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

I have compared the definition of the 5 classes I defined, they are mutually exclusive (there cannot be a name that is in both class), and they are complementary (all the names must belong to one of the classes (of course, because I have the "other" class that takes every unidentifiable names....). There can be a totally different definition on internet if you don't think number should exist in identifier names, but I guess just take the "0-9" our of the regex and it would work...
    
## Hardword to Softword
This notion is introduced by Lawrie in his paper *Quantifying identifier quality: An analysis of trends* (2007). "Hard words" are visible parts like "priorityQueue" and "soft words" are smaller semantic units like priority and queue. Regarding the logic to split words, the goal is to separate all the visible separable parts, here I fist split by naming convention:

First of all, no standard English word contains number or underscore in them, so if we see number or underscore, it is an indicator for split.

    [A-Za-z]+|\d+

After we split the name by underscores and numbers, each part will be a combination of upper and lower letters, here our rule is **"Split before each capital letter that is followed by a lowercase letter or capital letter that is preceded by a lowercase letter"**. 

    (?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])

For example: 
1. "helloWorld" will be "hello" and "World"
2. "HelloWorld" should be splitted to "Hello" and "World"
3. "VCDimension" should be "VC" and "Dimension".
4. “helloWORLD" should be "hello" and "WORLD"

Python library *inflection* uses the logic regarding underscore and combination of upper and lower letters, but it doesn't keep the original capitalization, neither does it split numbers. We need the original caitalization for the masters thesis. So I guess I will just write one parser myself.  

## Splitting softwords
By our definition above, soft words will only contain English Letters. (Because we splitted it by numbers and underscores). Now a softword can be a concatenation of one or more of the following things:

    dictionary word
    single letter
    common abbreviation (including acronyms, technical terms, domain specific terms)
    typo of dictionary word (typo of abbreviation would be unidentifiable term...)
    unidentifiable terms
    
To make sure this division is mutually exclusive, we define  
    Single letter is not dictionary word. 
    abbreviation is non-dictionary word, non single letter.
    typo of dictionary word is non-dictionary word, non single letter, non abbreviation
    unidentifiable temrs is non of the above

For example:

    filename = file + name, combination of two dictionary words
    regex = reg + ex, combination of abbreviations for "regular" and "expression"
    stepx = step + x, combination of a dictionary word and a single letter
    e = can be a single letter, can also be abbreviation of "exception", so it falls under "single letter". 
    
The difficulty of splitting soft words:
    
    agrs: can be an abbreviation of "arguments", but can also be interprete as "arg" + "s"
Previous attempts:
1. In "A large-scale investigation of local variable names in java programs: Is longer name better for broader scope variable?" 2021, Aman use the method: given a soft word, generate all possible two-term-concatenation, see if we can find concatenation of two dictionary words (their dictionary also includes 200 common abbreviations). (Limitation: what if the soft word is concatenation of more than two words? They claimed that such case doesn't exist in their data).
2. In "Quantifying identifier quality: An analysis of trends" 2007, Lawrie used A greedy algorithm to identify soft words. It looks for the longest prefix and the longest suffix that are ’on a list’. The list of abbreviations includes domain abbreviations (e.g., alt for altitude) and programming abbreviations (e.g., txt for text and msg for message). (Limitation: This list of only about 200 common abbreviations, clearly does not contain all abbreviation used in the analyzed code. )
3. In "Learning natural coding conventions" 2014, Allamanis used The aggressive splitting algorithm GenTest, which systematically generates all possible splits of an identifier and then scores them based on a set of features. The features and exact weightings can be found in the work of Lawrie et al. (Limitation: This is a more general approach than Aman, but it still limits to concatenation of two components.)
4. In "nvestigating naming convention adherence in java references" 2015, Butler tokenised the names with INTT. (Limitation: tokenization is certainly a better approach, not so much critisism here...)

## Identify abbreviations
## Identify typos
By our definition, typos are not some abbreviation, it is really just typos of a dictionary word. We will use the same approach by Feitelson in "How developers choose names" 2022: We will identify names with a Levenshtein distance less than equals 2. This means that if one name can be transformed into the other by up to 2 single-letter edits (insertion, deletion, or substitution), then it's the typo of the other. 


    
