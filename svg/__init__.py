"""
"""
try:
    import wxversion
    #~ wxversion.ensureMinimal('2.9')
    wxversion.select('3.8-msw-unicode-custom')
except:
    pass

def gd():
    import document
    return document.SVGDocument(document.document)