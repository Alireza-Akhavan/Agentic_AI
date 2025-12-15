from IPython.display import display, HTML
import re

def show_output(title, content, background="#f0f0f0", text_color="#000000"):
    # Convert Markdown into HTML
    def markdown_to_html(text):
        # Headers and size
        text = re.sub(r'^### (.+)$', r'<h5 style="font-weight: bold; font-size: 1.1em; margin: 10px 0 5px 0;">\1</h5>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h4 style="font-weight: bold; font-size: 1.3em; margin: 12px 0 6px 0;">\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h3 style="font-weight: bold; font-size: 1.5em; margin: 15px 0 8px 0;">\1</h3>', text, flags=re.MULTILINE)
        
        # Bold: **text** -> <strong>text</strong>
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="font-weight: bold;">\1</strong>', text)
        
        # Italic: *text* -> <em>text</em>
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)\*(?!\*)', r'<em>\1</em>', text)
        
        return text
    
    content_html = markdown_to_html(content)
    
    html = f"""
    <div style="
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: {background};
        color: {text_color};
        direction: rtl;
        text-align: right;
    ">
        <h3 style="
            margin-top: 0; 
            font-family: Vazirmatn, Vazir, Tahoma, Arial;
            font-weight: bold;
        ">{title}</h3>
        <div style="
            white-space: pre-wrap;
            font-family: Vazirmatn, Vazir, Tahoma, monospace;
            font-size: 14px;
            line-height: 1.8;
        ">{content_html}</div>
    </div>
    """
    display(HTML(html))