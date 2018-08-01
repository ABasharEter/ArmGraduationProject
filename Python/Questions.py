class Question:
    def __init__(self,text,label,numSamples):
        self.text = text
        self.label = label
        self.numSamples = numSamples
        self.currentSample=0
        self.data = None