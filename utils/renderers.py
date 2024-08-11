from io import BytesIO
from django.template.loader import get_template
from copilot import settings
from xhtml2pdf import pisa
import pdfkit


def html_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if pdf.err:
        return None
    return result.getvalue()
def html_to_pdf2(html_content):
    # Use the PDFKIT_CONFIG from settings if needed
    pdf = pdfkit.from_string(html_content, False, configuration=pdfkit.configuration(wkhtmltopdf=settings.PDFKIT_CONFIG['wkhtmltopdf']))
    return pdf