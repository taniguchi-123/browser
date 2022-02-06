import os, time
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QToolBar,
    QVBoxLayout,
    QWidget
)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window = None  #to avoid showing BookmarkWindow unles clicked
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://google.com"))
        self.setCentralWidget(self.browser)

        # tag::navigationSignals[]
        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.update_title)
        # end::navigationSignals[]

        # tag::navigation1[]
        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        back_btn = QAction(QIcon(os.path.join("icons", "arrow-180.png")), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)
        # end::navigation1[]

        # tag::navigation2[]
        next_btn = QAction(
            QIcon(os.path.join("icons", "arrow-000.png")), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)

        reload_btn = QAction(
            QIcon(os.path.join("icons", "arrow-circle-315.png")), "Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon(os.path.join("icons", "home.png")), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)
        # end::navigation2[]
        
        
        #bookmark button    
        bookmark_btn = QAction(QIcon(os.path.join("icons", "plus.png")), "Bookmark", self)
        bookmark_btn.setStatusTip("add to bookmark")
        bookmark_btn.triggered.connect(self.bookmark_clicked)
        navtb.addAction(bookmark_btn)        
        navtb.addSeparator()
        
        
        navtb.addSeparator()

        # tag::navigation3[]
        self.httpsicon = QLabel()  
        self.httpsicon.setPixmap(QPixmap(os.path.join("icons", "lock-nossl.png")))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(
            QIcon(os.path.join("icons", "cross-circle.png")), "Stop", self
        )
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(self.browser.stop)
        navtb.addAction(stop_btn)
        # end::navigation3[]
        
        

        self.menuBar().setNativeMenuBar(False)
        self.statusBar()

        # tag::menuFile[]
        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(
            QIcon(os.path.join("icons", "disk--arrow.png")), "Open file...", self
        )
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(
            QIcon(os.path.join("icons", "disk--pencil.png")), "Save Page As...", self
        )
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)
        # end::menuFile[]

        # tag::menuPrint[]
        print_action = QAction(
            QIcon(os.path.join("icons", "printer.png")), "Print...", self
        )
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        # Create our system printer instance.
        self.printer = QPrinter()
        # end::menuPrint[]
        
        
        # menuBookmark[]
        global bookmarks
        bookmarks = []    
        self.readSettings()
        
        
        self.show()
        self.setWindowIcon(QIcon(os.path.join("icons", "ma-icon-64.png")))

    # tag::navigationTitle[]
    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle("%s - Browser" % title)
    # end::navigationTitle[]

     
    # tag::menuFilefnOpen[]
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "Hypertext Markup Language (*.htm *.html);;" "All files (*.*)",
        )

        if filename:
            with open(filename, "r") as f:
                html = f.read()

            self.browser.setHtml(html)
            self.urlbar.setText(filename)
    # end::menuFilefnOpen[]

    # tag::menuFilefnSave[]
    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Page As",
            "",
            "Hypertext Markup Language (*.htm *html);;" "All files (*.*)",
        )

        if filename:
            # Define callback method to handle the write.
            def writer(html):
                with open(filename, "w") as f:
                    f.write(html)
            self.browser.page().toHtml(writer)
    # end::menuFilefnSave[]

    # tag::menuPrintfn[]
    def print_page(self):
        page = self.browser.page()

        def callback(*args):
            pass

        dlg = QPrintDialog(self.printer)
        dlg.accepted.connect(callback)
        if dlg.exec_() == QDialog.Accepted:
            page.print(self.printer, callback)
    # end::menuPrintfn[]

    # tag::navigationHome[]
    def navigate_home(self):
        self.browser.setUrl(QUrl("http://www.google.com"))
    # end::navigationHome[]

    # tag::navigationURL[]
    def navigate_to_url(self):  # Does not receive the Url
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.browser.setUrl(q)
    # end::navigationURL[]

    # tag::navigationURLBar[]
    def update_urlbar(self, q):

        if q.scheme() == "https":
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join("icons", "lock-ssl.png")))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join("icons", "lock-nossl.png")))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)
    # end::navigationURLBar[]
    
    
    def bookmark_clicked(self):
        bookmark_title = self.browser.page().title()
        bookmark_url = self.browser.url().toString()
        x =[bookmark_title,bookmark_url]
        bookmarks = self.new_items
        bookmarks.append(x)
        bookmark_select_action = QAction(bookmark_title,self)
        bookmark_select_action.triggered.connect(self.navigate_bookmark)
        self.bookmark_menu.addAction(bookmark_select_action)
        
        settings = QtCore.QSettings('test', 'browser')
        self.new_item = settings.value('bookmarks', [])
        self.new_item.append(x)
        settings.setValue('bookmarks', self.new_item)
        
        #update 2nd window list  (under debugging, not updated somehow...)
        subwindow.update_list()
        
    def navigate_bookmark(self):
        title_text = self.sender().text()
        bookmarks = self.new_items
        #print(bookmarks)
        for item in range(len(bookmarks)):
            if bookmarks[item][0] == title_text:
                address = bookmarks[item][1]    
                self.browser.setUrl(QUrl(address))
                break
            
    def showNewWindow(self):
        self.window = None   #211222　updated to avoid duble click for operation
        #print(self.window)
        if self.window is None:
            self.window = BookmarkWindow()
            self.window.show()
        else:
            self.window = None    #discard reference
        
    def closeEvent(self, event):
        setting = QtCore.QSettings('test', 'browser')
        setting.setValue("bookmarks", self.new_items)
        
 
    def readSettings(self):
        setting = QtCore.QSettings('test', 'browser')
        self.new_items = setting.value('bookmarks', [])      
        self.setBoorkMarkMenu()
        self.setBoorkMarkItems(setting.value("bookmarks", []))
        
            
    def setBoorkMarkMenu(self):
        self.bookmark_menu = self.menuBar().addMenu("&Bookmark")
        bookmark_manage_action = QAction("ブックマークの管理",self)
        bookmark_manage_action.triggered.connect(self.showNewWindow)
        self.bookmark_menu.addAction(bookmark_manage_action)

    def updateBoorkMarkMenu(self):
        bookmark_manage_action = QAction("ブックマークの管理",self)
        bookmark_manage_action.triggered.connect(self.showNewWindow)
        self.bookmark_menu.addAction(bookmark_manage_action)
        self.setBoorkMarkItems(self.new_items)
        
        
    def setBoorkMarkItems(self,bookmarks):      #from this 'bookmarks' has 'self.new_items' data inside
        global qty 
        qty = len(bookmarks)
        for item in range(qty):
            name = bookmarks[item][0]
            bookmark_select_action = QAction(name,self)
            bookmark_select_action.triggered.connect(self.navigate_bookmark)
            self.bookmark_menu.addAction(bookmark_select_action)
                        
    def removeBookmarkMenu(self):
        self.bookmark_menu.clear()   
        self.updateBoorkMarkMenu()
        
    
