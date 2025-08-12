import chainlit as cl
import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from unstructured.partition.auto import partition
from unstructured.documents.elements import Title, NarrativeText, ListItem, Table, Header, Footer, Text

# Global variable to store results (since cl.get_session() doesn't exist in this version)
processed_results = []

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    
    # Welcome message with instructions
    welcome_msg = """🚀 **Welcome to Dataset Processor!**

**How to use:**
1. **Process files**: Type `process /path/to/your/file.pdf` (or any supported format)
2. **View results**: Type `show` to see extracted content
3. **Export data**: Type `export` to download results
4. **Get help**: Type `help` for more options

**Supported formats**: PDF, DOCX, TXT, JPG, PNG, and more!

**Example**: `process /Users/username/Documents/resume.pdf`

Type `help` for detailed instructions or start processing a file!"""
    
    await cl.Message(content=welcome_msg).send()

async def process_files_from_paths(file_paths: List[str]):
    """Process files from file paths with real-time progress"""
    
    global processed_results # Access the global variable
    
    if not file_paths:
        await cl.Message(content="❌ No file paths provided.").send()
        return
    
    # Validate file paths
    valid_paths = []
    for path in file_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            await cl.Message(content=f"⚠️ **Warning**: File not found: {path}").send()
    
    if not valid_paths:
        await cl.Message(content="❌ No valid file paths found. Please check your paths and try again.").send()
        return
    
    await cl.Message(content=f"🔄 **Starting to process {len(valid_paths)} files...**").send()
    
    results = []
    total_files = len(valid_paths)
    
    for i, file_path in enumerate(valid_paths):
        try:
            await cl.Message(content=f"📄 **Processing file {i+1}/{total_files}**: {os.path.basename(file_path)}").send()
            
            # Process the file
            result = await process_single_file_from_path(file_path)
            results.append(result)
            
            await cl.Message(content=f"✅ **Successfully processed**: {os.path.basename(file_path)}").send()
            
        except Exception as e:
            error_msg = f"❌ **Error processing {os.path.basename(file_path)}**: {str(e)}"
            await cl.Message(content=error_msg).send()
            continue
    
    # Store results globally
    processed_results = results
    
    # Summary
    successful = len([r for r in results if r.get('success', False)])
    total_elements = sum([r.get('element_count', 0) for r in results if r.get('success', False)])
    
    summary_msg = f"""📊 **Processing Complete!**

**Summary:**
• Files processed: {len(valid_paths)}
• Successfully processed: {successful}
• Total elements extracted: {total_elements}

**Next steps:**
• Type `show` to preview extracted content
• Type `export` to download results
• Type `process /path/to/another/file` to process more files"""
    
    await cl.Message(content=summary_msg).send()

