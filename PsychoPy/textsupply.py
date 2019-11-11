
class TextSupplier: 
    def __init__(self): 
        self.text = "The goal would be to identify another aspect of the brain’s activity that could explain without conflict a number of brain functions such as  working memory, perception, and spontaneous activity? If we find something and build a theory around that something, this theory would need to provide explanations for multiple phenomena without suffering from the superposition problem."
        self.splitText = self.text.split()
        self.targets = {"a", "goal"}
        self.max = len(self.splitText)
        self.cursor = 0
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
        if word in self.targets: 
            return True
        else: 
            return False