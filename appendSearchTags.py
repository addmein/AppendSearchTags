# -*- coding: utf-8 -*-
import wx, os, logging
from lxml import etree as ET
from requests.utils import quote

logger = logging.getLogger(__name__)

class Example(wx.Frame):
    
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
            size=(500,645))
        
        self.InitUI()
        self.Centre()
        self.Show()        
            
    def InitUI(self):
        width = 440
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#EDFAFA')
        
        sizer = wx.GridBagSizer(5,5)
        
        text1 = wx.StaticText(panel, label="This application will add the search tags to the .ncx located in the working folder.\n\nPlease choose the folder where the .ncx file is located.")
        sizer.Add(text1, pos=(0, 0), span=(1,5), 
            flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
        text1.Wrap(width)
        
        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1,0), span=(1,5), 
            flag=wx.EXPAND|wx.BOTTOM, border = 10)
        
        dp1 = wx.DirPickerCtrl(panel, -1, message="Choose folder:", style=wx.DIRP_DIR_MUST_EXIST|wx.DIRP_USE_TEXTCTRL)
        sizer.Add(dp1, pos=(2,1), span=(1,4), flag=wx.TOP|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        self.Bind(wx.EVT_DIRPICKER_CHANGED, self.OnBrowse, dp1)
        
        text2 = wx.StaticText(panel, label="Folder path:")
        sizer.Add(text2, pos=(2, 0), span=(1,1), flag=wx.LEFT|wx.TOP, border=5)
                
        button2 = wx.Button(panel, label='Start')
        sizer.Add(button2, pos=(4,2), span=(1,1), flag=wx.BOTTOM|wx.RIGHT)
        
        button2.Bind(wx.EVT_BUTTON, self.OnStart)
        
        button3 = wx.Button(panel, label='Quit')
        sizer.Add(button3, pos=(4,3), span=(1,1), flag=wx.BOTTOM|wx.RIGHT)
        
        button3.Bind(wx.EVT_BUTTON, self.OnQuit)
        
        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(5,0), span=(1,5), 
            flag=wx.EXPAND|wx.BOTTOM, border = 10)
        
        log = wx.TextCtrl(panel, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        sizer.Add(log, pos=(6,0), span=(18,5), flag=wx.TOP|wx.EXPAND, border=10)
        
        handler = WxTextCtrlHandler(log)
        logger.addHandler(handler)
        FORMAT = "%(asctime)s --- %(levelname)s --- %(message)s"
        handler.setFormatter(logging.Formatter(FORMAT))
        logger.setLevel(logging.DEBUG)
        
        
        sizer.AddGrowableCol(2)
        
        panel.SetSizer(sizer)
        
    def OnQuit(self, e):
        self.Close(True)
        
    def OnStart(self, e):
        #print path
        a = ProcessFiles()
        a.ProcFiles(path)
        a.ShowMessageFinished()
        
        
    def OnBrowse(self, e):
        global path
        path = e.GetPath()
        return path

    
    
    
class ProcessFiles():
    
    def ProcFiles(self, dir):
        print dir
        textpath = os.path.join(dir, "Text")
        print textpath
        i = 0
        for file in os.listdir(textpath):
            logger.log(logging.INFO, "Processing file  ==>  %s" %file)
            print "Processing file  ==>  %s" %file
            if file.endswith(".xhtml"):
                f = os.path.join(textpath,file)
                tree = ET.parse(f)
                root = tree.getroot()
                #print root
                searcharr = []
                searchtext = None
                for node in root.findall('.//'):
                    print node
                    try:
                        if ((node.tag == "{http://www.w3.org/1999/xhtml}span") or (node.tag == "{http://www.w3.org/1999/xhtml}p") or (node.tag == "{http://www.w3.org/1999/xhtml}h2")) and ("H2" in node.attrib['class']) and (node.text != None):
                            print "%s --> %s" %(node.attrib['class'], node.text)
                            logger.log(logging.INFO, "Class: H2. Text: %s" % node.text)
                            print "Class: H2. Text: %s" % node.text
                            searcharr.append(node.text)
                            searchtext = ', '.join(searcharr)
                            i += 1
                    except:
                        pass
                    
                if searchtext != None:
                    print "Found H2 in file: %s. Search text: %s" % (file, searchtext)
                    logger.log(logging.INFO, "Found H2 in file: %s. Search text: %s" % (file, searchtext))
                    a.insertSearchTag(dir, file, searchtext)

                    
            logger.log(logging.INFO, "The file %s was CHECKED." %file)
        logger.log(logging.INFO, "TASK FINISHED.")
        print "TASK FINISHED."
    
    def insertSearchTag(self, dir, filename, text):
        ncx = os.path.join(dir, 'toc.ncx')
        tree = ET.parse(ncx)
        root = tree.getroot()
        #print root.tag
        print "GOT ROOT NCX"
        filename = quote(filename, safe='')
        for content in root.iter("{http://www.daisy.org/z3986/2005/ncx/}content"):
            #print filename.lower()[:-6]
            #print content.attrib['src'].lower()
            if filename.lower() in content.attrib['src'].lower():
                parent = content.getparent()
                print "Parent: %s." %parent
                parent[0].append(ET.Element("search"))
                print parent[0]
                print parent[0][0].tag
                parent[0][1].text = text
                print "text"
                print "Text: %s " % text

        tree.write(ncx, encoding="utf-8") # Default encoding is ascii. utf-8 is used so that while writing, the special characters will remain the same.
        print "The TOC.ncx file is updated."
        logger.log(logging.INFO, "The TOC.ncx file is updated.")

            
    def ShowMessageFinished(self):
        wx.MessageBox('Finished!', 'Info',
            wx.OK | wx.ICON_INFORMATION)
            
a = ProcessFiles()            

class WxTextCtrlHandler(logging.Handler):
    
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl
        
    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.WriteText, s)
        
LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL
]

            
    
if __name__ == '__main__':
    
    app = wx.App()
    Example(None, title='Add Search Tags')
    app.MainLoop()