async def process_single_file_from_path(file_path: str) -> Dict[str, Any]:
    """Process a single file from path and return structured results"""

    try:
        # Show OCR warning for images
        file_ext = Path(file_path).suffix.lower()
        if file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            await cl.Message(content="🔍 **OCR Processing**: This is an image file. OCR text extraction may take a moment...").send()
        
        # Process with unstructured
        elements = partition(file_path)
        
        # Show processing progress
        await cl.Message(content=f"📊 **Analyzing structure**: Found {len(elements)} content elements...").send()
        
        # Convert to structured format with better error handling
        structured_data = []
        word_count = 0
        processed_count = 0
        skipped_count = 0
        
        for i, element in enumerate(elements):
            try:
                # Extract text content safely
                text = ""
                if hasattr(element, 'text') and element.text is not None:
                    text = str(element.text).strip()
                elif hasattr(element, '__str__'):
                    text = str(element).strip()
                
                # Skip if no meaningful text
                if not text or len(text) < 2:
                    continue
                
                # Determine element type safely
                element_type = "unknown"
                if isinstance(element, Title):
                    element_type = "title"
                elif isinstance(element, NarrativeText):
                    element_type = "narrative"
                elif isinstance(element, ListItem):
                    element_type = "list_item"
                elif isinstance(element, Table):
                    element_type = "table"
                elif isinstance(element, Header):
                    element_type = "header"
                elif isinstance(element, Footer):
                    element_type = "footer"
                elif isinstance(element, Text):
                    element_type = "text"
                else:
                    # Try to get class name for unknown types
                    class_name = element.__class__.__name__
                    element_type = class_name.lower()
                
                # Extract metadata safely
                metadata = {}
                try:
                    if hasattr(element, 'metadata') and element.metadata is not None:
                        if hasattr(element.metadata, 'to_dict'):
                            metadata = element.metadata.to_dict()
                        elif hasattr(element.metadata, '__dict__'):
                            metadata = {k: v for k, v in element.metadata.__dict__.items() 
                                      if not k.startswith('_') and v is not None}
                        else:
                            metadata = dict(element.metadata)
                except Exception:
                    metadata = {}
                
                # Extract coordinates safely
                coordinates = None
                try:
                    if hasattr(element, 'coordinates') and element.coordinates is not None:
                        if hasattr(element.coordinates, 'to_dict'):
                            coordinates = element.coordinates.to_dict()
                        elif hasattr(element.coordinates, '__dict__'):
                            coordinates = {k: v for k, v in element.coordinates.__dict__.items() 
                                         if not k.startswith('_') and v is not None}
                        else:
                            coordinates = dict(element.coordinates)
                except Exception:
                    coordinates = None
                
                # Add to structured data
                structured_data.append({
                    'type': element_type,
                    'text': text,
                    'metadata': metadata,
                    'coordinates': coordinates,
                    'element_index': i
                })
                
                # Update counts
                word_count += len(text.split())
                processed_count += 1
                
                # Show progress every 50 elements
                if (i + 1) % 50 == 0:
                    await cl.Message(content=f"📝 **Processing elements**: {i + 1}/{len(elements)} completed...").send()
                    
            except Exception as element_error:
                # Log element processing errors but continue
                skipped_count += 1
                if skipped_count <= 10:  # Only show first 10 errors to avoid spam
                    await cl.Message(content=f"⚠️ **Warning**: Skipped element {i+1} due to processing error: {type(element_error).__name__}: {str(element_error)[:100]}...").send()
                elif skipped_count == 11:
                    await cl.Message(content="⚠️ **Note**: Additional element processing errors will be logged but not displayed to avoid spam...").send()
                continue
        
        # Show final processing summary
        summary_msg = f"""📋 **Processing Summary for {os.path.basename(file_path)}**:
• Total elements found: {len(elements)}
• Successfully processed: {processed_count}
• Skipped due to errors: {skipped_count}
• Words extracted: {word_count:,}
• File size: {os.path.getsize(file_path):,} bytes"""
        
        await cl.Message(content=summary_msg).send()
        
        return {
            'success': True,
            'filename': os.path.basename(file_path),
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'word_count': word_count,
            'elements': structured_data,
            'element_count': len(structured_data),
            'file_type': Path(file_path).suffix.lower(),
            'total_elements_found': len(elements),
            'processed_count': processed_count,
            'skipped_count': skipped_count
        }
        
    except Exception as e:
        # More detailed error information
        error_details = f"❌ **Processing Error** for {os.path.basename(file_path)}:\n\n"
        error_details += f"**Error Type**: {type(e).__name__}\n"
        error_details += f"**Error Message**: {str(e)}\n\n"
        error_details += "**Troubleshooting Tips**:\n"
        error_details += "• Check if the file is corrupted or password-protected\n"
        error_details += "• Ensure the file format is supported\n"
        error_details += "• Try with a different PDF file\n"
        error_details += "• Check if the file contains complex layouts or special characters"
        
        await cl.Message(content=error_details).send()
        raise e

async def show_processed_content():
    """Show a preview of the processed content"""
    
    global processed_results # Access the global variable
    
    if not processed_results:
        await cl.Message(content="❌ No processed data to show. Please process some files first.").send()
        return
    
    # Show summary of all processed files
    summary_msg = f"📊 **Processed Files Summary**\n\n"
    for i, result in enumerate(processed_results):
        if result.get('success', False):
            summary_msg += f"**{i+1}. {result['filename']}**\n"
            summary_msg += f"   • Elements: {result['element_count']:,}\n"
            summary_msg += f"   • Words: {result['word_count']:,}\n"
            summary_msg += f"   • Size: {result['file_size']:,} bytes\n"
            summary_msg += f"   • Type: {result['file_type']}\n\n"
    
    await cl.Message(content=summary_msg).send()
    
    # Show sample content from each file
    for i, result in enumerate(processed_results):
        if result.get('success', False) and result.get('elements'):
            elements = result['elements']
            
            # Show first few elements as preview
            preview_msg = f"📄 **Preview of {result['filename']}**\n\n"
            
            # Show first 5 elements
            for j, element in enumerate(elements[:5]):
                preview_msg += f"**{j+1}. {element['type'].title()}**\n"
                preview_msg += f"   {element['text'][:200]}{'...' if len(element['text']) > 200 else ''}\n\n"
            
            if len(elements) > 5:
                preview_msg += f"... and {len(elements) - 5} more elements\n\n"
            
            await cl.Message(content=preview_msg).send()

