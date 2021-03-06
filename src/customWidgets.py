#TODO: ACTUALLY IMPORT EVERYTHING FROM INSTEAD OF BEING LAZY
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os.path
import tooltips
import settings
import regex as re



def calculateTextSize(string, font):
    metrics = QFontMetrics(font)
    boundingBox = metrics.boundingRect(string)

    return boundingBox.width(), boundingBox.height()

class definition(QWidget):
    def __init__(self, word, response, simple=False, darkmode=False, parent=None):
        super(definition, self).__init__(parent)
        
        #  Basic widget structure:
        #  |--------------------definition_header----------------------|
        #  ||----------------|  |------------------|  |--------------| |
        #  ||     Title      |  |  collapsebutton  |  |  CloseButton | |
        #  ||----------------|  |------------------|  |--------------| |
        #  |----------------------contentWidget------------------------|
        #  |                                                           |
        #  |                                                           |
        #  |                     definitionLabel                       |
        #  |                                                           |
        #  |                                                           |
        #  |-----------------------------------------------------------|

        # Get the background color and create a version of it that is slightly darker
        background_light = self.palette().color(self.backgroundRole()).name()
        background_dark = background_light[1:]
        background_dark = '#%02x%02x%02x' % tuple(int(int('0x'+background_dark[i:i+2], 0)/1.1) for i in range(0, len(background_dark), 2))
        self.selected = False

        #The overall layout for the whole widget
        definitionLayout = QGridLayout()
        self.setLayout(definitionLayout)

        # A header containing the word and expand/collapse and close buttons
        definition_header = QWidget()
        definition_header_layout = QHBoxLayout()
        definition_header.setLayout(definition_header_layout)
        self.word = word
        title = QLabel(word)
        #print(title.name)
        titlefont = QFont("Helvetica", 20, True)
        title.setFont(titlefont)

        self.collapsebutton = QToolButton()
        self.collapsebutton.setFixedSize(QSize(30,30))

        #Images from https://visualpharm.com/free-icons/collapse%20arrow-595b40b65ba036ed117d1768
        # and https://visualpharm.com/free-icons/expand%20arrow-595b40b65ba036ed117d1765

        # A nice single liner that defines the path of the CollapseButton Icon based on if using dark mode.
        collapse_icnpath, expand_icnpath = ['../resources/{type}{ifdark}'.format(ifdark='Dark' if darkmode else '', type='Expand' if i else 'Collapse') for i in range(2)]

        btnsize = 28 # btnsize % 2 must == 0 for it to properly display

        self.expand_icn = QIcon()
        self.expand_icn.addFile(expand_icnpath, QSize(btnsize, btnsize))
        self.collapse_icn = QIcon()
        self.collapse_icn.addFile(collapse_icnpath, QSize(btnsize, btnsize))

        self.collapsebutton.setStyleSheet(
            'QToolButton { background-color:'+background_dark+';'
                'border-radius:'+str(btnsize/2)+';' # Must be half the buttonsize 
            '}'
            'QToolButton:hover {'
                'background-color:'+background_dark+';'
                'border: 1px solid 	#0087BD;' 
            '}')
        self.collapsebutton.setToolTip('Show the details of this word')
        self.collapsebutton.clicked.connect(self.showDetails)

        closebutton = QPushButton('X')
        closebutton.setFixedSize(QSize(28,28))
        closebutton.setStyleSheet(
            'QPushButton {'
                'background-color:'+background_dark+';'
                'border-radius: 14px;' # Must be half the buttonsize
            '}'
            'QPushButton:hover {'
                'background-color:'+background_dark+';'
                'border: 1px solid red;'
            '}')
        closebutton.setToolTip('Remove')

        detailsButton = QPushButton('...')
        detailsButton.setFixedSize(QSize(28,28))
        detailsButton.setStyleSheet(
            'QPushButton {'
                'background-color:'+background_dark+';'
                'border-radius: 14px;' # Must be half the buttonsize
            '}'
            'QPushButton:hover {'
                'background-color:'+background_dark+';'
                'border: 1px solid red;'
            '}')

        detailsButton.clicked.connect(self.findExampleSentance)
        closebutton.clicked.connect(self.remove)

        definition_header_layout.addWidget(title, Qt.AlignLeft)
        definition_header_layout.addWidget(self.collapsebutton, Qt.AlignRight)
        definition_header_layout.addWidget(closebutton,Qt.AlignRight)
        definition_header_layout.addWidget(detailsButton,Qt.AlignRight)
        

        definitionLayout.addWidget(definition_header)
        # END OF HEADER

        # CREATE CONTENT WIDGET

        # For now always assume complex results
        response = response.rstrip('\r\n')
        
        # Highlight translations
        if settings.definition_highlighting:
            responseDef = re.findall("(.+)[;]", response)
            highlightStyle = {'bold':'b', 'italics':'i', 'normal':'', 'b':'b', 'i':'i'}
            style_letter = highlightStyle[settings.definition_hl_style.lower()]
            hl_color = '#C0C0C0' if settings.definition_hl_clr == None else settings.definition_hl_clr
            for word_form_def in responseDef:
                response = response.replace(word_form_def+';', 
                '<font color={hl_color}><{style_lttr}>{translation}</{style_lttr}></font>'.format(
                hl_color=hl_color, style_lttr=style_letter,
                translation=word_form_def))

            # This works for some reason
            response = '<br>'.join(response.splitlines())
        
        
        print(response)
            #response = ''.join()
        self.contentWidget = QLabel(response)
        #self.contentWidget.setText()
        #self.contentWidget.setFont(QFont('Arial', 13, True))
        self.contentWidget.setStyleSheet('padding: 10px; border-radius: 7px; background-color:{bg_dark};'.format(bg_dark=background_dark))

        # Hide the definition based on setting choice
        if not settings.showdefinitions:
            self.contentWidget.hide()
    
        if self.contentWidget.isHidden():
            self.collapsebutton.setIcon(self.expand_icn)
        else:
            self.collapsebutton.setIcon(self.collapse_icn)

        definitionLayout.addWidget(self.contentWidget, 1, 0)


    #Function that runs when the user expands on collapses the word details
    def showDetails(self):
        if self.contentWidget.isHidden():
            self.contentWidget.show()
            self.collapsebutton.setIcon(self.collapse_icn)
            self.collapsebutton.setToolTip('Collapse') 
        else:
            self.contentWidget.hide()
            self.collapsebutton.setIcon(self.expand_icn)
            self.collapsebutton.setToolTip('Expand') 
        
    def remove(self):
        self.setParent(None)
    def findExampleSentance(self):
        #TODO: Optimize as currently this is super slow
        with open('../textsamples/corpus.txt') as corpus:
            filetext = corpus.read()
            sentances = [s+ '.' for s in filetext.split('.') if self.word in s]
            sentance = min(sentances)
        print(sentance)




