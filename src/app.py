import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from customWidgets import ButtonLineEdit, wordElement, ComplexWordElement, toolbarDropdowns
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
            self.DarkMode = True if subprocess.check_output(["defaults", 'read', '-g',
            'AppleInterfaceStyle']).decode("utf-8")  == 'Dark\n' else False
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
        self.center_container = QWidget()
        self.main_layout = QVBoxLayout()

        self.setCentralWidget(self.center_container)
        self.center_container.setLayout(self.main_layout)

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
        output = subprocess.check_output(['./words', word], cwd = '../resources/words/')
        if searchtype == 'Latin to English':
            output = subprocess.check_output(['./words', word], cwd = '../resources/words/')
        if searchtype == 'English to Latin':
            output = subprocess.check_output(['./words', '-E', word], cwd = '../resources/words/')
        output = output.decode("utf-8")
        if resultsmode == "Complex results" :
            self.main_layout.addWidget(ComplexWordElement(output))
        else:
            responses = response(output).parseresponse()
            wordheader = QWidget()
            header_layout = QGridLayout()
            wordheader.setLayout(header_layout)
            header_layout.addWidget(QLabel(self.search_le.text()), 0, 0)
            minimizeButton = QPushButton('Collapse')
            
            header_layout.addWidget(minimizeButton, 0, 1)

            contentWidget = QWidget()
            contentGrid =  QVBoxLayout()
            contentWidget.setLayout(contentGrid)

            header_layout.addWidget(contentWidget, 1, 0)

            self.main_layout.addWidget(wordheader)
            for details in responses:
                contentGrid.addWidget(wordElement(details))
                #self.main_layout.addWidget(wordElement(details))



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
