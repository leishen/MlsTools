import xml.dom.minidom as xmlparse

__all__ = ['getnodetext']

def getnodetext(node):
    rc = []
    for n in node.childNodes:
        if n.nodeType == n.TEXT_NODE:
            rc.append(n.data)
    return ''.join(rc)
