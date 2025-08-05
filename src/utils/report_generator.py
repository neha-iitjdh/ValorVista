"""
PDF Report Generator for ValorVista.
Creates professional valuation reports.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .visualizations import create_feature_importance_chart, create_price_distribution


class ReportGenerator:
    """Generate professional PDF valuation reports."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1976D2'),
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#333333'),
            borderWidth=0,
            borderPadding=0
        ))

        self.styles.add(ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=colors.HexColor('#555555')
        ))

        self.styles.add(ParagraphStyle(
            'PriceHighlight',
            parent=self.styles['Normal'],
            fontSize=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1976D2'),
            spaceBefore=10,
            spaceAfter=10
        ))

        self.styles.add(ParagraphStyle(
            'FooterText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER
        ))

    def generate_report(
        self,
        property_data: Dict[str, Any],
        prediction: Dict[str, Any],
        explanation: Dict[str, Any],
        feature_importance: List[Dict[str, Any]],
        output_path: Path
    ) -> Path:
        """
        Generate complete valuation report.

        Args:
            property_data: Input property features.
            prediction: Prediction results with intervals.
            explanation: Prediction explanation.
            feature_importance: Feature importance data.
            output_path: Path to save the PDF.

        Returns:
            Path to generated PDF.
        """
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        # Title
        story.append(Paragraph("ValorVista", self.styles['CustomTitle']))
        story.append(Paragraph(
            "AI-Powered Property Valuation Report",
            ParagraphStyle('Subtitle', parent=self.styles['Normal'],
                          fontSize=12, alignment=TA_CENTER,
                          textColor=colors.HexColor('#666666'))
        ))
        story.append(Spacer(1, 20))

        # Report metadata
        story.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor('#E0E0E0')
        ))
        story.append(Spacer(1, 10))

        meta_data = [
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['Report ID:', output_path.stem.split('_')[-1]],
        ]
        meta_table = Table(meta_data, colWidths=[1.5*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#888888')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # Valuation Summary Section
        story.append(Paragraph("Valuation Summary", self.styles['SectionHeader']))
        story.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor('#1976D2')
        ))
        story.append(Spacer(1, 15))

        # Main prediction
        pred_value = prediction['predictions'][0]
        story.append(Paragraph(
            f"<b>Estimated Market Value</b>",
            ParagraphStyle('Label', parent=self.styles['Normal'],
                          fontSize=10, alignment=TA_CENTER,
                          textColor=colors.HexColor('#666666'))
        ))
        story.append(Paragraph(
            f"${pred_value:,.0f}",
            self.styles['PriceHighlight']
        ))

        # Confidence interval
        if 'prediction_intervals' in prediction and prediction['prediction_intervals']:
            interval = prediction['prediction_intervals'][0]
            story.append(Paragraph(
                f"95% Confidence Range: {interval['formatted']['lower']} - {interval['formatted']['upper']}",
                ParagraphStyle('Interval', parent=self.styles['Normal'],
                              fontSize=10, alignment=TA_CENTER,
                              textColor=colors.HexColor('#888888'))
            ))
        story.append(Spacer(1, 20))

        # Property Details Section
        story.append(Paragraph("Property Details", self.styles['SectionHeader']))
        story.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor('#1976D2')
        ))
        story.append(Spacer(1, 10))

        property_details = self._format_property_details(property_data)
        details_table = Table(property_details, colWidths=[2.5*inch, 2*inch, 2.5*inch])
        details_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))

        # Key Valuation Factors Section
        story.append(Paragraph("Key Valuation Factors", self.styles['SectionHeader']))
        story.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor('#1976D2')
        ))
        story.append(Spacer(1, 10))

        if explanation.get('key_factors'):
            factors_data = [['Feature', 'Value', 'Impact']]
            for factor in explanation['key_factors'][:8]:
                impact_pct = f"{factor['importance']*100:.1f}%"
                factors_data.append([
                    factor['feature'],
                    str(factor['value']),
                    impact_pct
                ])

            factors_table = Table(factors_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            factors_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ]))
            story.append(factors_table)

        story.append(Spacer(1, 20))

        # Disclaimer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor('#E0E0E0')
        ))
        story.append(Spacer(1, 10))

        disclaimer = """
        <b>Disclaimer:</b> This valuation estimate is generated by an AI model based on historical
        data and property characteristics. It is intended for informational purposes only and should
        not be considered as a formal appraisal. Actual market values may vary based on current
        market conditions, property condition, and other factors not captured in this analysis.
        We recommend consulting with a licensed real estate professional for accurate property valuations.
        """
        story.append(Paragraph(disclaimer, ParagraphStyle(
            'Disclaimer', parent=self.styles['Normal'],
            fontSize=8, textColor=colors.HexColor('#888888'),
            alignment=TA_LEFT
        )))

        story.append(Spacer(1, 20))
        story.append(Paragraph(
            f"Generated by ValorVista | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['FooterText']
        ))

        # Build PDF
        doc.build(story)
        return output_path

    def _format_property_details(self, data: Dict[str, Any]) -> List[List[str]]:
        """Format property data into table rows."""
        details = [
            ['Basic Information', '', 'Features'],
            [f"Living Area: {data.get('GrLivArea', 'N/A'):,} sq ft",
             f"Year Built: {data.get('YearBuilt', 'N/A')}",
             f"Bedrooms: {data.get('BedroomAbvGr', 'N/A')}"],
            [f"Lot Area: {data.get('LotArea', 'N/A'):,} sq ft",
             f"Quality: {data.get('OverallQual', 'N/A')}/10",
             f"Bathrooms: {data.get('FullBath', 0) + 0.5*data.get('HalfBath', 0)}"],
            [f"Basement: {data.get('TotalBsmtSF', 0):,} sq ft",
             f"Condition: {data.get('OverallCond', 'N/A')}/10",
             f"Garage Cars: {data.get('GarageCars', 'N/A')}"],
            [f"Floors: {1 if data.get('2ndFlrSF', 0) == 0 else 2}",
             f"Neighborhood: {data.get('Neighborhood', 'N/A')}",
             f"Fireplaces: {data.get('Fireplaces', 0)}"],
        ]
        return details
