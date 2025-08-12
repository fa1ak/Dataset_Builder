# 🚀 Dataset Processing Tool with Chainlit & Unstructured

A powerful, user-friendly tool for processing and extracting structured data from various document types using the **unstructured** library with a beautiful **Chainlit** interface.

## ✨ Features

- **📁 Multi-format Support**: PDF, DOCX, TXT, MD, HTML, Images (with OCR), CSV, XLSX, PPTX
- **🔄 Real-time Processing**: Live progress updates and status tracking
- **📊 Structured Output**: Preserves document structure (titles, lists, tables, etc.)
- **📤 Multiple Export Formats**: JSON, CSV, and summary reports
- **🎨 Beautiful UI**: Modern, responsive interface with action buttons
- **🔒 Local Processing**: All processing happens locally for privacy
- **📱 Mobile Friendly**: Works on desktop and mobile devices

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- pyenv (recommended for virtual environment management)

### Setup Steps

1. **Clone and Navigate**
   ```bash
   cd ~/Desktop/Projects/DatasetBuilder
   ```

2. **Activate Virtual Environment**
   ```bash
   pyenv activate unstructured
   ```

3. **Install Dependencies**
   ```bash
   # Core unstructured library (already installed)
   # Chainlit (already installed)
   pip install pandas
   ```

4. **Verify Installation**
   ```bash
   python -c "import chainlit, unstructured; print('✅ All dependencies installed!')"
   ```

## 🚀 Usage

### Starting the App

1. **Run the Application**
   ```bash
   chainlit run dataset_processor.py
   ```

2. **Open in Browser**
   - The app will automatically open at `http://localhost:8000`
   - Or manually navigate to the URL shown in the terminal

### Using the App

1. **Upload Files**
   - Click the file upload button or drag & drop files
   - Supported formats are automatically detected

2. **Process Documents**
   - Click "🔄 Process Files" to start extraction
   - Watch real-time progress updates
   - View processing statistics

3. **Export Results**
   - Click "📤 Export Results" to download data
   - Choose from JSON, CSV, or summary formats

4. **Interactive Commands**
   - Type `help` for instructions
   - Type `process` to start processing
   - Type `export` to download results
   - Type `clear` to reset session

## 📁 Supported File Types

| Category | Formats | Features |
|----------|---------|----------|
| **Documents** | PDF, DOCX, TXT, MD, HTML | Text extraction, structure preservation |
| **Images** | JPG, PNG, TIFF, BMP | OCR text extraction |
| **Spreadsheets** | CSV, XLSX | Tabular data extraction |
| **Presentations** | PPTX | Slide content extraction |

## 🔧 Configuration

### File Upload Limits
- **Max File Size**: 100 MB
- **Max Files**: 10 per session
- **Accepted Types**: All supported formats

### Processing Options
- **OCR**: Automatically enabled for images
- **Structure Detection**: Automatic title, list, and table recognition
- **Metadata Extraction**: File properties and processing information

## 📊 Output Formats

### 1. JSON Export
Complete structured data with metadata:
```json
{
  "filename": "document.pdf",
  "word_count": 1250,
  "elements": [
    {
      "type": "title",
      "text": "Document Title",
      "metadata": {...}
    }
  ]
}
```

### 2. CSV Export
Flattened data for analysis:
```csv
filename,element_type,text,word_count,file_type
document.pdf,title,Document Title,2,.pdf
document.pdf,narrative,Main content...,45,.pdf
```

### 3. Summary Report
Processing statistics and file information:
```csv
filename,file_type,file_size_mb,word_count,element_count,status
document.pdf,.pdf,2.5,1250,15,Success
```

## 🎯 Use Cases

- **📚 Research**: Extract text from academic papers and reports
- **📊 Data Analysis**: Process spreadsheets and structured documents
- **📝 Content Creation**: Extract content from various sources
- **🔍 Information Retrieval**: Search through document collections
- **📋 Compliance**: Process legal and regulatory documents
- **🎨 Creative Projects**: Extract text from images and designs

## 🚀 Advanced Features

### Batch Processing
- Upload multiple files at once
- Process all files in sequence
- Consolidated results and statistics

### Structure Preservation
- Maintains document hierarchy
- Identifies titles, subtitles, and sections
- Preserves list formatting and table structure

### OCR Capabilities
- Automatic text extraction from images
- Support for multiple image formats
- Quality-based processing

## 🔍 Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size (max 100 MB)
   - Verify file format is supported
   - Ensure sufficient disk space

2. **Processing Errors**
   - Check file integrity
   - Verify unstructured library installation
   - Check system dependencies (tesseract, poppler)

3. **Performance Issues**
   - Large files may take longer
   - Complex layouts require more processing time
   - Consider breaking large documents into smaller parts

### System Requirements

- **Memory**: 4GB+ RAM recommended
- **Storage**: Sufficient space for temporary files
- **Dependencies**: tesseract, poppler (for PDF/image processing)

## 🛠️ Development

### Project Structure
```
DatasetBuilder/
├── dataset_processor.py    # Main application
├── .chainlit/
│   └── config.toml        # Chainlit configuration
├── exports/               # Generated export files
└── README.md             # This file
```

### Customization
- Modify `SUPPORTED_FORMATS` for different file types
- Adjust processing logic in `process_single_file()`
- Customize export formats in `export_processed_data()`
- Update UI styling in `.chainlit/config.toml`

## 📚 Resources

- **Unstructured Documentation**: [https://unstructured.io/](https://unstructured.io/)
- **Chainlit Documentation**: [https://docs.chainlit.io/](https://docs.chainlit.io/)
- **Python Documentation**: [https://docs.python.org/](https://docs.python.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section above
- Review the unstructured and Chainlit documentation
- Open an issue in the repository

---

**Happy Document Processing! 🎉**
