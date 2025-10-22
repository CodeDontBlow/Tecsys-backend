import PyPDF2
import io



def pdf_to_text(pdf_file_bytes):

    try:
        pdf_content = io.BytesIO(pdf_file_bytes)
        reader = PyPDF2.PdfReader(pdf_content)
        total_pages = len(reader.pages)
        
        full_text = f"Archive processed in memory\n"
        full_text += f"Number of pages: {total_pages}\n\n"
        
            
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            if text.strip():
                full_text += f"--- Page {page_num+1} ---\n{text}\n"
            else:
                full_text += f"--- Page {page_num+1} (Page content - OCR didnt catch the text) ---\n"
        
            return full_text
    except Exception as e:
        return f"Error to process PDF: {str(e)}"


