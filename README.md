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
This notion is introduced by Lawrie in his paper *Quantifying identifier quality: An analysis of trends* (2007). "Hard words" are visible parts like "priorityQueue" and "soft words" are smaller semantic units like priority and queue. Regarding the logic to split words, the goal is to separate all the visible separable parts:

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
