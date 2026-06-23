import io
import logging
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

from core.types import Project

logger = logging.getLogger(__name__)


class PDFExportService:
    """Service for exporting research reports to PDF format."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Define custom paragraph styles for the report."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2563EB'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1F2937'),
            spaceBefore=20,
            spaceAfter=12,
            borderWidth=0,
            borderPadding=0,
            borderColor=None
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#4B5563'),
            spaceBefore=15,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='Citation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6B7280'),
            spaceBefore=5,
            spaceAfter=10,
            leftIndent=20,
            fontName='Helvetica-Oblique'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#9CA3AF'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletItem',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            leftIndent=20,
            spaceAfter=6,
            leading=14
        ))

    def generate_pdf(self, project: Project) -> bytes:
        """Generate a PDF document from a project."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        story.extend(self._build_title_page(project))
        story.append(PageBreak())
        story.extend(self._build_content_pages(project))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _build_title_page(self, project: Project) -> list:
        """Build the title page elements."""
        elements = []
        
        elements.append(Spacer(1, 2 * inch))
        
        title_style = self.styles['ReportTitle']
        elements.append(Paragraph(project.title, title_style))
        
        elements.append(Spacer(1, 0.5 * inch))
        
        meta_style = self.styles['Metadata']
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            meta_style
        ))
        elements.append(Paragraph(
            f"Research Query: {project.query[:100]}{'...' if len(project.query) > 100 else ''}",
            meta_style
        ))
        
        elements.append(Spacer(1, 1 * inch))
        
        elements.append(Paragraph(
            "Powered by Multi-Agent Market Research System",
            meta_style
        ))
        
        return elements
    
    def _build_content_pages(self, project: Project) -> list:
        """Build the main content pages with sections."""
        elements = []
        
        elements.append(Paragraph("Table of Contents", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.2 * inch))
        
        for i, section in enumerate(project.sections, 1):
            elements.append(Paragraph(
                f"{i}. {section.title}",
                self.styles['BulletItem']
            ))
        
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(PageBreak())
        
        for section in project.sections:
            elements.append(Paragraph(section.title, self.styles['SectionHeading']))
            
            content = section.content or "Content not available."
            paragraphs = content.split('\n\n')
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                if para.startswith('**Sources:**'):
                    citations = para.replace('**Sources:**\n', '').split('\n')
                    for citation in citations:
                        if citation.strip():
                            elements.append(Paragraph(
                                citation.strip(),
                                self.styles['Citation']
                            ))
                elif para.startswith('•') or para.startswith('-'):
                    items = para.split('\n')
                    for item in items:
                        if item.strip():
                            clean_item = item.strip().lstrip('•-').strip()
                            elements.append(Paragraph(f"• {clean_item}", self.styles['BulletItem']))
                else:
                    clean_para = para.replace('**', '').replace('*', '')
                    elements.append(Paragraph(clean_para, self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.3 * inch))
        
        return elements


def get_pdf_service() -> PDFExportService:
    """Factory function to get PDF service instance."""
    return PDFExportService()
