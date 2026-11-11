import os
import markdown
from weasyprint import HTML


def create_cv_pdf(markdown_content: str, output_filename: str = "CV_Optimizado.pdf") -> str:
    """Convierte el contenido Markdown del CV optimizado en un PDF formal."""
    try:
        # Convertir Markdown a HTML
        html_body = markdown.markdown(markdown_content)
        
        # Estilos CSS profesionales simulando el formato corporativo y limpio
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    color: #333333;
                    line-height: 1.4;
                    font-size: 11pt;
                    margin: 20mm;
                }}
                h1 {{
                    font-size: 18pt;
                    color: #111827;
                    border-bottom: 2px solid #2563eb;
                    padding-bottom: 4px;
                    margin-bottom: 8px;
                }}
                h2 {{
                    font-size: 13pt;
                    color: #1f2937;
                    border-bottom: 1px solid #e5e7eb;
                    padding-bottom: 2px;
                    margin-top: 16px;
                    margin-bottom: 6px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                h3 {{
                    font-size: 11pt;
                    color: #374151;
                    margin-top: 10px;
                    margin-bottom: 4px;
                }}
                p, li {{
                    font-size: 10pt;
                    margin-bottom: 4px;
                }}
                ul {{
                    margin-top: 2px;
                    padding-left: 15px;
                }}
                a {{
                    color: #2563eb;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """
        
        output_path = os.path.join(os.getcwd(), output_filename)
        HTML(string=html_content).write_pdf(output_path)
        return output_path
    except Exception as e:
        print(f"Error generando el PDF: {e}")
        return None