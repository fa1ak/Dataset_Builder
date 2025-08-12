import chainlit as cl
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import json
import pandas as pd

# Import unstructured components
from unstructured.partition.auto import partition
from unstructured.staging.base import convert_to_dict
from unstructured.documents.elements import Text, Title, NarrativeText, ListItem, Table

# Configuration
SUPPORTED_FORMATS = [
    '.pdf', '.docx', '.txt', '.md', '.html', '.jpg', '.jpeg', '.png', 
    '.tiff', '.bmp', '.csv', '.xlsx', '.pptx'
]

@cl.on_chat_start
async def start():
    """Initialize the dataset processing app"""
    
    # Create welcome message with app description
    welcome_msg = """🚀 **Dataset Processing Tool with Unstructured**

This tool helps you process and extract structured data from various document types using the power of unstructured library.

**Supported Formats:**
• **Documents**: PDF, DOCX, TXT, MD, HTML
• **Images**: JPG, PNG, TIFF, BMP (with OCR)
• **Spreadsheets**: CSV, XLSX
• **Presentations**: PPTX

**Features:**
• Drag & drop file uploads
• Text extraction and structure analysis
• Export results in multiple formats
• Batch processing capabilities

**How to use:**
1. **Upload files** using the file upload button below
2. **Type 'process'** to start processing uploaded files
3. **Type 'export'** to download your processed results
4. **Type 'help'** for detailed instructions
5. **Type 'demo'** to see a sample processing workflow

**File Upload:**
Use the file upload button below to add your documents. You can upload multiple files at once!

Ready to process some documents? 🎯"""
    
    await cl.Message(content=welcome_msg).send()
    
    # Create file upload button
    await cl.Message(
        content="📁 **Upload Your Files**",
        elements=[
            cl.File(
                name="upload_files",
                path="",
                display="inline",
                description="Click to upload files for processing"
            )
        ]
    ).send()

async def process_uploaded_files():
    """Process all uploaded files in the session"""
    
    files = cl.get_session().files
    if not files:
        await cl.Message(content="❌ No files uploaded yet. Please upload some files first using the file upload button.").send()
        return
    
    await cl.Message(content=f"🔄 Starting to process {len(files)} files...").send()
    
    results = []
    for i, file in enumerate(files):
        await cl.Message(content=f"📄 Processing file {i+1}/{len(files)}: {file.name}").send()
        
        try:
            result = await process_single_file(file)
            results.append(result)
            
            # Show progress
            progress_msg = f"✅ Completed: {file.name}"
            if result.get('word_count'):
                progress_msg += f" ({result['word_count']} words)"
            await cl.Message(content=progress_msg).send()
            
        except Exception as e:
            error_msg = f"❌ Error processing {file.name}: {str(e)}"
            await cl.Message(content=error_msg).send()
    
    # Store results in session
    cl.get_session().user_session["processed_results"] = results
    
    # Summary
    if results:
        total_words = sum(r.get('word_count', 0) for r in results)
        summary_msg = f"""🎉 **Processing Complete!**

**Summary:**
• Files processed: {len(results)}
• Total words extracted: {total_words:,}
• Successful extractions: {len([r for r in results if r.get('success')])}

Use 'export' to download your processed data!"""
        
        await cl.Message(content=summary_msg).send()
    else:
        await cl.Message(content="❌ No files were successfully processed.").send()

async def process_single_file(file: cl.File) -> Dict[str, Any]:
    """Process a single file and return structured results"""
    
    # Create temporary file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp_file:
        tmp_file.write(file.content)
        tmp_path = tmp_file.name
    
    try:
        # Process with unstructured
        elements = partition(tmp_path)
        
        # Convert to structured format
        structured_data = []
        word_count = 0
        
        for element in elements:
            element_dict = convert_to_dict(element)
            
            # Extract text content
            if hasattr(element, 'text'):
                text = element.text
                word_count += len(text.split())
            else:
                text = str(element)
                word_count += len(text.split())
            
            # Determine element type
            element_type = "text"
            if isinstance(element, Title):
                element_type = "title"
            elif isinstance(element, NarrativeText):
                element_type = "narrative"
            elif isinstance(element, ListItem):
                element_type = "list_item"
            elif isinstance(element, Table):
                element_type = "table"
            
            structured_data.append({
                'type': element_type,
                'text': text,
                'metadata': element_dict.get('metadata', {}),
                'coordinates': element_dict.get('coordinates', None)
            })
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {
            'success': True,
            'filename': file.name,
            'file_size': len(file.content),
            'word_count': word_count,
            'elements': structured_data,
            'element_count': len(structured_data),
            'file_type': Path(file.name).suffix.lower()
        }
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise e

