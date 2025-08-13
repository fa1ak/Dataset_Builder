# Dataset Processing Tool with Chainlit & Unstructured

A powerful, user-friendly tool for processing and extracting structured data from various document types using the **unstructured** library with a beautiful **Chainlit** interface.

## Features

- **Multi-format Support**: PDF, DOCX, TXT, MD, HTML, Images (with OCR), CSV, XLSX, PPTX
- **Real-time Processing**: Live progress updates and status tracking
- **Structured Output**: Preserves document structure (titles, lists, tables, etc.)
- **Multiple Export Formats**: JSON, CSV, and text exports
- **Beautiful UI**: Modern, responsive chat interface
- **Local Processing**: All processing happens locally for privacy
- **Mobile Friendly**: Works on desktop and mobile devices
- **Robust Processing**: Handles processing errors gracefully without crashing
- **Docker Ready**: Easy setup with Docker and Docker Compose

## Quick Start (Docker - Recommended)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

### One-Command Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/fa1ak/Dataset_Builder.git
   cd Dataset_Builder
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the tool**
   - Open your browser and go to: `http://localhost:8000`
   - The tool is ready to use!

### Manual Docker Setup

If you prefer to set up manually:

1. **Clone and navigate**
   ```bash
   git clone https://github.com/fa1ak/Dataset_Builder.git
   cd Dataset_Builder
   ```

2. **Create directories**
   ```bash
   mkdir -p data exports
   ```

3. **Build and run**
   ```bash
   docker-compose up --build
   ```

## Local Installation (Alternative)

### Prerequisites

- Python 3.10+
- pyenv (recommended for virtual environment management)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/fa1ak/Dataset_Builder.git
   cd Dataset_Builder
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import chainlit, unstructured; print('✅ All dependencies installed!')"
   ```

## Usage

### Starting the App

#### With Docker (Recommended)
```bash
docker-compose up --build
```

#### With Local Python
```bash
python -m chainlit run dataset_processor.py
```

### Using the App

1. **Process Documents by Path**
   - Type `process /path/to/your/file.pdf` to start extraction
   - Use absolute paths for best results
   - Example: `process /Users/username/Documents/resume.pdf`
   - **With Docker**: Place files in the `data` folder and use `process /app/data/yourfile.pdf`

2. **View Results**
   - Type `show` to preview extracted content
   - See real-time processing progress
   - View processing statistics and summaries

3. **Export Results**
   - Type `export` to download data to local files
   - Files are saved in the `exports/` directory
   - Available formats: JSON, CSV, and text

4. **Interactive Commands**
   - Type `help` for detailed instructions
   - Type `process /path/to/file` to start processing
   - Type `show` to preview content
   - Type `export` to download results
   - Type `clear` to reset session
   - Type `demo` to see sample workflow

## Supported File Types

| Category | Formats | Features |
|----------|---------|----------|
| **Documents** | PDF, DOCX, TXT, MD, HTML | Text extraction, structure preservation |
| **Images** | JPG, PNG, TIFF, BMP | OCR text extraction |
| **Spreadsheets** | CSV, XLSX | Tabular data extraction |
| **Presentations** | PPTX | Slide content extraction |

## Configuration

### Processing Options
- **OCR**: Automatically enabled for images
- **Structure Detection**: Automatic title, list, and table recognition
- **Metadata Extraction**: File properties and processing information
- **Error Handling**: Robust processing that continues despite individual element failures

### File Processing
- **Path-based**: Provide full file paths to process documents
- **Multiple files**: Process several files at once
- **Local files only**: All files must be accessible from your system

### Docker Volumes
- **Data directory**: Mount your documents in the `data` folder
- **Exports directory**: Results are automatically saved to the `exports` folder
- **Port mapping**: Access the tool at `http://localhost:8000`

## Output Formats

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
      "metadata": {...},
      "coordinates": {...}
    }
  ]
}
```

### 2. CSV Export
Summary statistics for each file:
```csv
filename,element_count,word_count,file_size,file_type
document.pdf,15,1250,2560000,.pdf
```

### 3. Text Export
All extracted text content organized by file:
```text
==================================================
FILE: document.pdf
ELEMENTS: 15
WORDS: 1250
==================================================

[TITLE]
Document Title

[NARRATIVE]
Main content text...
```

## Use Cases

- **Research**: Extract text from academic papers and reports
- **Data Analysis**: Process spreadsheets and structured documents
- **Content Creation**: Extract content from various sources
- **Information Retrieval**: Search through document collections
- **Compliance**: Process legal and regulatory documents
- **Creative Projects**: Extract text from images and designs

## Advanced Features

### Batch Processing
- Process multiple files at once
- Example: `process /path/to/file1.pdf /path/to/file2.docx /path/to/image.jpg`
- Consolidated results and statistics

### Structure Preservation
- Maintains document hierarchy
- Identifies titles, subtitles, and sections
- Preserves list formatting and table structure
- Handles complex layouts gracefully

### OCR Capabilities
- Automatic text extraction from images
- Support for multiple image formats
- Quality-based processing

### Robust Error Handling
- Individual element processing failures don't stop the entire process
- Detailed error reporting and progress tracking
- Continues processing despite problematic elements

## Troubleshooting

### Common Issues

1. **File Not Found**
   - Use absolute paths for best results
   - Check file permissions and accessibility
   - Verify file exists at the specified path
   - **With Docker**: Place files in the `data` folder and use `/app/data/filename.pdf`

2. **Processing Errors**
   - Check file integrity
   - Verify Docker container is running properly
   - Check system dependencies (tesseract, poppler) are installed in container

3. **Performance Issues**
   - Large files may take longer
   - Complex layouts require more processing time
   - Consider breaking large documents into smaller parts

### Docker Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs
   
   # Rebuild container
   docker-compose down
   docker-compose up --build
   ```

2. **Port already in use**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

3. **Permission issues**
   ```bash
   # Ensure directories exist and have proper permissions
   mkdir -p data exports
   chmod 755 data exports
   ```

### System Requirements

- **Memory**: 4GB+ RAM recommended
- **Storage**: Sufficient space for temporary files
- **Dependencies**: All included in Docker container

## 🛠️ Development

### Project Structure
```
DatasetBuilder/
├── dataset_processor.py    # Main application
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
├── .chainlit/
│   └── config.toml       # Chainlit configuration
├── data/                 # User documents (mounted volume)
├── exports/              # Generated export files (mounted volume)
└── README.md             # This file
```

### Customization
- Modify element processing logic in `process_single_file_from_path()`
- Customize export formats in `export_processed_data()`
- Update UI styling in `.chainlit/config.toml`
- Adjust progress tracking frequency
- Modify Docker configuration in `Dockerfile` and `docker-compose.yml`

### Building Custom Docker Image
```bash
# Build custom image
docker build -t my-dataset-processor .

# Run custom image
docker run -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/exports:/app/exports my-dataset-processor
```

## Resources

- **Unstructured Documentation**: [https://unstructured.io/](https://unstructured.io/)
- **Chainlit Documentation**: [https://docs.chainlit.io/](https://docs.chainlit.io/)
- **Docker Documentation**: [https://docs.docker.com/](https://docs.docker.com/)
- **Python Documentation**: [https://docs.python.org/](https://docs.python.org/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (including Docker build)
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the Docker logs: `docker-compose logs`
- Review the unstructured and Chainlit documentation
- Open an issue in the repository
