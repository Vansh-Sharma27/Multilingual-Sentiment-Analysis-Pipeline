"""
API routes for sentiment analysis operations
RESTful endpoints for text analysis and results retrieval
"""

from flask import Blueprint, request, jsonify, current_app, render_template
import logging
from datetime import datetime, timezone
import uuid
from app.services.language_service import LanguageService
from app.services.optimized_sentiment_service import OptimizedSentimentService
from app.services.insights_service import InsightsService
from app.services.chunking_service import ChunkingService
from app.services.translation_service import TranslationService
from app.services.file_processing_service import FileProcessingService
from app.models.review_models import ProcessingResult, AnalysisRequest, TextChunk
from app.utils.text_processor import TextProcessor
import time

logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Services will be initialized lazily
language_service = None
sentiment_service = None
insights_service = None
text_processor = None
chunking_service = None
translation_service = None
file_processing_service = None

def get_services():
    """Lazy initialization of services to ensure environment variables are loaded"""
    global language_service, sentiment_service, insights_service, text_processor
    global chunking_service, translation_service, file_processing_service
    
    if language_service is None:
        language_service = LanguageService()
    if sentiment_service is None:
        sentiment_service = OptimizedSentimentService()
    if insights_service is None:
        insights_service = InsightsService()
    if text_processor is None:
        text_processor = TextProcessor()
    if chunking_service is None:
        chunking_service = ChunkingService()
    if translation_service is None:
        translation_service = TranslationService()
    if file_processing_service is None:
        file_processing_service = FileProcessingService()
    
    return (language_service, sentiment_service, insights_service, text_processor,
            chunking_service, translation_service, file_processing_service)

# In-memory storage for results (in production, use a database)
results_store = {}

@api_bp.route('/debug/env', methods=['GET'])
def debug_env():
    """
    Debug endpoint to check environment variables (remove in production)
    """
    import os
    # Get services to ensure they're initialized
    services = get_services()
    sentiment_svc = services[1]
    insights_svc = services[2]
    
    return jsonify({
        'huggingface_api_key_set': bool(os.environ.get('HUGGINGFACE_API_KEY')),
        'huggingface_key_prefix': os.environ.get('HUGGINGFACE_API_KEY', '')[:7] + '...' if os.environ.get('HUGGINGFACE_API_KEY') else 'NOT SET',
        'gemini_api_key_set': bool(os.environ.get('GEMINI_API_KEY')),
        'sentiment_service_has_key': bool(sentiment_svc.api_key),
        'insights_service_has_key': bool(insights_svc.ollama_service.api_key),
        'flask_env': os.environ.get('FLASK_ENV', 'not set'),
        'all_env_keys': list(os.environ.keys())
    }), 200