async def process_files_from_paths(file_paths: List[str]):
    """Process files from file paths (alternative method)"""
    
    if not file_paths:
        await cl.Message(content="❌ No file paths provided. Please provide valid file paths.").send()
        return
    
    await cl.Message(content=f"🔄 Starting to process {len(file_paths)} files...").send()
    
    results = []
    for i, file_path in enumerate(file_paths):
        file_path = file_path.strip()
        if not os.path.exists(file_path):
            await cl.Message(content=f"❌ File not found: {file_path}").send()
            continue
            
        await cl.Message(content=f"📄 Processing file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}").send()
        
        try:
            result = await process_single_file_from_path(file_path)
            results.append(result)
            
            # Show progress
            progress_msg = f"✅ Completed: {os.path.basename(file_path)}"
            if result.get('word_count'):
                progress_msg += f" ({result['word_count']} words)"
            await cl.Message(content=progress_msg).send()
            
        except Exception as e:
            error_msg = f"❌ Error processing {os.path.basename(file_path)}: {str(e)}"
            await cl.Message(content=error_msg).send()
    
    # Store results in session
    cl.get_session().user_session["processed_results"] = results
    
    # Summary
    if results:
        total_words = sum(r.get('word_count', 0) for r in results)
        summary_msg = f"""🎉 **Processing Complete!**

**Summary:**
• Files processed: {len(results)}
• Total words extracted: {total_words:,}
• Successful extractions: {len([r for r in results if r.get('success')])}

Use 'export' to download your processed data!"""
        
        await cl.Message(content=summary_msg).send()
    else:
        await cl.Message(content="❌ No files were successfully processed.").send()

async def process_single_file_from_path(file_path: str) -> Dict[str, Any]:
    """Process a single file from path and return structured results"""
    
    try:
        # Process with unstructured
        elements = partition(file_path)
        
        # Convert to structured format
        structured_data = []
        word_count = 0
        
        for element in elements:
            element_dict = convert_to_dict(element)
            
            # Extract text content
            if hasattr(element, 'text'):
                text = element.text
                word_count += len(text.split())
            else:
                text = str(element)
                word_count += len(text.split())
            
            # Determine element type
            element_type = "text"
            if isinstance(element, Title):
                element_type = "title"
            elif isinstance(element, NarrativeText):
                element_type = "narrative"
            elif isinstance(element, ListItem):
                element_type = "list_item"
            elif isinstance(element, Table):
                element_type = "table"
            
            structured_data.append({
                'type': element_type,
                'text': text,
                'metadata': element_dict.get('metadata', {}),
                'coordinates': element_dict.get('coordinates', None)
            })
        
        return {
            'success': True,
            'filename': os.path.basename(file_path),
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'word_count': word_count,
            'elements': structured_data,
            'element_count': len(structured_data),
            'file_type': Path(file_path).suffix.lower()
        }
        
    except Exception as e:
        raise e

