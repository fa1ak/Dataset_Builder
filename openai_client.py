"""
OpenAI API integration for enhanced document processing
"""
import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClient:
    """OpenAI API client for document analysis and content generation"""
    
    def __init__(self):
        """Initialize OpenAI client with configuration"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
        
        # Feature flags
        self.enable_summarization = os.getenv("ENABLE_SUMMARIZATION", "true").lower() == "true"
        self.enable_analysis = os.getenv("ENABLE_ANALYSIS", "true").lower() == "true"
        self.enable_questions = os.getenv("ENABLE_QUESTIONS", "true").lower() == "true"
        self.enable_content_generation = os.getenv("ENABLE_CONTENT_GENERATION", "true").lower() == "true"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available and configured"""
        try:
            return self.api_key is not None and self.api_key != "your_openai_api_key_here"
        except Exception:
            return False
    
    def summarize_document(self, text_content: str, max_length: int = 500) -> Dict[str, Any]:
        """Generate a summary of the document content"""
        if not self.enable_summarization or not self.is_available():
            return {"error": "Summarization not available"}
        
        try:
            prompt = f"""Please provide a comprehensive summary of the following document content. 
            Focus on the main points, key information, and important details.
            Keep the summary under {max_length} words.
            
            Document content:
            {text_content[:4000]}  # Limit to avoid token limits
            
            Summary:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates clear, concise summaries of documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "summary": summary,
                "word_count": len(summary.split()),
                "original_word_count": len(text_content.split())
            }
            
        except Exception as e:
            return {"error": f"Summarization failed: {str(e)}"}
    
    def analyze_document(self, text_content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze document content for insights and patterns"""
        if not self.enable_analysis or not self.is_available():
            return {"error": "Analysis not available"}
        
        try:
            analysis_prompts = {
                "general": "Analyze this document and provide insights about its structure, main topics, and key information.",
                "technical": "Analyze this technical document and identify key concepts, procedures, and important details.",
                "business": "Analyze this business document and identify key metrics, strategies, and important business information.",
                "academic": "Analyze this academic document and identify the main arguments, evidence, and conclusions."
            }
            
            prompt = f"""{analysis_prompts.get(analysis_type, analysis_prompts['general'])}
            
            Document content:
            {text_content[:4000]}
            
            Analysis:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a document analysis expert that provides detailed insights and analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "analysis": analysis,
                "analysis_type": analysis_type,
                "word_count": len(analysis.split())
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def answer_questions(self, text_content: str, questions: List[str]) -> Dict[str, Any]:
        """Answer questions about the document content"""
        if not self.enable_questions or not self.is_available():
            return {"error": "Question answering not available"}
        
        try:
            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            
            prompt = f"""Based on the following document content, please answer the questions provided.
            If the answer cannot be found in the document, please state that clearly.
            
            Document content:
            {text_content[:4000]}
            
            Questions:
            {questions_text}
            
            Answers:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on document content. Be accurate and cite specific parts of the document when possible."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            answers = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "answers": answers,
                "questions": questions,
                "word_count": len(answers.split())
            }
            
        except Exception as e:
            return {"error": f"Question answering failed: {str(e)}"}
    
    def generate_content(self, text_content: str, content_type: str = "report") -> Dict[str, Any]:
        """Generate new content based on the document"""
        if not self.enable_content_generation or not self.is_available():
            return {"error": "Content generation not available"}
        
        try:
            content_prompts = {
                "report": "Create a professional report based on this document content.",
                "summary": "Create a detailed summary of this document.",
                "outline": "Create a structured outline of this document.",
                "key_points": "Extract and list the key points from this document.",
                "recommendations": "Based on this document, provide recommendations and next steps."
            }
            
            prompt = f"""{content_prompts.get(content_type, content_prompts['report'])}
            
            Document content:
            {text_content[:4000]}
            
            Generated content:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content generator that creates high-quality, well-structured content based on source material."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "content": generated_content,
                "content_type": content_type,
                "word_count": len(generated_content.split())
            }
            
        except Exception as e:
            return {"error": f"Content generation failed: {str(e)}"}
    
    def extract_key_information(self, text_content: str) -> Dict[str, Any]:
        """Extract key information like dates, names, numbers, etc."""
        if not self.is_available():
            return {"error": "OpenAI API not available"}
        
        try:
            prompt = f"""Extract key information from this document and organize it into categories.
            Look for: dates, names, numbers, locations, organizations, key terms, and important facts.
            
            Document content:
            {text_content[:4000]}
            
            Please format the extracted information as JSON with categories like:
            {{
                "dates": ["date1", "date2"],
                "names": ["name1", "name2"],
                "numbers": ["number1", "number2"],
                "locations": ["location1", "location2"],
                "organizations": ["org1", "org2"],
                "key_terms": ["term1", "term2"],
                "important_facts": ["fact1", "fact2"]
            }}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting and categorizing key information from documents. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            extracted_info = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                parsed_info = json.loads(extracted_info)
                return {
                    "success": True,
                    "extracted_info": parsed_info,
                    "raw_response": extracted_info
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "extracted_info": {"raw_text": extracted_info},
                    "raw_response": extracted_info
                }
            
        except Exception as e:
            return {"error": f"Information extraction failed: {str(e)}"}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            # This would require additional API calls to get usage data
            return {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "features_enabled": {
                    "summarization": self.enable_summarization,
                    "analysis": self.enable_analysis,
                    "questions": self.enable_questions,
                    "content_generation": self.enable_content_generation
                }
            }
        except Exception as e:
            return {"error": f"Could not get usage stats: {str(e)}"}

# Global instance
openai_client = OpenAIClient() if os.getenv("OPENAI_API_KEY") else None