@api_bp.route('/gpu-status', methods=['GET'])
def gpu_status():
    """
    Check GPU status and availability
    
    Returns:
        JSON response with GPU information
    """
    # Get services to check GPU status
    services = get_services()
    sentiment_svc = services[1]
    
    if hasattr(sentiment_svc, 'get_gpu_status'):
        gpu_info = sentiment_svc.get_gpu_status()
    else:
        gpu_info = {'gpu_available': False, 'message': 'GPU status not available'}
    
    return jsonify(gpu_info), 200

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    System health check endpoint
    
    Returns:
        JSON response with system status
    """
    # Initialize services if not already done
    services = get_services()
    insights_svc = services[2]
    
    # Get service stats
    sentiment_stats = services[1].get_stats()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'services': {
            'language': 'active',
            'sentiment': sentiment_stats.get('status', 'active'),
            'insights': 'active',
            'translation': 'active',
            'provider': 'Ollama GPT OSS-120B'
        }
    }), 200

@api_bp.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """
    Test endpoint for frontend connectivity debugging
    
    Returns:
        JSON response with request information
    """
    return jsonify({
        'status': 'success',
        'message': 'API is working correctly',
        'method': request.method,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'headers': dict(request.headers),
        'args': dict(request.args),
        'data': request.get_json() if request.is_json else None
    }), 200

@api_bp.route('/analyze/enhanced', methods=['POST'])
def analyze_enhanced():
    """
    Enhanced text analysis using GPT OSS-12B advanced capabilities
    
    Expected JSON payload:
    {
        "text": "Text to analyze comprehensively"
    }
    
    Returns:
        JSON response with enhanced analysis including emotion, themes, style, etc.
    """
    try:
        # Validate request
        if not request.json or 'text' not in request.json:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = request.json['text']
        
        # Validate text length
        if len(text.strip()) < 3:
            return jsonify({'error': 'Text too short for enhanced analysis'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long. Maximum 5000 characters for enhanced analysis'}), 400
        
        # Get services
        services = get_services()
        sentiment_svc = services[1]
        
        # Perform enhanced analysis using Ollama GPT OSS-12B
        try:
            enhanced_analysis = sentiment_svc.ollama_service.enhance_text_analysis(text)
            
            if 'error' in enhanced_analysis:
                # Fallback to basic analysis
                sentiment, confidence = sentiment_svc.analyze_sentiment(text)
                enhanced_analysis = {
                    'sentiment': sentiment.value,
                    'confidence': confidence,
                    'emotion': 'unknown',
                    'key_themes': ['general'],
                    'language_style': 'unknown',
                    'urgency_level': 'medium',
                    'customer_intent': 'unknown'
                }
            
            # Add basic sentiment if not provided
            if 'sentiment' not in enhanced_analysis:
                sentiment, confidence = sentiment_svc.analyze_sentiment(text)
                enhanced_analysis['sentiment'] = sentiment.value
                enhanced_analysis['confidence'] = confidence
            
            # Detect language
            language_svc = services[0]
            language_code, lang_confidence = language_svc.detect_language(text)
            language_name = _get_language_name(language_code)
            
            response = {
                'text': text,
                'language': language_name,
                'language_code': language_code,
                'language_confidence': lang_confidence,
                'enhanced_analysis': enhanced_analysis,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'model': 'GPT OSS-120B via Ollama'
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            # Fallback to basic sentiment analysis
            sentiment, confidence = sentiment_svc.analyze_sentiment(text)
            language_svc = services[0]
            language_code, lang_confidence = language_svc.detect_language(text)
            
            return jsonify({
                'text': text,
                'language': _get_language_name(language_code),
                'language_code': language_code,
                'basic_analysis': {
                    'sentiment': sentiment.value,
                    'confidence': confidence
                },
                'error': 'Enhanced analysis unavailable, showing basic analysis',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f"Error in enhanced analysis: {e}")
        return jsonify({'error': 'Internal server error during enhanced analysis'}), 500

@api_bp.route('/detect-language', methods=['POST'])
def detect_language():
    """
    Detect language of input text
    
    Expected JSON payload:
    {
        "text": "Text to analyze for language"
    }
    
    Returns:
        JSON response with language detection results
    """
    try:
        # Validate request
        if not request.json or 'text' not in request.json:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = request.json['text']
        
        # Validate text length
        if len(text.strip()) < 3:
            return jsonify({'error': 'Text too short for language detection'}), 400
        
        # Get language service
        services = get_services()
        language_svc = services[0]
        
        # Detect language
        language_code, confidence = language_svc.detect_language(text)
        
        # Convert language code to readable name
        language_name = _get_language_name(language_code)
        
        return jsonify({
            'language': language_name,
            'language_code': language_code,
            'confidence': confidence,
            'text_sample': text[:50] + '...' if len(text) > 50 else text
        }), 200
        
    except Exception as e:
        logger.error(f"Error in language detection: {e}")
        return jsonify({'error': 'Language detection failed'}), 500

@api_bp.route('/analyze', methods=['POST'])
def analyze_text():
    """
    Analyze sentiment of single text input
    
    Expected JSON payload:
    {
        "text": "Your text to analyze",
        "options": {
            "include_translation": true,
            "generate_insights": true
        }
    }
    
    Returns:
        JSON response with analysis results
    """
    try:
        # Validate JSON content type and parse JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            request_data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        # Validate request
        if not request_data or 'text' not in request_data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = request_data['text']
        
        # Handle both simple format ({text, translate}) and complex format ({text, options})
        if 'translate' in request_data:
            # Simple format from original frontend
            options = {
                'include_translation': request_data.get('translate', True),
                'generate_insights': False
            }
        else:
            # Complex format with options object
            options = request_data.get('options', {})
        
        # Validate text length
        if len(text) < 3:
            return jsonify({'error': 'Text too short for analysis'}), 400
        
        if len(text) > 10000:
            return jsonify({'error': 'Text too long. Maximum 10000 characters'}), 400
        
        # Start processing timer
        start_time = time.time()
        
        # Get services (lazy initialization)
        services = get_services()
        language_svc = services[0]
        sentiment_svc = services[1]
        insights_svc = services[2]
        
        # Language detection
        language, lang_confidence = language_svc.detect_language(text)
        logger.info(f"Detected language: {language} (confidence: {lang_confidence:.2f})")
        
        # Translation if needed
        translated_text = text
        was_translated = False
        if options.get('include_translation', True) and language != 'en':
            # Use the translation service instead of language service's basic method
            translation_svc = services[5]  # Get translation service
            trans_result = translation_svc.translate_to_english(text, language)
            if trans_result.get('was_translated'):
                translated_text = trans_result.get('translated_text', text)
                was_translated = True
            else:
                translated_text = text
        
        # Sentiment analysis
        sentiment, sent_confidence = sentiment_svc.analyze_sentiment(translated_text)
        
        # Processing time
        processing_time = time.time() - start_time
        
        # Create single result entry with translation info
        result_entry = {
            'text': text,
            'sentiment': sentiment.value.title(),  # Capitalize first letter (Positive, Negative, Neutral)
            'confidence': sent_confidence,
            'language': _get_language_name(language) if language else 'Unknown',
            'original_text': text,
            'translated_text': translated_text if was_translated else None,
            'was_translated': was_translated,
            'translation_info': {
                'source_language': language,
                'target_language': 'en' if was_translated else language,
                'was_translated': was_translated
            }
        }
        
        # Create summary (single text always counts as 1)
        summary = {
            'positive': 1 if sentiment.value == 'positive' else 0,
            'negative': 1 if sentiment.value == 'negative' else 0,
            'neutral': 1 if sentiment.value == 'neutral' else 0
        }
        
        # Prepare response in expected frontend format
        response = {
            'results': [result_entry],
            'summary': summary,
            'processing_time': processing_time,
            'job_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Generate insights if requested (default: true for single text)
        if options.get('generate_insights', True):
            try:
                # Create a simple processing result for insights
                result = ProcessingResult(
                    job_id=response['job_id'],
                    total_reviews=1,
                    processed_reviews=1,
                    positive_count=summary['positive'],
                    negative_count=summary['negative'],
                    neutral_count=summary['neutral'],
                    languages_detected=[language],
                    processing_time=processing_time,
                    created_at=datetime.now(timezone.utc)
                )
                insights = insights_svc.generate_insights(result)
                response['insights'] = [insights] if isinstance(insights, str) else insights
            except Exception as e:
                logger.warning(f"Failed to generate insights: {e}")
                # Provide fallback insights
                response['insights'] = [
                    f"Text analyzed as {sentiment.value} sentiment with {sent_confidence:.0%} confidence.",
                    f"Language detected as {language} with {lang_confidence:.0%} confidence.",
                    "Consider analyzing more text samples for comprehensive insights."
                ]
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in text analysis: {e}")
        return jsonify({'error': 'Internal server error during analysis'}), 500

@api_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple texts in batch
    
    Expected JSON payload:
    {
        "texts": ["text1", "text2", ...],
        "options": {
            "parallel_processing": true,
            "generate_insights": true
        }
    }
    
    Returns:
        JSON response with batch analysis results
    """
    try:
        # Validate request
        if not request.json or 'texts' not in request.json:
            return jsonify({'error': 'Texts field is required'}), 400
        
        texts = request.json['texts']
        options = request.json.get('options', {})
        
        # Validate batch size
        if not texts:
            return jsonify({'error': 'No texts provided'}), 400
        
        if len(texts) > 100:
            return jsonify({'error': 'Batch size too large. Maximum 100 texts'}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start processing timer
        start_time = time.time()
        
        # Get services (lazy initialization)
        services = get_services()
        language_svc = services[0]
        sentiment_svc = services[1]
        insights_svc = services[2]
        
        # Process texts
        results = []
        languages_detected = set()
        
        # Create chunks for parallel processing
        if options.get('parallel_processing', True) and len(texts) > 5:
            chunks = [TextChunk(i, text, i, i+1) for i, text in enumerate(texts)]
            
            # Detect languages first
            for chunk in chunks:
                lang, _ = language_svc.detect_language(chunk.text)
                chunk.language = lang
                languages_detected.add(lang)
            
            # Parallel sentiment analysis
            sentiments = sentiment_svc.parallel_analyze(chunks)
        else:
            # Sequential processing
            sentiments = []
            for text in texts:
                lang, _ = language_svc.detect_language(text)
                languages_detected.add(lang)
                sentiment, confidence = sentiment_svc.analyze_sentiment(text)
                sentiments.append((sentiment, confidence))
        
        # Calculate statistics
        stats = sentiment_svc.get_sentiment_statistics(sentiments)
        
        # Processing time
        processing_time = time.time() - start_time
        
        # Create processing result
        result = ProcessingResult(
            job_id=job_id,
            total_reviews=len(texts),
            processed_reviews=len(sentiments),
            positive_count=stats['positive_count'],
            negative_count=stats['negative_count'],
            neutral_count=stats['neutral_count'],
            languages_detected=list(languages_detected),
            processing_time=processing_time,
            created_at=datetime.now(timezone.utc)
        )
        
        # Generate insights if requested
        if options.get('generate_insights', True):
            result.gemini_insights = insights_svc.generate_insights(result)
        
        # Store result for retrieval
        results_store[job_id] = result
        
        # Create response
        response = result.to_dict()
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        return jsonify({'error': 'Internal server error during batch analysis'}), 500

@api_bp.route('/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """
    Retrieve analysis results by job ID
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        JSON response with stored results
    """
    try:
        # Check if job exists
        if job_id not in results_store:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get stored result
        result = results_store[job_id]
        
        # Convert to dictionary and return
        return jsonify(result.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error retrieving results: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/results/<job_id>', methods=['DELETE'])
def delete_results(job_id):
    """
    Delete stored analysis results
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        JSON response confirming deletion
    """
    try:
        # Check if job exists
        if job_id not in results_store:
            return jsonify({'error': 'Job not found'}), 404
        
        # Delete result
        del results_store[job_id]
        
        return jsonify({
            'message': 'Results deleted successfully',
            'job_id': job_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting results: {e}")
        return jsonify({'error': 'Internal server error'}), 500

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