async def export_processed_data():
    """Export processed data in various formats"""
    
    results = cl.get_session().user_session.get("processed_results", [])
    if not results:
        await cl.Message(content="❌ No processed data to export. Please process some files first.").send()
        return
    
    await cl.Message(content="📤 Preparing export...").send()
    
    # Create export directory
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    # Export as JSON
    json_path = export_dir / "processed_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    # Export as CSV (flattened)
    csv_data = []
    for result in results:
        for element in result.get('elements', []):
            csv_data.append({
                'filename': result['filename'],
                'element_type': element['type'],
                'text': element['text'][:500],  # Truncate long text
                'word_count': len(element['text'].split()),
                'file_type': result['file_type']
            })
    
    df = pd.DataFrame(csv_data)
    csv_path = export_dir / "processed_data.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    # Create summary report
    summary_data = []
    for result in results:
        summary_data.append({
            'filename': result['filename'],
            'file_type': result['file_type'],
            'file_size_mb': round(result['file_size'] / (1024*1024), 2),
            'word_count': result['word_count'],
            'element_count': result['element_count'],
            'status': 'Success' if result.get('success') else 'Failed'
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_path = export_dir / "processing_summary.csv"
    summary_df.to_csv(summary_path, index=False, encoding='utf-8')
    
    # Send export files
    files_to_send = [
        cl.File(name="processed_data.json", path=str(json_path), display="inline"),
        cl.File(name="processed_data.csv", path=str(csv_path), display="inline"),
        cl.File(name="processing_summary.csv", path=str(summary_path), display="inline")
    ]
    
    await cl.Message(
        content="📤 **Export Complete!**\n\nYour processed data has been exported in multiple formats:",
        elements=files_to_send
    ).send()

async def clear_session_data():
    """Clear all processed data from the session"""
    
    cl.get_session().user_session.clear()
    await cl.Message(content="🗑️ Session data cleared. You can start fresh!").send()

async def show_help_info():
    """Show detailed help information"""
    
    help_msg = """❓ **Help & Usage Guide**

**Getting Started:**
1. **Upload Files**: Use the file upload button to add documents
2. **Process Files**: Type 'process' to start extraction
3. **Export Results**: Type 'export' to download your processed data
4. **Alternative**: Type 'process <file1> <file2>' to process files from paths

**Supported File Types:**
• **PDFs**: Full text extraction with layout preservation
• **Images**: OCR text extraction (requires tesseract)
• **Office Documents**: DOCX, XLSX, PPTX parsing
• **Plain Text**: TXT, MD, HTML processing

**Processing Options:**
• Automatic format detection
• OCR for image files
• Structure preservation (titles, lists, tables)
• Metadata extraction

**Output Formats:**
• **JSON**: Complete structured data with metadata
• **CSV**: Flattened data for analysis
• **Summary**: Processing statistics and file information

**Commands:**
• 'help' - Show this help message
• 'process' - Process uploaded files
• 'process <file1> <file2>' - Process files from paths
• 'export' - Download processed results
• 'clear' - Clear session data
• 'demo' - Run a sample processing workflow

**Example Usage:**
```
# Upload files first, then:
process

# Or process specific files:
process /path/to/document.pdf /path/to/image.jpg
export
clear
```

**Tips:**
• Large files may take longer to process
• Image quality affects OCR accuracy
• Complex layouts are preserved when possible
• All processing happens locally for privacy

**Need More Help?**
Check the unstructured documentation for advanced features and configuration options."""
    
    await cl.Message(content=help_msg).send()

async def run_demo():
    """Run a demo processing workflow"""
    
    await cl.Message(content="🎬 **Demo Mode - Sample Processing Workflow**").send()
    
    # Check if we have example docs in the unstructured repo
    example_docs_path = Path("../unstructured/example-docs")
    if example_docs_path.exists():
        # Find some example files
        example_files = []
        for ext in ['.txt', '.pdf', '.docx']:
            files = list(example_docs_path.rglob(f"*{ext}"))
            if files:
                example_files.extend(files[:2])  # Take first 2 of each type
        
        if example_files:
            await cl.Message(content=f"📁 Found {len(example_files)} example files. Processing them...").send()
            await process_files_from_paths([str(f) for f in example_files])
        else:
            await cl.Message(content="❌ No example files found in the unstructured repository.").send()
    else:
        await cl.Message(content="❌ Example docs directory not found. Please ensure you're running from the correct location.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle user messages"""
    
    content = message.content.lower().strip()
    
    if content in ['help', '?', 'info']:
        await show_help_info()
    elif content.startswith('process'):
        # Extract file paths from the message
        parts = message.content.split()
        if len(parts) > 1:
            file_paths = parts[1:]
            await process_files_from_paths(file_paths)
        else:
            # Process uploaded files
            await process_uploaded_files()
    elif content in ['export', 'download', 'save']:
        await export_processed_data()
    elif content in ['clear', 'reset', 'new']:
        await clear_session_data()
    elif content in ['demo', 'example', 'sample']:
        await run_demo()
    else:
        # Default response
        await cl.Message(content="💡 **Tip**: Type 'help' for instructions, 'process' to start processing uploaded files, 'export' to download results, or 'demo' to see a sample workflow!").send()

if __name__ == "__main__":
    # This will be used when running the app
    print("Dataset Processing Tool with Chainlit and Unstructured")
    print("Run with: chainlit run dataset_processor.py")
