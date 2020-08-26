class TestClass:
    def __init__(self, _type, form):
        self.type = _type
        self.form = form
        self.url = "https://www.prepsharp.com/" + form
        self.filename = _type + "_" + form
        self.pages = []
        self.answers = {"english":{}, "math":{},
                        "reading":{}, "science":{}}
        self.student = {}
        self.mistakes = {}
        self.scale = {"english":{}, "math":{},
                      "reading":{}, "science":{}}
        self.secLens = {"english":75, "math":60,
                        "reading":40, "science":40}
        self.scoreList = []


    def __repr__(self):
        output = ""
        for section in self.mistakes:
            output += section + ": " + str(self.mistakes[section]) + "\n"
        return output
    
        
    #Sets the test to partial or full based on inSecs.
    def setSections(self, inSecs=[]):
        if len(inSecs) > 0:
            for section in inSecs:
                self.student[section] = {}
                self.mistakes[section] = []
        else:
            self.student = {}
            self.mistakes = {}
         
    
    #Uses self.url to extract text of answers and scale from pdf.
    def setPagesFromUrl(self):
        import io, requests
        from PyPDF2 import PdfFileReader

        r = requests.get(self.url)
        f = io.BytesIO(r.content)
        pdf = PdfFileReader(f)
        for pageNum in range(2):
            pageObj = pdf.getPage(pageNum)
            pageTxt = pageObj.extractText()
            self.pages.append(pageTxt)


    #Finds and sets answers appropriately via pages[0].
    def setAnswers(self):
        txt = self.pages[0]
        low = txt.find("1")
        high = txt.find("ACT") - 3
        txt = txt[low:high]

        for section in self.answers.keys(): 
            for total in range(self.secLens[section]):
                try:
                   num = int(txt[:2])
                except(ValueError):
                    self.answers[section][int(txt[0])] = txt[1]
                    txt = txt[2:]
                else:
                    self.answers[section][num] = txt[2]
                    txt = txt[3:]


    #Finds and sets scale appropriately via pages[1]
    def setScale(self):
        txt = self.pages[1]
        
        for section in self.scale.keys():
            trim = txt.find('Score')
            txt = txt[trim + len('Score '):]

            for num in range(36,0,-1):
                i = txt.find(str(num),1,7)
                d = txt.find('-',0,3)

                if i == 4 and d == 2:
                    self.scale[section][num] = txt[:i+1]
                    txt = txt[i+1 + len(str(num)):]
                    continue
                elif i == 3 and d == 2:
                    self.scale[section][num] = txt[:i+2]
                    txt = txt[i+2 + len(str(num)):]
                    continue
                elif i == 2 and d == 1:
                    j = txt.find(str(num),i+1)
                    self.scale[section][num] = txt[:j]
                    txt = txt[j + len(str(num)):]
                    continue
                elif i == 1 and d == -1:
                    if num > 13:
                        self.scale[section][num] = txt[:i+1]
                        txt = txt[i+1 + len(str(num)):]
                        continue
                elif i == -1:
                    continue

                self.scale[section][num] = txt[:i]
                txt = txt[i + len(str(num)):]

            #formatting
            for num in range(36,0,-1):
                try:
                    _str = self.scale[section][num]
                    self.scale[section][num] = int(_str)
                except(ValueError):
                    d = _str.find('-')
                    if d > 0:
                        self.scale[section][num] = range(int(_str[:d]),
                                                         int(_str[d+1:])+1)
                except(KeyError):
                    pass
                

    #Takes in a list of sections.
    #Prints answers in a readable manner.
    def printAnswers(self, inList):
        for section in inList:
            print(section)
            high = len(self.answers[section]) + 1
            for low in range(1,6):
                for num in range(low,high,5):
                    print(self.answers[section][num], " ", end="")
                print("\n")


    #Takes a string such as AFBGCH.. and sets all test answers.
    def enterAnswers(self, inStr):
        for sec in self.student:
            for num in range(1,self.secLens[sec]+1):
                self.student[sec][num] = inStr[0]
                inStr = inStr[1:]


    #Generates random answers to be used for testing.
    def randomTest(self):
        import random
        sample1 = 'ABCDE'
        sample2 = 'FGHJK'
        total = sum(self.secLens.values())
        ans = ''
        
        for q in range(1,total+1):
            if q % 2 == 1:
                ans += random.choice(sample1)
            else:
                ans += random.choice(sample2)

            if q == 60:
                sample1 = sample1[:-1]
                sample2 = sample2[:-1]

        #re-order so English ans go first.
        ans = ans[60:135] + ans[:60] + ans[135:]
        return(ans)


    #Checks student's answers vs answer key.
    #Stores incorrect question num in mistakes.
    #Can be done over all sections or a subset.
    def checkTest(self):
        for sec,vals in self.student.items():
            for num in vals.keys():
                if self.answers[sec][num] != self.student[sec][num]:
                    self.mistakes[sec].append(num)
                self.mistakes[sec].sort()


    #Sets section scores using scale.
    #Score list will contain 5 scores, including the overall score.
    def setScores(self):
        for sec,vals in self.scale.items():
            c = self.secLens[sec] - len(self.mistakes[sec])
            for score,correct in vals.items():
                try:
                    if c == correct or c in correct:
                        self.scoreList.append(score)
                        break
                except(TypeError):
                    pass

        total = sum(self.scoreList)/len(self.scoreList)

        import math
        if total - math.floor(total) < 0.5:
            roundedTotal = math.floor(total)
        else:
            roundedTotal = math.ceil(total)
        self.scoreList.append(roundedTotal)

        
    #Saves dictionary attribute as json file.
    def saveAttribute(self, inAttr):
        name = self.filename + "_" + inAttr + ".json"
        
        import json
        with open(name, 'w') as f:
            if inAttr == "answers":
                json.dump(self.answers,f)
            elif inAttr == "scale":
                json.dump(self.scale,f)
            elif inAttr == "mistakes":
                json.dump(self.mistakes,f)

