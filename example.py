from classes import TestClass

#Exmaple of full test grading

test = TestClass("act", "72c")
test.setSections(["english", "math", "reading", "science"])
test.setPagesFromUrl()
test.setAnswers()
test.setScale()

#Sample student
matthew = test.randomTest()
test.enterAnswers(matthew)

test.checkTest()
test.setScores()

print(repr(test))
