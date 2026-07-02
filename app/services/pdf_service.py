from io import BytesIO

from flask import send_file

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet


class PDFService:

    @staticmethod
    def generate_report(title, filename, content):

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter
        )

        styles = getSampleStyleSheet()

        story = []

        story.append(
            Paragraph(
                f"<b>{title}</b>",
                styles["Title"]
            )
        )

        story.append(
            Paragraph("<br/><br/>", styles["Normal"])
        )

        paragraphs = content.split("\n")

        for line in paragraphs:

            if line.strip():

                story.append(
                    Paragraph(
                        line.replace("<", "&lt;").replace(">", "&gt;"),
                        styles["BodyText"]
                    )
                )

        doc.build(story)

        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )