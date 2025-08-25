"""
Enhanced file upload routes with full service integration
Handles CSV, TXT, and JSON files with chunking and translation
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from app.utils.file_validator import FileValidator
from app.models.review_models import ProcessingResult
import time

logger = logging.getLogger(__name__)

# Create Blueprint
upload_enhanced_bp = Blueprint('upload_enhanced', __name__)

# Initialize file validator
file_validator = FileValidator()

# Services will be imported from get_services
def get_upload_services():
    """Get required services for upload processing"""
    from app.routes.api_routes import get_services
    services = get_services()
    return {
        'language': services[0],
        'sentiment': services[1],
        'insights': services[2],
        'text_processor': services[3],
        'chunking': services[4],
        'translation': services[5],
        'file_processing': services[6]
    }

@upload_enhanced_bp.route('/file/analyze', methods=['POST'])
def analyze_file():
    """
    Enhanced file upload and analysis endpoint
    
    Accepts: CSV, TXT, or JSON files
    
    Returns:
        JSON response with detailed analysis results
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file has a filename
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        is_valid, error_message = file_validator.validate_file(file)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Get services
        services = get_upload_services()
        
        # Process file to extract texts
        logger.info(f"Processing file: {file.filename}")
        file_result = services['file_processing'].process_file(file)
        
        if not file_result['success']:
            return jsonify({
                'error': file_result.get('error', 'Failed to process file'),
                'details': file_result
            }), 400
        
        texts = file_result.get('texts', [])
        
        if not texts:
            return jsonify({'error': 'No valid texts found in file'}), 400
        
        logger.info(f"Extracted {len(texts)} texts from file")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Process options
        options = {
            'chunk_large_texts': request.form.get('chunk_large_texts', 'true').lower() == 'true',
            'translate': request.form.get('translate', 'true').lower() == 'true',
            'generate_insights': request.form.get('generate_insights', 'true').lower() == 'true'
        }
        
        # Process texts with chunking if needed
        all_chunks = []
        for text in texts:
            if options['chunk_large_texts'] and len(text) > 512:
                chunks = services['chunking'].chunk_text(text)
                all_chunks.extend([chunk['text'] for chunk in chunks])
            else:
                all_chunks.append(text)
        
        logger.info(f"Processing {len(all_chunks)} text chunks")
        
        # Language detection and translation with per-chunk tracking
        languages_detected = set()
        processed_texts = []
        translation_results = []
        chunk_languages = []  # Track language for each specific chunk
        
        for chunk in all_chunks:
            # Detect language for this specific chunk
            lang, lang_conf = services['language'].detect_language(chunk)
            languages_detected.add(lang)
            chunk_languages.append(lang)  # Store the specific language for this chunk
            
            # Translate if needed
            if options['translate'] and services['translation'].enabled:
                trans_result = services['translation'].translate_to_english(chunk, lang)
                translation_results.append(trans_result)
                processed_texts.append(trans_result['translated_text'])
            else:
                translation_results.append({
                    'original_text': chunk,
                    'translated_text': chunk,
                    'source_language': lang,
                    'was_translated': False
                })
                processed_texts.append(chunk)
        
        # Batch sentiment analysis for better performance
        logger.info(f"Performing batch sentiment analysis on {len(processed_texts)} texts")
        sentiments = services['sentiment'].batch_analyze(processed_texts)
        sentiment_details = []
        
        # Process results with corresponding metadata
        for i, (text, (sentiment, confidence)) in enumerate(zip(processed_texts, sentiments)):
            # Get the corresponding language and translation info for this specific chunk
            original_text = all_chunks[i] if i < len(all_chunks) else text
            text_language = chunk_languages[i] if i < len(chunk_languages) else 'unknown'
            
            # Check if this text was translated
            was_translated = False
            translated_text = None
            if i < len(translation_results):
                trans_result = translation_results[i]
                was_translated = trans_result.get('was_translated', False)
                translated_text = trans_result.get('translated_text', text) if was_translated else None
            
            sentiment_details.append({
                'text': text,  # Analyzed text (translated if applicable)
                'original_text': original_text,  # Original text before translation
                'translated_text': translated_text,  # Translated text if applicable
                'sentiment': sentiment.value.title(),  # Capitalize (Positive, Negative, Neutral)
                'confidence': confidence,
                'language': _get_language_name(text_language) if text_language else 'Unknown',
                'was_translated': was_translated,
                'translation_info': {
                    'source_language': text_language,
                    'target_language': 'en' if was_translated else text_language,
                    'was_translated': was_translated
                }
            })
        
        # Calculate statistics
        positive_count = sum(1 for s, _ in sentiments if s.value == 'positive')
        negative_count = sum(1 for s, _ in sentiments if s.value == 'negative')
        neutral_count = sum(1 for s, _ in sentiments if s.value == 'neutral')
        
        # Processing time
        processing_time = time.time() - start_time
        
        # Create processing result
        result = ProcessingResult(
            job_id=job_id,
            total_reviews=len(texts),
            processed_reviews=len(sentiments),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            languages_detected=list(languages_detected),
            processing_time=processing_time,
            created_at=datetime.utcnow()
        )
        
        # Generate insights if requested
        insights = None
        if options['generate_insights']:
            try:
                insights = services['insights'].generate_insights(result)
            except Exception as e:
                logger.warning(f"Failed to generate insights: {e}")
                insights = "Insights generation unavailable"
        
        # Prepare response in expected frontend format
        response = {
            'job_id': job_id,
            'results': sentiment_details,  # Full detailed results for frontend
            'summary': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            },
            'processing_time': processing_time,
            'timestamp': datetime.utcnow().isoformat(),
            'file_info': {
                'filename': file.filename,
                'format': file_result.get('format'),
                'total_texts': len(texts),
                'total_chunks': len(all_chunks),
                'languages_detected': list(languages_detected)
            }
        }
        
        # Add insights if available
        if insights and insights != "Insights generation unavailable":
            if isinstance(insights, str):
                # Split insights into array if it's a single string
                response['insights'] = [line.strip() for line in insights.split('\n') if line.strip()]
            else:
                response['insights'] = insights
        
        # Add file-specific metadata if available
        if 'metadata' in file_result:
            response['file_metadata'] = file_result['metadata']
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error during file processing',
            'details': str(e)
        }), 500

