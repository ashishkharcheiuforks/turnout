# simple wrappers around pdfrw
import pdfrw

ANNOT_KEY = "/Annots"
ANNOT_FIELD_KEY = "/T"
ANNOT_VAL_KEY = "/V"
ANNOT_RECT_KEY = "/Rect"
SUBTYPE_KEY = "/Subtype"
WIDGET_SUBTYPE_kEY = "/Widget"


def fill_form(input_file, output_file, data):
    """input_file can be file object or path name
    output_file can be file object or path name
    data is dictionary with keys corresponding to the form fields"""

    the_pdf = pdfrw.PdfReader(input_file)
    annotations = the_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_kEY:
            key = annotation[ANNOT_FIELD_KEY][1:-1]
            if key in data.keys():
                val = data[key]
                if val == None:
                    # skip nulls
                    continue
                if val == True:
                    # treat booleans as checkboxes
                    annotation.update(pdfrw.PdfDict(V=pdfrw.PdfName("On")))
                else:
                    annotation.update(pdfrw.PdfDict(V="{}".format(val)))
                # mark the fields as un-editable
                annotation.update(pdfrw.PdfDict(Ff=1))

    # set NeedAppearances to ensure the fields are visible in some clientds
    the_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject("true")))

    pdfrw.PdfWriter().write(output_file, the_pdf)
