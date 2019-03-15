#TODO: ACTUALLY IMPORT EVERYTHING FROM INSTEAD OF BEING LAZY
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from customWidgets import ButtonLineEdit, wordElement, ComplexWordElement, toolbarDropdowns, definition
import subprocess
import regex as re
import settings
import tooltips

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = settings.title
        self.left = settings.left
        self.top = settings.top
        self.width = settings.width
        self.height = settings.height

        self.platform = sys.platform

        # Detect if using OSX dark mode for element styling
        if self.platform == 'darwin':
            try:
                self.DarkMode = True if subprocess.check_output(["defaults", 'read', '-g',
                'AppleInterfaceStyle']).decode("utf-8")  == 'Dark\n' else False
            except:
                self.DarkMode = False
        else:
            self.DarkMode = False
        
        self.resultsmode = 'Complex results'
        self.searchtype = 'Latin to English'
        self.initUI()

    def initUI(self):
       
        # Create and add various widgets to the toolbar
        self.tb = self.addToolBar('Toolbar')

        # Create the Searchbar widget
        searchicn_path = '../resources/magnifier-tool.svg'
        self.search_le = ButtonLineEdit(searchicn_path, self.DarkMode)
        self.search_le.buttonClicked.connect(self.searchword)
        self.search_le.returnPressed.connect(self.searchword)
        self.search_le.setPlaceholderText('Search')
        self.search_le.setToolTip(tooltips.searchwidget_tp)

        searchdetails = QWidget()
        searchdetailsLayout = QGridLayout()
        searchdetails.setLayout(searchdetailsLayout)

        # Create the Language swap and results style dropdown widgets
        self.searchdets = toolbarDropdowns()

        self.tb.addWidget(self.searchdets)

        self.tb.addWidget(self.search_le)

        # Create and configure the body container of the widget
        self.scroll_area = QScrollArea()
        self.center_container = QWidget()
        self.main_layout = QVBoxLayout()
        self.center_container.setLayout(self.main_layout)
        

        self.scroll_area.setWidget(self.center_container)
        self.scroll_area.setWidgetResizable(True)

        self.setCentralWidget(self.scroll_area)
        

        recommendedSize = self.center_container.sizeHint()
        self.spacer = QSpacerItem(recommendedSize.width(), recommendedSize.height(), QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(self.spacer)

        #create the window title and size
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #Show Window
        self.show()
        
    def change_results_mode(self, value):
        self.resultsmode = value
    def change_search_type(self, value):
        # Because simple mode for English to Latin is not supported,
        # automatically swap the user over to complex mode on change
        self.responsemode.clear()
        if value == 'English to Latin':
            self.responsemode.addItem("Complex results")
        elif value == 'Latin to English':
            self.responsemode.addItem("Complex results")
            self.responsemode.addItem("Simple results")

        self.searchtype = value

    def searchword(self):
        searchtype, resultsmode = self.searchdets.returndetails()

        validdict = {}
        word = ''+self.search_le.text()
        command = ['./words', word] if searchtype == 'Latin to English' else ['./words', '-E', word]
        output = subprocess.check_output(command, cwd = '../resources/words/').decode("utf-8")

        
        definition_entry = definition(word, output, darkmode=self.DarkMode)

        # Check if the word is a duplicate of a word in the history
        # And if it is display a prompt asking about researching
        duplicate = False
        for entrynum in range(self.main_layout.count()):
            dictionaryentry = self.main_layout.itemAt(entrynum)
            if type(dictionaryentry) != QSpacerItem:
                dictionaryentry = dictionaryentry.widget()
                labels = dictionaryentry.findChildren(QLabel)[0]
                if labels.text() == word and not duplicate:
                    msg = QMessageBox()
                    msg.setText('This search matchs a word already in the history. Do you still wanna search for the word?')
                    msg.setWindowTitle('Duplicate warning')
                    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    #msg.buttonClicked.connect(self.buttonpressed)
                    retval = msg.exec_()
                    if retval == QMessageBox.Yes:
                        duplicate = False
                    if retval == QMessageBox.No:
                        duplicate = True
                    break
        
        if not duplicate:
            self.main_layout.insertWidget(0, definition_entry)

        # Have to re-add the spacer to the bottom.
        self.main_layout.removeItem(self.spacer)
        self.main_layout.addItem(self.spacer)    

    def buttonpressed(self, value):
        return False if value.text() == 'Yes' else True

class response():
    def __init__(self, responsestr):
        self.response = responsestr
        self.definitions = []
        self.elements = []

    def parseresponse(self):
        responselst = [s.replace('\r', '') for s in self.response.split('\n')]

        for line in responselst:
            matched = False

            ######### READ WORD VALUES OF LATIN WORDS FROM OUTPUT BASED ON THE WORD TYPE #########

            # Match adjective template
            groups = re.match('(\w+)(?:\.(\w+))?\s+ADJ\s+(\d)\s+(\d)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)', line)
            if groups != None:

                self.elements.append({'stem'   : groups.group(1),
                                      'ending' : groups.group(2),
                                      'type'   : 'ADJ',
                                      'code1'  : groups.group(3),
                                      'code2'  : groups.group(4),
                                      'case'   : groups.group(5),
                                      'number' : groups.group(6),
                                      'gender' : groups.group(7),
                                      'interpretation' : groups.group(8)})
                matched = True
            # Match Noun template
            groups = re.match('(\w+)(?:\.(\w+))?\s+N\s+(\d)\s+(\d)\s+(\w+)\s+(\w+)\s+(\w+)', line)
            if groups != None and matched != True :

                self.elements.append({'stem'   : groups.group(1), 
                                      'ending' : groups.group(2), 
                                      'type'   : 'Noun',
                                      'code1'  : groups.group(3),
                                      'code2'  : groups.group(4),
                                      'case'   : groups.group(5),
                                      'number' : groups.group(6),
                                      'gender' : groups.group(7)})

                matched = True
            # Match Pluperfect and present form Verb template 
            groups = re.match('(\w+)(?:\.(\w+))?\s+V\s+(\d)\s+(\d)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w)\s+(\w)', line)
            if groups != None and matched != True:
                self.elements.append({'stem'   : groups.group(1), 
                                      'ending' : groups.group(2), 
                                      'type'   : 'Verb',
                                      'code1'  : groups.group(3),
                                      'code2'  : groups.group(4),
                                      'form1'  : groups.group(5),
                                      'form2'  : groups.group(6),
                                      'form3'  : groups.group(7),
                                      'number' : groups.group(8),
                                      'tense'  : groups.group(9)})
                matched = True

            # Match Future form verbs this needs to be after Pluperfect and present form because
            # It will match those as well
            groups = re.match('(\w+)(?:\.(\w+))?\s+V\s+(\d)\s+(\d)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)', line)
            if groups != None and matched != True:
                self.elements.append({'stem'   : groups.group(1), 
                                      'ending' : groups.group(2), 
                                      'type'   : 'Verb',
                                      'code1'  : groups.group(3),
                                      'code2'  : groups.group(4),
                                      'form1'  : groups.group(5),
                                      'form3'  : groups.group(6),
                                      'number' : groups.group(7),
                                      'tense'  : groups.group(8)})
                matched = True
            # Match adverbs
            groups = re.match('(\w+)(?:\.(\w+))?\s+ADV\s+(\w+)', line)
            if groups != None and matched != True:
                self.elements.append({'stem'   : groups.group(1), 
                                      'ending' : groups.group(2), 
                                      'type'   : 'Adverb',
                                      'form1'  : groups.group(3)})
                matched = True
            
            # Match Conjunction
            groups = re.match('(\w+)(?:\.(\w+))?\s+CONJ', line)
            if groups != None and matched != True:
                self.elements.append({'stem'   : groups.group(1), 
                                      'ending' : groups.group(2), 
                                      'type'   : 'Conjunction'})
                matched = True

            # Match interjection
            groups = re.match('(\w+)(?:\.(\w+))?\s+INTERJ', line)
            if groups != None and matched != True:
                self.elements.append({'stem'   : groups.group(1), 
                                      'ending' : groups.group(2), 
                                      'type'   : 'Interjection'})
                matched = True

            # Match interjection
            groups = re.match('(\w+)(?:\.(\w+))?\s+TACKON', line)
            if groups != None and matched != True:
                self.elements.append({'stem'   : groups.group(1), 
                                      'ending' : groups.group(2), 
                                      'type'   : 'Tackon'})
                matched = True
            
        self.cleanelements()

        return self.elements

    # Could put this into the custom widget and it would be cleaner
    # but it makes more sense for it to be here.
    def cleanelements(self):
        word_details_key = ['stem', 'ending', 'code1', 'code2', 'form1',
        'form2', 'form3', 'case', 'number', 'tense', 'gender', 'interpretation']
        newelements = []

        for detaildict in self.elements:
            cleanedup = detaildict

            for x in word_details_key:
                try:
                    temp = cleanedup[x]
                except KeyError:
                    cleanedup[x] = None
            newelements.append(cleanedup)

        self.elements = newelements

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