@upload_enhanced_bp.route('/file/sample/<file_format>', methods=['GET'])
def get_sample_file(file_format):
    """
    Get sample data for a specific file format
    
    Args:
        file_format: Format type (csv, txt, json)
        
    Returns:
        Sample data or error
    """
    try:
        services = get_upload_services()
        
        if file_format not in ['csv', 'json']:
            return jsonify({'error': 'Invalid format. Use csv or json'}), 400
        
        sample_data = services['file_processing'].get_sample_data(file_format)
        
        return jsonify({
            'format': file_format,
            'sample_data': sample_data,
            'instructions': get_format_instructions(file_format)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting sample data: {e}")
        return jsonify({'error': 'Failed to generate sample data'}), 500

def get_format_instructions(file_format):
    """Get instructions for file format"""
    instructions = {
        'csv': 'CSV file should have columns with text data. Common column names: text, review, comment, feedback',
        'json': 'JSON array of objects with text fields, or object with reviews array. Fields: text, review, content, message'
    }
    return instructions.get(file_format, 'Unknown format')

def _get_language_name(language_code):
    """Convert language code to readable name"""
    language_names = {
        'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
        'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'pl': 'Polish',
        'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean', 'zh-cn': 'Chinese',
        'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi', 'tr': 'Turkish',
        'sv': 'Swedish', 'da': 'Danish', 'no': 'Norwegian', 'fi': 'Finnish'
    }
    return language_names.get(language_code.lower(), language_code.title())
