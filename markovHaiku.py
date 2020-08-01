import sys
import logging
import random
from collections import defaultdict
from count_syllables import count_syllables

logging.disable(logging.CRITICAL)  # comment-out to enable debugging messages
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def loadTrainingFile(file):
    """Return a text file as a string."""
    with open(file) as f:
        rawHaiku = f.read()
        return rawHaiku

def prepTraining(rawHaiku):
    """Load string, remove newline, split words on spaces, and return list."""
    corpus = rawHaiku.replace('\n', ' ').split()
    return corpus

def mapWordToWord(corpus):
    """Load list & use dictionary to map word to word that follows."""
    limit = len(corpus)-1
    dict1To1 = defaultdict(list)
    for index, word in enumerate(corpus):
        if index < limit:
            suffix = corpus[index + 1]
            dict1To1[word].append(suffix)
    logging.debug("mapWordToWord results for \"sake\" = %s\n", 
                  dict1To1['sake'])
    return dict1To1

def map2WordsToWord(corpus):
    """Load list & use dictionary to map word-pair to trailing word."""
    limit = len(corpus)-2
    dict2To1 = defaultdict(list)
    for index, word in enumerate(corpus):
        if index < limit:
            key = word + ' ' + corpus[index + 1]
            suffix = corpus[index + 2]
            dict2To1[key].append(suffix)
    logging.debug("map2WordsToWord results for \"sake jug\" = %s\n",
                  dict2To1['sake jug'])
    return dict2To1

def randomWord(corpus):
    """Return random word and syllable count from training corpus."""
    word = random.choice(corpus)
    numSyls = count_syllables(word)
    if numSyls > 4:
        randomWord(corpus)
    else:
        logging.debug("random word & syllables = %s %s\n", word, numSyls)
        return (word, numSyls)

def wordAfterSingle(prefix, suffixMap1, currentSyls, targetSyls):
    """Return all acceptable words in a corpus that follow a single word."""
    acceptedWords = []
    suffixes = suffixMap1.get(prefix)
    if suffixes != None:
        for candidate in suffixes:
            numSyls = count_syllables(candidate)
            if currentSyls + numSyls <= targetSyls:
                acceptedWords.append(candidate)
    logging.debug("accepted words after \"%s\" = %s\n",
                  prefix, set(acceptedWords))
    return acceptedWords


def wordAfterDouble(prefix, suffixMap2, currentSyls, targetSyls):
    """Return all acceptable words in a corpus that follow a word pair."""
    acceptedWords = []
    suffixes = suffixMap2.get(prefix)
    if suffixes != None:
        for candidate in suffixes:
            numSyls = count_syllables(candidate)
            if currentSyls + numSyls <= targetSyls:
                acceptedWords.append(candidate)
    logging.debug("accepted words after \"%s\" = %s\n",
                  prefix, set(acceptedWords))
    return acceptedWords

def haikuLine(suffixMap1, suffixMap2, corpus, endPrevLine, targetSyls):
    """Build a haiku line from a training corpus and return it."""
    line = '2/3'
    lineSyls = 0
    currentLine = []

    if len(endPrevLine) == 0:  # build first line
        line = '1'
        word, numSyls = randomWord(corpus)
        currentLine.append(word)
        lineSyls += numSyls
        wordChoices = wordAfterSingle(word, suffixMap1,
                                         lineSyls, targetSyls)
        while len(wordChoices) == 0:
            prefix = random.choice(corpus)
            logging.debug("new random prefix = %s", prefix)
            wordChoices = wordAfterSingle(prefix, suffixMap1,
                                             lineSyls, targetSyls)
        word = random.choice(wordChoices)
        numSyls = count_syllables(word)
        logging.debug("word & syllables = %s %s", word, numSyls)
        lineSyls += numSyls
        currentLine.append(word)
        if lineSyls == targetSyls:
            endPrevLine.extend(currentLine[-2:])
            return currentLine, endPrevLine

    else:  # build lines 2 & 3
        currentLine.extend(endPrevLine)

    while True:
        logging.debug("line = %s\n", line)
        prefix = currentLine[-2] + ' ' + currentLine[-1]
        wordChoices = wordAfterDouble(prefix, suffixMap2,
                                         lineSyls, targetSyls)
        while len(wordChoices) == 0:
            index = random.randint(0, len(corpus) - 2)
            prefix = corpus[index] + ' ' + corpus[index + 1]
            logging.debug("new random prefix = %s", prefix)
            wordChoices = wordAfterDouble(prefix, suffixMap2,
                                             lineSyls, targetSyls)
        word = random.choice(wordChoices)
        numSyls = count_syllables(word)
        logging.debug("word & syllables = %s %s", word, numSyls)
        
        if lineSyls + numSyls > targetSyls:
            continue
        elif lineSyls + numSyls < targetSyls:
            currentLine.append(word)
            lineSyls += numSyls
        elif lineSyls + numSyls == targetSyls:
            currentLine.append(word)
            break

    endPrevLine = []
    endPrevLine.extend(currentLine[-2:])

    if line == '1':
        finalLine = currentLine[:]
    else:
        finalLine = currentLine[2:]

    return finalLine, endPrevLine


def main():
    """Give user choice of building a haiku or modifying an existing haiku."""
    intro = """\n
    A thousand monkeys at a thousand typewriters...
    or one computer...can sometimes produce a haiku.\n"""
    print("{}".format(intro))

    rawHaiku = loadTrainingFile("train.txt")
    corpus = prepTraining(rawHaiku)
    suffixMap1 = mapWordToWord(corpus)
    suffixMap2 = map2WordsToWord(corpus)
    final = []

    choice = None
    while choice != "0":

        print(
            """
            Japanese Haiku Generator
            0 - Quit
            1 - Generate a Haiku poem
            2 - Regenerate Line 2
            3 - Regenerate Line 3
            """
            )

        choice = input("Choice: ")
        print()

        # exit
        if choice == "0":
            print("Sayonara.")
            sys.exit()

        # generate a full haiku
        elif choice == "1":
            final = []
            endPrevLine = []
            firstLine, endPrevLine1 = haikuLine(suffixMap1, suffixMap2,
                                                    corpus, endPrevLine, 5)
            final.append(firstLine)
            line, endPrevLine2 = haikuLine(suffixMap1, suffixMap2,
                                              corpus, endPrevLine1, 7)
            final.append(line)
            line, endPrevLine3 = haikuLine(suffixMap1, suffixMap2,
                                              corpus, endPrevLine2, 5)
            final.append(line)

        # regenerate line 2
        elif choice == "2":
            if not final:
                print("Please generate a full haiku first (Option 1).")
                continue
            else:
                line, endPrevLine2 = haikuLine(suffixMap1, suffixMap2,
                                                  corpus, endPrevLine1, 7)
                final[1] = line

        # regenerate line 3
        elif choice == "3":
            if not final:
                print("Please generate a full haiku first (Option 1).")
                continue
            else:
                line, endPrevLine3 = haikuLine(suffixMap1, suffixMap2,
                                                  corpus, endPrevLine2, 5)
                final[2] = line

        # some unknown choice
        else:
            print("\nSorry, but that isn't a valid choice.", file=sys.stderr)
            continue

        # display results
        print()
        print("First line = ", end="")
        print(' '.join(final[0]), file=sys.stderr)
        print("Second line = ", end="")
        print(" ".join(final[1]), file=sys.stderr)
        print("Third line = ", end="")
        print(" ".join(final[2]), file=sys.stderr)
        print()

    input("\n\nPress the Enter key to exit.")

if __name__ == '__main__':
    main()