class History(QWidget):
    def __init__(self, darkmode=False, parent=None): 
        super(History, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        #self.setlayout(self.layout)

        self.header = QWidget()
        self.header_layout = QHBoxLayout()
        #header_layout.setContentsMargins(0,0,0,0)
        self.header.setLayout(self.header_layout)

        background_dark = self.palette().color(self.backgroundRole()).name()
        background_light = background_dark[1:]
        background_dark = '#%02x%02x%02x' % tuple(int(int('0x'+background_light[i:i+2], 0)/1.1) for i in range(0, len(background_light), 2))
        background_light = '#%02x%02x%02x' % tuple(int(int('0x'+background_light[i:i+2], 0)/.9) for i in range(0, len(background_light), 2))
        
        
        title = QLabel('History')
        title.setFont(
            QFont(settings.history_header_font, 
            settings.history_title_fntsize, 
            True))

        seperator = QFrame()
        seperator.setFrameStyle(QFrame.HLine | QFrame.Plain)

        clear_button = QPushButton('Clear')
        clear_button.setFont(
            QFont(settings.history_header_font,
            settings.history_clearbtn_fntsize,
            True))
        clear_button.setFixedSize(QSize(40,24))
        #TODO: make it so the tooltip shows the number of entries. 
        numentries = 1
        clear_button.setToolTip("Entries: %s" %(numentries))
        
        clear_button.setStyleSheet(
            'QPushButton {' 
                'border-radius: 5px;'
                'background-color:'+background_dark+';'
                'color:'+settings.history_clearbtn_fntcolor+';'
            '}'
            'QPushButton:hover {'
                'border-radius: 5px;'
                'background-color:'+background_light+';'
                'color:'+settings.history_clearbtn_fntcolor+';'
            '}')
        clear_button.clicked.connect(self.clear_history)
        self.header_layout.addWidget(title)
        self.header_layout.addWidget(seperator, Qt.AlignCenter)
        self.header_layout.addWidget(clear_button, Qt.AlignRight)

        self.layout.insertWidget(0, self.header)
    
    def clear_history(self):
        print("cleared")
        #TODO: Implement a feature to clear the history
        #for widgetindex in range(self.layout.count()-1):
            #widgetitem = self.layout.itemAt(widgetindex)
            #widget_elem = widgetitem.widget()
            #if widget_elem != None:
                #widgetelem = self.layout.itemAt(widgetindex)
                #self.layout.removeWidget(widget_elem)
        #self.layout.insertWidget(0, self.header)


        

class wordElement(QWidget):
    def __init__(self, word_details, darkmode=False, parent=None): 
        super(wordElement, self).__init__(parent)

        word_details_key = ['stem', 'ending', 'code1', 'code2', 'form1',
        'form2', 'form3', 'case', 'number', 'tense', 'gender', 'interpretation']

        ######### SET VARIABLE VALUE BY READING THE DICT #########
        self.stem = word_details['stem']
        self.ending = word_details['ending']
        self.word_type = word_details['type']
        self.code1 = word_details['code1']
        self.code2 = word_details['code2']
        self.form1 = word_details['form1']
        self.form2 = word_details['form2']
        self.form3 = word_details['form3']
        self.case = word_details['case']
        self.number = word_details['number']
        self.tense = word_details['tense']
        self.gender = word_details['gender']
        self.interpretation = word_details['interpretation']
        
        grid = QGridLayout(self)

        ######### WIDGET CONTAINING STEM AND ENDING      #########
        wordwidget = QWidget()
        word_grid = QGridLayout()

        stem_label = QLabel(self.stem)
        ending_value = QLabel(self.ending)
        word_grid.addWidget(stem_label, 0, 0, Qt.AlignLeft)
        word_grid.addWidget(ending_value, 0, 1, Qt.AlignLeft)

        wordwidget.setLayout(word_grid)
        grid.addWidget(wordwidget, 0, 0, Qt.AlignLeft)


        ######### WIDGET CONTAINING DETAILS ABOUT THE WORD #########
        textsize = 14
        current_font = QFont("Arial", textsize)
        details_width, details_height = calculateTextSize(self.word_type, current_font)
        details_width = details_width + 15
        backgroundcolor = self.palette().color(self.backgroundRole())

        #QWidget does not have a setpixmap attribute
        detailswidget = QLabel()
    
        pixelmap = QPixmap(QSize(details_width, details_height))
        pixelmap.fill(backgroundcolor)

        painter = QPainter()
        painter.begin(pixelmap)

        #make sure antialiasing is enabled otherwise it will look aweful
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()

        # Create the fancy looking polygon that will inclose the grammatical
        # type of the word
        word_type_section = QPolygonF([QPointF(0, details_height/2), 
                                     QPointF(10,0),
                                     QPointF(details_width, 0),
                                     QPointF(details_width, details_height),
                                     QPointF(10, details_height),
                                     QPointF(0, details_height/2)])

        path.addPolygon(word_type_section)

        #TODO: change the color of this to something pleasant on the eyes
        painter.fillPath(path, QBrush(Qt.green))

        painter.setFont( current_font )
        painter.setPen(backgroundcolor)
        painter.drawText(10, details_height/2+textsize/2.5, self.word_type)
        painter.end()
        detailswidget.setPixmap(pixelmap)
        grid.addWidget(detailswidget, 0, 1, Qt.AlignRight)
        deleteButton = QPushButton("X", None)
        deleteButton.clicked.connect(self.remove)
        grid.addWidget(deleteButton, 0, 2, Qt.AlignLeft)
    
    def remove(self):
        self.setParent(None)

class ComplexWordElement(QWidget):
    def __init__(self, response, darkmode=False, parent=None): 
        super(ComplexWordElement, self).__init__(parent)

        grid = QGridLayout(self)

        contentsWidget = QLabel(response)
        grid.addWidget(contentsWidget, 0, 0, Qt.AlignLeft)

        deleteButton = QPushButton("X", None)
        deleteButton.clicked.connect(self.remove)
        grid.addWidget(deleteButton, 0, 1, Qt.AlignRight)

    def remove(self):
        self.setParent(None)

class toolbarDropdowns(QWidget):
    def __init__(self, darkmode=False, parent=None): 
        super(toolbarDropdowns, self).__init__(parent)

        self.gridlayout = QGridLayout()
        self.setLayout(self.gridlayout)
        self.gridlayout.setVerticalSpacing(1)

        self.searchtype = QComboBox()
        self.searchtype.setFrame(False)
        self.searchtype.addItem("Latin to English")
        self.searchtype.addItem("English to Latin")
        self.searchtype.currentTextChanged.connect(self.change_response_type)

        self.responsetype = QComboBox()
        self.responsetype.setFrame(False)
        self.responsetype.addItem("Simple results")
        self.responsetype.addItem("Complex results")

        self.gridlayout.addWidget(self.searchtype, 0,0, Qt.AlignBottom )
        self.gridlayout.addWidget(self.responsetype, 1,0, Qt.AlignTop)

    def change_response_type(self, value):
        # Because simple mode for English to Latin is not supported,
        # automatically swap the user over to complex mode on change
        self.responsetype.clear()
        if value == 'English to Latin':
            self.responsetype.addItem("Complex results")
        elif value == 'Latin to English':
            self.responsetype.addItem("Complex results")
            self.responsetype.addItem("Simple results")
            
    def returndetails(self):
        return(self.searchtype.currentText(), self.responsetype.currentText())

class ButtonLineEdit(QLineEdit):
    #Modified line edit class Containing a line edit and a search and clear button
    buttonClicked = pyqtSignal(bool)

    def __init__(self, icon_file, darkmode = False, parent=None):
        super(ButtonLineEdit, self).__init__(parent)


        # Use Special SVG's designed for Darkmode if it is being used
        if darkmode:
            old_icon_file = icon_file
            icon_file = icon_file.split('/')
            icon_file.insert(-1, 'Darkmode')
            icon_file = '/'.join(icon_file)
            if not os.path.isfile(icon_file):
                icon_file = old_icon_file

        
        # Group containing the clear and search buttons 
        self.buttongroup = QWidget(self)
        self.buttongroupLayout = QGridLayout()
        self.buttongroup.setLayout(self.buttongroupLayout)

        # Create the clear button and use showclearbutton() to show/hide 
        # it depending on if QLineEdit is not empty
        self.clearbutton = QPushButton('X')
        self.clearbutton.setToolTip(tooltips.searchclear_tp)
        self.clearbutton.setStyleSheet('border: 0px; padding: 0px;')

        self.clearbutton.setCursor(Qt.ArrowCursor)
        self.clearbutton.clicked.connect(self.clearentry)
        self.textChanged.connect(self.showclearbutton)
        
        # The Search button
        self.Searchbutton = QToolButton()
        self.Searchbutton.setIcon(QIcon(icon_file))
        self.Searchbutton.setToolTip(tooltips.search_tp)
        self.Searchbutton.setStyleSheet('border: 0px; padding: 0px;')
        self.Searchbutton.setCursor(Qt.ArrowCursor)
        self.Searchbutton.clicked.connect(self.buttonClicked.emit)

        self.buttongroupLayout.addWidget(self.clearbutton, 0, 0)
        self.buttongroupLayout.addWidget(self.Searchbutton, 0, 1, Qt.AlignRight)

        # Make sure styling is correct no matter the window size
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        buttonSize = self.buttongroup.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth*2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth*2 + 2))

    def resizeEvent(self, event):
        buttonSize = self.buttongroup.sizeHint()
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.buttongroup.move(self.rect().right() - frameWidth - buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1)/2)

        super(ButtonLineEdit, self).resizeEvent(event)

    def clearentry(self):
        self.clear()

    def showclearbutton(self):
        self.clearbutton.show() if len(self.text()) > 0 else self.clearbutton.hide()