async def export_processed_data():
    """Export processed data in various formats"""
    
    global processed_results # Access the global variable
    
    if not processed_results:
        await cl.Message(content="❌ No processed data to export. Please process some files first.").send()
        return
    
    try:
        # Create export directory
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        # Export as JSON
        json_file = os.path.join(export_dir, "processed_data.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(processed_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Export as CSV (simplified)
        csv_file = os.path.join(export_dir, "processed_data.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("filename,element_count,word_count,file_size,file_type\n")
            for result in processed_results:
                if result.get('success', False):
                    f.write(f"{result['filename']},{result['element_count']},{result['word_count']},{result['file_size']},{result['file_type']}\n")
        
        # Export detailed text content
        text_file = os.path.join(export_dir, "extracted_text.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            for result in processed_results:
                if result.get('success', False):
                    f.write(f"\n{'='*50}\n")
                    f.write(f"FILE: {result['filename']}\n")
                    f.write(f"ELEMENTS: {result['element_count']}\n")
                    f.write(f"WORDS: {result['word_count']}\n")
                    f.write(f"{'='*50}\n\n")
                    
                    for element in result.get('elements', []):
                        f.write(f"[{element['type'].upper()}]\n")
                        f.write(f"{element['text']}\n\n")
        
        export_msg = f"""📤 **Export Complete!**

**Files created in 'exports' directory:**
• `processed_data.json` - Complete structured data
• `processed_data.csv` - Summary statistics
• `extracted_text.txt` - All extracted text content

**Export location**: `{os.path.abspath(export_dir)}`

You can now download these files from your system."""
        
        await cl.Message(content=export_msg).send()
        
    except Exception as e:
        await cl.Message(content=f"❌ **Export Error**: {str(e)}").send()

async def clear_session_data():
    """Clear all processed data from the session"""
    
    global processed_results # Access the global variable
    processed_results = []
    await cl.Message(content="🗑️ Session data cleared. You can start fresh!").send()

async def show_help_info():
    """Show help information"""
    
    help_msg = """📚 **Dataset Processor Help**

**Commands:**
• `help` - Show this help message
• `process /path/to/file.pdf` - Process a file from path
• `show` - Preview extracted content
• `export` - Download results as files
• `clear` - Clear all processed data
• `demo` - Run a sample workflow

**Supported File Types:**
• **Documents**: PDF, DOCX, TXT, RTF
• **Images**: JPG, PNG, TIFF, BMP (with OCR)
• **Spreadsheets**: XLSX, CSV
• **Presentations**: PPTX
• **And more!**

**Examples:**
• `process /Users/username/Documents/resume.pdf`
• `process /path/to/image.jpg`
• `process /path/to/document.docx`

**Tips:**
• Use absolute paths for best results
• Large files may take longer to process
• OCR processing is automatic for images
• Results are stored in memory until exported

**Need help?** Type `help` anytime!"""
    
    await cl.Message(content=help_msg).send()

async def run_demo():
    """Run a demo workflow"""
    
    demo_msg = """🎯 **Demo Workflow**

This is a demonstration of the Dataset Processor capabilities.

**To get started:**
1. **Process a file**: Type `process /path/to/your/file.pdf`
2. **View results**: Type `show` to see what was extracted
3. **Export data**: Type `export` to download the results

**Sample file paths you can try:**
• Any PDF document on your system
• Text files (.txt)
• Word documents (.docx)
• Images (.jpg, .png)

**Example command:**
`process /Users/username/Desktop/sample.pdf`

Try processing a file and see the magic happen! 🚀"""
    
    await cl.Message(content=demo_msg).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle user messages"""

    content = message.content.lower().strip()

    if content in ['help', '?', 'info']:
        await show_help_info()
    elif content.startswith('process'):
        parts = message.content.split()
        if len(parts) > 1:
            file_paths = parts[1:]
            await process_files_from_paths(file_paths)
        else:
            await cl.Message(content="❌ Please provide file paths. Example: 'process /path/to/your/file.pdf'").send()
    elif content in ['show', 'preview', 'view']:
        await show_processed_content() # New command
    elif content in ['export', 'download', 'save']:
        await export_processed_data()
    elif content in ['clear', 'reset', 'new']:
        await clear_session_data()
    elif content in ['demo', 'example', 'sample']:
        await run_demo()
    else:
        await cl.Message(content="💡 **Tip**: Type 'help' for instructions, 'process /path/to/file.pdf' to start processing, 'show' to preview content, 'export' to download results, or 'demo' to see a sample workflow!").send()

if __name__ == "__main__":
    # This will be used when running the app
    print("Dataset Processing Tool with Chainlit and Unstructured")
    print("Run with: chainlit run dataset_processor.py")
