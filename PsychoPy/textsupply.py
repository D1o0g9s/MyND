import string 
from os import listdir
from os.path import join
import random

MAX_TO_MEMORIZE = 4
class TextSupplier: 
    def __init__(self, articles_path): 
        all_articles = listdir(articles_path)
        self.article_filenames = [join(articles_path, all_articles[i]) for i in range(len(all_articles)) if not all_articles[i].startswith(".")]
        self.instructions_filename = join(articles_path, "Instructions.txt")
        self.files_read = set()
        self.files_not_read = set(self.article_filenames)
        print(self.files_not_read)
        
    def getCharacterFrequencies(self, text): 
        # Returns the character frequencies in a sorted tuple list [(freq, char), ...]
        # Smallest frequency is at the front of the list
        char_freq = dict()
        for char in text: 
            if char.isalnum() :
                char = char.lower()
                if char not in char_freq: 
                    char_freq[char] = 1
                else :
                    char_freq[char] = char_freq[char] + 1
        tuple_list = [(char_freq[char], char) for char in char_freq]
        sorted_tuple_list = sorted(tuple_list)
        return sorted_tuple_list
        
    def getIthSection(self, a_list, i, num_partitions): 
        num_elements_total = len(a_list)
        elements_per_group = num_elements_total // num_partitions
        section = a_list[elements_per_group * i: elements_per_group * (i+1)]
        return section

    def updateText(self): 
        # updates self.text and targets with the filename's data
        with open(self.current_article, encoding="utf-8") as txt_file: 
            self.text = txt_file.read()
            self.splitText = self.text.split()

            # Update the cursor
            self.max = len(self.splitText)
            self.cursor = 0

            # Get the target letters / numbers: 
            char_freq = self.getCharacterFrequencies(self.text)
            num_top = min(MAX_TO_MEMORIZE, len(char_freq))
            
            random_from_each_section = [random.choice(self.getIthSection(char_freq, i, num_top))[1] for i in range(1, num_top - 1)]
            self.targets = set(random_from_each_section)
            

    def getAnotherArticle(self): 
        # Gets the next article and updates the data structures to ensure that we keep track of what article has been seen
        if(not self.files_not_read):
            return False
        if not self.files_read: 
            filename = self.instructions_filename
        else: 
            filename = random.choice(list(self.files_not_read))

        print(filename)
        self.files_not_read.remove(filename)
        self.files_read.add(filename)
        self.current_article = filename
        self.updateText()

    def hasNext(self): 
        return self.cursor < self.max
    
    def getNext(self): 
        if self.cursor < self.max: 
            toReturn = self.splitText[self.cursor]
            self.cursor += 1
            return toReturn
        else :
            return -1

    def getTargets(self) :
        return self.targets

    def checkInSet(self, word):
        cleaned_word = word.translate(word.maketrans("", "", string.punctuation)).lower()
        for char in self.targets: 
            if char in cleaned_word: 
                return True
        return False
    
    def getArticlePath(self):
        return self.current_article


