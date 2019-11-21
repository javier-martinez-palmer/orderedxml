'''
WHY OF THIS MODULE?
1) it loads/writes xml files while keeping the original order
2) no extra dependencies
3) deals properly with the encoding
4) respects comments in the original xml
'''

import os
import sys
import codecs
import imp
from collections import OrderedDict

from . import chardet
from chardet.universaldetector import UniversalDetector

'''
https://stackoverflow.com/questions/2741480/can-elementtree-be-told-to-preserve-the-order-of-attributes
'''
'''
https://stackoverflow.com/questions/2741480/can-elementtree-be-told-to-preserve-the-order-of-attributes/47422944#47422944
'''
'''
https://github.com/martinblech/xmltodict
'''
'''
https://stackoverflow.com/questions/11170949/how-to-make-a-copy-of-a-python-module-at-runtime
'''

# in order to patch the module without changing the original
# we must import a copy
# import xml.etree.ElementTree as ET
# This way we can import this module and patch it safely
xml_patched=imp.load_module('xml_patched', *imp.find_module('xml'))
from xml_patched.etree import ElementTree as ET

# further imports of the default xml module  
# will import a new module in sys.modules 


# =======================================================================
# Patch ElementTree to allow us write ordered
def _serialize_xml(write, elem, encoding, qnames, namespaces):
    tag = elem.tag
    text = elem.text
    if tag is ET.Comment:
        write("<!--%s-->" % ET._encode(text, encoding))
    elif tag is ET.ProcessingInstruction:
        write("<?%s?>" % ET._encode(text, encoding))
    else:
        tag = qnames[tag]
        if tag is None:
            if text:
                write(ET._escape_cdata(text, encoding))
            for e in elem:
                _serialize_xml(write, e, encoding, qnames, None)
        else:
            write("<" + tag)
            items = elem.items()
            if items or namespaces:
                if namespaces:
                    for v, k in sorted(namespaces.items(),
                                       key=lambda x: x[1]):  # sort on prefix
                        if k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k.encode(encoding),
                            ET._escape_attrib(v, encoding)
                            ))
                #for k, v in sorted(items):  # lexical order
                for k, v in items: # Monkey patch
                    if isinstance(k, ET.QName):
                        k = k.text
                    if isinstance(v, ET.QName):
                        v = qnames[v.text]
                    else:
                        v = ET._escape_attrib(v, encoding)
                    write(" %s=\"%s\"" % (qnames[k], v))
            if text or len(elem):
                write(">")
                if text:
                    write(ET._escape_cdata(text, encoding))
                for e in elem:
                    _serialize_xml(write, e, encoding, qnames, None)
                write("</" + tag + ">")
            else:
                write(" />")
    if elem.tail:
        write(ET._escape_cdata(elem.tail, encoding))
        
ET._serialize_xml = _serialize_xml
ET._serialize['xml'] = _serialize_xml




class OrderedXMLTreeBuilder(ET.XMLTreeBuilder):
    def __init__(self, *args, **kwargs):
        super(OrderedXMLTreeBuilder, self).__init__(*args, **kwargs)
        self._parser.CommentHandler = self.comment

    def _start_list(self, tag, attrib_in):
        fixname = self._fixname
        tag = fixname(tag)
        attrib = OrderedDict()
        if attrib_in:
            for i in range(0, len(attrib_in), 2):
                attrib[fixname(attrib_in[i])] = self._fixtext(attrib_in[i+1])
        return self._target.start(tag, attrib)

    def comment(self, data):
        self._target.start(ET.Comment, OrderedDict())
        self._target.data(data)
        self._target.end(ET.Comment)


# Make sorted() a no-op for the ElementTree module
ET.sorted = lambda x: x


try:
    # python3 use a cPython implementation by default, prevent that
    ET.Element = ET._Element_Py
    # similarly, override SubElement method if desired
    def SubElement(parent, tag, attrib=OrderedDict(), **extra):
        attrib = attrib.copy()
        attrib.update(extra)
        element = parent.makeelement(tag, attrib)
        parent.append(element)
        return element
    ET.SubElement = SubElement
except AttributeError:
    pass  # nothing else for python2, ElementTree is pure python
# =======================================================================


def etree_read(filename):
    # find encoding
    detector = UniversalDetector()
    detector.reset()
    ddoc={}
    for line in file(filename, 'rb'):
        detector.feed(line)
        if detector.done: break
    detector.close()
    fenc= detector.result['encoding']
    # read file xml and return etree
    etree=ET.parse(filename, OrderedXMLTreeBuilder(encoding=fenc))
    etree.encoding=fenc
    return etree

def etree_to_string(etree):
    return ET.tostring(etree.getroot(), encoding=etree.encoding)

def etree_to_file(etree, filename):
    etree.write(filename, encoding=etree.encoding, xml_declaration=True, method='xml')