class BookmarkWindow(QWidget):
    """this is 2nd window """    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        bookmarks = window.new_items    #get information from MainWindow()
        
        self.del_button = QtWidgets.QPushButton('Delete')
        self.del_button.clicked.connect(self.delete_event)
        self.layout.addWidget(self.del_button)
        
        self.update_button = QtWidgets.QPushButton('update')
        self.update_button.clicked.connect(self.update_list)
        self.layout.addWidget(self.update_button)
        
        self.itemlist = QtWidgets.QListWidget()
        for item in range(qty):
            self.itemlist.addItem(bookmarks[item][0])
        self.layout.addWidget(self.itemlist)
        self.setLayout(self.layout)

 
    def update_list(self):
        bookmarks = window.new_items
        
        #from here update itemlist on 2nd window
        self.itemlist.clear()
        
        qty = len(bookmarks)
        for item in range(qty):
            self.itemlist.addItem(bookmarks[item][0])
        self.layout.addWidget(self.itemlist)        
        
    
    def delete_event(self):
        bookmarks = window.new_items
        if len(bookmarks)>0:
            row = self.itemlist.currentRow()
            del(bookmarks[row])
            
            ##self.populate_list(bookmarks)
            window.removeBookmarkMenu()
            
            #from here update itemlist on 2nd window
            self.itemlist.clear()
            qty = len(bookmarks)
            for item in range(qty):
                self.itemlist.addItem(bookmarks[item][0])
            self.layout.addWidget(self.itemlist)
                    
    def closeEvent(self, event):
        self.window = None
        
app = QApplication(sys.argv)
app.setApplicationName("Browser")

window = MainWindow()
subwindow = BookmarkWindow()

app.exec_()
