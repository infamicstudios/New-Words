from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os.path
import tooltips

def calculateTextSize(string, font):
    metrics = QFontMetrics(font)
    boundingBox = metrics.boundingRect(string)

    return boundingBox.width(), boundingBox.height()





class wordElement(QWidget):
    def __init__(self, word_details, darkmode=False, parent=None): 
        super(wordElement, self).__init__(parent)

        word_details_key = ['stem', 'ending', 'code1', 'code2', 'form1',
        'form2', 'form3', 'case', 'number', 'tense', 'gender', 'interpretation']

        #Fill in any parts of the dict that were not defined when pasing,
        #for x in word_details_key:
            #try:
                #temp = word_details[x]
            #except KeyError:
                #word_details[x] = None
                

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


class LanguageSwapButton(QWidget):
    
    def __init__(self, darkmode=False, parent=None):
        super(LanguageSwapButton, self).__init__(parent)
        #QWidget.__init__(self, parent=parent)

        layout = QHBoxLayout(self)


        #svg from https://www.svgrepo.com/svg/208426/switch-swap
        switch_path = '../resources/switch-swap-svgrepo-com.svg'
 
        
        state_lbl = QLabel('English to Latin')

        switch_icn = QIcon(switch_path) 
        switch_btn = QPushButton(switch_icn, None,None)
        
        
        # If using osx darkmode
        if darkmode:
            state_lbl.setStyleSheet("QLabel { color : white; }")
            switch_btn.setStyleSheet("QPushButton {"
                                     "border: none;"
                                     "color : white;}")
        layout.addWidget(state_lbl)
        layout.addWidget(switch_btn)

"""class WordDefinition(QWidget):

    def __init__(self, word, definition, darkmode=False, parent=None):
        super(WordDefinition, self).__init__(parent)

        

        # Three layouts are used here, One primary vertical layout 
        # main_layout that contains the other two layouts. Within 
        # main_layout is closed_layout and expanded_layout.
        # closed_layout is essentially a tree header containing
        # the definition of the word and a button to expand and 
        # display expanded_layout. expanded_layout contains the other 
        # details of the word (inflections, gender, age etc).

        main_layout = QGridLayout(self)

        self.setAttribute(Qt.WA_DeleteOnClose)

        word_label= QLabel(word+':')
        word_label.setFont(QFont("Arial", 16))  
        main_layout.addWidget(word_label, 0, 0, Qt.AlignLeft)

        self.expand_btn = QPushButton('↓', None)
        self.expand_btn.clicked.connect(self.toggleDetails)
        main_layout.addWidget(self.expand_btn, 0, 1, Qt.AlignRight)

        delete_btn = QPushButton('x', None)
        delete_btn.clicked.connect(self.delete)
        main_layout.addWidget(delete_btn, 0, 2, Qt.AlignRight)

        definition_label = QLabel(str(definition['senses']))
        definition_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(definition_label, 1, 0, (Qt.AlignLeft | Qt.AlignTop))

        
        expanded_layout = QGridLayout()
        word_part_label1 = QLabel('Forms: %s' % (definition['orth']) )
        word_part_label2 = QLabel('Most Common Inflection: %s' %(definition['infls'][0]))
        search_for_sentance_btn = QPushButton('See example sentance', None)

        expanded_layout.addWidget(word_part_label1, 0, 0, (Qt.AlignLeft | Qt.AlignTop))
        expanded_layout.addWidget(word_part_label2, 1, 0, (Qt.AlignLeft | Qt.AlignTop))
        expanded_layout.addWidget(search_for_sentance_btn, 2, 0, (Qt.AlignLeft | Qt.AlignTop))

        self.expanded_widget = QWidget()
        self.expanded_widget.setLayout(expanded_layout)
        self.expanded_widget.hide()

        main_layout.addWidget(self.expanded_widget, 2, 0, (Qt.AlignLeft | Qt.AlignTop))

    # Toggle the visibility of the extra details of the word.
    def toggleDetails(self):
        
        # If visible
        if self.expanded_widget.isVisible():
            self.expanded_widget.hide()
            self.expand_btn.setText('↓')

        # If hidden
        else:
            self.expanded_widget.show()
            self.expand_btn.setText('↑')
    def delete(self):
        self.close()"""
        

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