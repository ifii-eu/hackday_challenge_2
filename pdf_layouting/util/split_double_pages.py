import fitz  # PyMuPDF

def split_a3_to_a4(input_pdf_path, output_pdf_path):
    # Open the source PDF
    doc = fitz.open(input_pdf_path)
    output = fitz.open()

    for page in doc:
        rect = page.rect
        width = rect.width
        height = rect.height

        # Ensure landscape
        if width < height:
            print(f"Warning: Page {page.number + 1} is not landscape. Skipping.")
            continue

        # Left half (A4 portrait)
        left_rect = fitz.Rect(0, 0, width / 2, height)
        left_page = output.new_page(width=width / 2, height=height)
        left_page.show_pdf_page(left_page.rect, doc, page.number, clip=left_rect)

        # Right half (A4 portrait)
        right_rect = fitz.Rect(width / 2, 0, width, height)
        right_page = output.new_page(width=width / 2, height=height)
        right_page.show_pdf_page(right_page.rect, doc, page.number, clip=right_rect)

    # Save the output PDF
    output.save(output_pdf_path)
    output.close()
    doc.close()

# Example usage
split_a3_to_a4("document.pdf", "split.pdf")
