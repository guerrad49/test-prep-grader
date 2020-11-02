class TestClass:
    def __init__(self, _type, form):
        #_type currently only supports "act"
        self.type = _type
        #form number provided by user, ex. "72f"
        self.form = form
        self.url = "https://www.prepsharp.com/" + form
        self.filename = _type + "_" + form
        self.pages = []
        self.answers = {"english":{}, "math":{}, "reading":{}, "science":{}}
        self.student = {}
        self.mistakes = {}
        self.scale = {"english":{}, "math":{}, "reading":{}, "science":{}}
        self.secLens = {"english":75, "math":60, "reading":40, "science":40}
        self.scoreDict = {}


    def __repr__(self):
        output = ""

        #Display section title, mistakes and score for each section graded
        for section in self.mistakes:
            output += section + ": " + str(self.mistakes[section]) + "\n"
            output += "score: " + str(self.scoreDict[section]) + "\n\n"

        #If a full test was graded, additionally display composite score
        if len(self.scoreDict) == 5:
            output += "composite: " + str(self.scoreDict["composite"])
            
        return output
    
        
    #User sets sections, as a list, completed in test to be graded
    def setSections(self, inSecs=[]):
        for section in inSecs:
            self.student[section] = {}
            self.mistakes[section] = []
            self.scoreDict[section] = 0
            
    
    #Uses defined url to extract text of answers and scale from online pdf
    def setPagesFromUrl(self):
        import io, requests
        from PyPDF2 import PdfFileReader

        r = requests.get(self.url)
        f = io.BytesIO(r.content)
        pdf = PdfFileReader(f)

        #Online pdf contains 2 pages of data - answer key and scale
        for pageNum in range(2):
            pageObj = pdf.getPage(pageNum)
            pageTxt = pageObj.extractText()
            self.pages.append(pageTxt)


    #Takes answer key text (after selfPagesFromURL called) and stores answers
    #into structured dictionary
    def setAnswers(self):
        txt = self.pages[0]
        low = txt.find("1")
        high = txt.find("ACT") - 3
        txt = txt[low:high]

        #Algorithm for structuring plain text data
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


    #Takes scale text (after selfPagesFromURL called) and stores scale
    #into structured dictionary
    def setScale(self):
        txt = self.pages[1]

        #Algorithm for structuring plain text data
        for section in self.scale.keys():
            trim = txt.find("Score")
            txt = txt[trim + len("Score "):]

            for num in range(36,0,-1):
                i = txt.find(str(num),1,7)
                d = txt.find("-",0,3)

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

            #Additional formatting for easier use
            for num in range(36,0,-1):
                try:
                    _str = self.scale[section][num]
                    self.scale[section][num] = int(_str)
                except(ValueError):
                    d = _str.find("-")
                    if d > 0:
                        self.scale[section][num] = range(int(_str[:d]),
                                                         int(_str[d+1:])+1)
                except(KeyError):
                    pass
                

    #User provides a subset of sections, as a list, to be printed to screen
    def printAnswers(self, inList):
        dash = "-"*89
        for section in inList:
            print(dash)
            print(section)
            print(dash)
            totalQuestions = len(self.answers[section]) + 1

            #Loop to format answers in rows containing 15 answers each
            for questToStart in range(1,6):
                for num in range(questToStart,totalQuestions,5):
                    print('{:2d}{:1s}{:3s}'.format(num, ".", self.answers[section][num]), end="")
                print("\n")


    #Generates pseudo-random answers to be used as a mock test
    #Primarily used for self-testing
    def randomTest(self):
        import random

        #Sample space of accepted answers on ACT
        sample1 = "ABCDE"
        sample2 = "FGHJK"
        total = sum(self.secLens.values())
        ans = ""
        
        for question in range(1,total+1):
            if question % 2 == 1:
                ans += random.choice(sample1)
            else:
                ans += random.choice(sample2)

            #Delete E and K from sample space to match ACT
            if question == 60:
                sample1 = sample1[:-1]
                sample2 = sample2[:-1]

        #Re-order so English anwers go first
        ans = ans[60:135] + ans[:60] + ans[135:]
        return(ans)


    #User provides a long string of test answers to be graded
    def enterAnswers(self, inStr):

        #Algorithm for structuring provided string
        for sec in self.student:
            for num in range(1,self.secLens[sec]+1):
                self.student[sec][num] = inStr[0]
                inStr = inStr[1:]


    #Checks student answers vs answer key dictionary
    def checkTest(self):
        for sec,vals in self.student.items():
            for num in vals.keys():
                #If student answer doesn't match key, store number as mistake
                if self.answers[sec][num] != self.student[sec][num]:
                    self.mistakes[sec].append(num)
                self.mistakes[sec].sort()


    #Set section scores once test, partial or full, is graded
    def setScores(self):
        for sec,vals in self.scale.items():
            try:
                c = self.secLens[sec] - len(self.mistakes[sec])
                for score,correct in vals.items():
                    try:
                        if c == correct or c in correct:
                            self.scoreDict[sec] = score
                            break
                    except(TypeError):
                        pass
            except(KeyError):
                pass

        #If given a full test, compute and store composite score
        if len(self.mistakes) == 4:
            total = sum(self.scoreDict.values())/len(self.scoreDict)

            #Required to round composite score appropriately
            import math
            if total - math.floor(total) < 0.5:
                roundedTotal = math.floor(total)
            else:
                roundedTotal = math.ceil(total)
            self.scoreDict["composite"] = roundedTotal

        
    #User can save certain attributes as json file for record keeping
    #such as answers, scale, and mistakes
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

