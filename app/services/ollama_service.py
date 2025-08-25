"""
Ollama API integration service
Handles sentiment analysis and insights generation using GPT OSS-12B model
"""

import logging
import os
import hashlib
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from ollama import Client
from app.models.review_models import SentimentLabel, ProcessingResult
import json
import time

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for Ollama API integration using GPT OSS-12B model"""
    
    def __init__(self):
        """Initialize Ollama service with API configuration"""
        self.api_key = os.environ.get('OLLAMA_API_KEY', '843da26fdc2545c5b01aa2e094f83699.vMZEWzSM4bI4AFhVinBVAJTu')
        self.host = os.environ.get('OLLAMA_HOST', 'https://ollama.com')
        self.model = "gpt-oss:120b"  # GPT OSS-120B model (correct format with colon)
        self.client = None
        self.temperature = 0.1  # Low temperature for consistent results
        self.max_tokens = 1000
        
        # Initialize caches for performance optimization
        self.sentiment_cache = {}  # Cache for sentiment analysis results
        self.translation_cache = {}  # Cache for translation results
        self.max_cache_size = 1000  # Maximum items to cache
        
        self._initialize_client()
    
    def _get_cache_key(self, text: str, operation: str = "") -> str:
        """Generate a cache key for text operations"""
        # Create a hash of the text for consistent cache keys
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{operation}_{text_hash}"
    
    def _manage_cache_size(self, cache_dict: dict):
        """Manage cache size using LRU eviction"""
        if len(cache_dict) >= self.max_cache_size:
            # Remove oldest 10% of entries
            remove_count = self.max_cache_size // 10
            oldest_keys = list(cache_dict.keys())[:remove_count]
            for key in oldest_keys:
                del cache_dict[key]
    
    def _initialize_client(self):
        """Initialize Ollama client"""
        try:
            # Initialize Ollama client with proper configuration including auth headers
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            # Try different client configurations
            try:
                # Method 1: Client with headers
                self.client = Client(host=self.host, headers=headers)
                logger.info("Trying Ollama client with auth headers...")
            except Exception:
                # Method 2: Client without headers (for local Ollama instances)
                self.client = Client(host=self.host)
                logger.info("Trying Ollama client without auth headers...")
            
            # Test connection by trying to list models
            try:
                models = self.client.list()
                logger.info(f"Ollama client initialized successfully. Available models: {[m['name'] for m in models['models']] if 'models' in models else 'Unable to list models'}")
                
                # Check if our model is available
                available_models = [m['name'] for m in models.get('models', [])]
                if self.model not in available_models:
                    logger.warning(f"Model {self.model} not found in available models: {available_models}")
                    logger.info(f"Available models: {available_models}")
                    
                    # Use the first available model as fallback
                    if available_models:
                        fallback_model = available_models[0]
                        logger.info(f"Using fallback model: {fallback_model}")
                        self.model = fallback_model
                else:
                    logger.info(f"✅ Model {self.model} is available")
                        
            except Exception as test_error:
                logger.warning(f"Could not test Ollama connection: {test_error}")
                
            logger.info("Ollama service initialized with GPT OSS-120B model")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            self.client = None
    
    def analyze_sentiment(self, text: str) -> Tuple[SentimentLabel, float]:
        """
        Analyze sentiment using GPT OSS-12B model with caching
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            Tuple of (SentimentLabel, confidence_score)
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(text, "sentiment")
            if cache_key in self.sentiment_cache:
                logger.debug(f"Cache hit for sentiment analysis: {text[:50]}...")
                return self.sentiment_cache[cache_key]
            
            if not self.client:
                logger.warning("Ollama client not available, using fallback")
                return self._fallback_sentiment(text)
            
            # Create sentiment analysis prompt
            prompt = f"""Analyze the sentiment of the following text and respond with ONLY a JSON object in this exact format:
{{"sentiment": "positive|negative|neutral", "confidence": 0.85, "reasoning": "brief explanation"}}

Text to analyze: "{text}"

Response:"""
            
            # Make API call with proper error handling for auth
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    options={
                        'temperature': self.temperature,
                        'num_predict': 200  # Ollama uses num_predict instead of max_tokens
                    }
                )
                logger.debug(f"Ollama response: {response}")
                
            except Exception as chat_error:
                logger.error(f"Chat API error: {chat_error}")
                # If we get an auth error, try re-initializing the client
                if "unauthorized" in str(chat_error).lower() or "401" in str(chat_error):
                    logger.info("Attempting to re-initialize client due to auth error...")
                    self._initialize_client()
                    # Retry once
                    try:
                        response = self.client.chat(
                            model=self.model,
                            messages=[{'role': 'user', 'content': prompt}],
                            options={'temperature': self.temperature, 'num_predict': 200}
                        )
                    except Exception:
                        return self._fallback_sentiment(text)
                else:
                    return self._fallback_sentiment(text)
            
            # Parse response
            if response and 'message' in response:
                content = response['message']['content'].strip()
                
                # Try to parse JSON response
                try:
                    result = json.loads(content)
                    sentiment_str = result.get('sentiment', 'neutral').lower()
                    confidence = float(result.get('confidence', 0.7))
                    
                    # Map to SentimentLabel
                    if sentiment_str == 'positive':
                        sentiment = SentimentLabel.POSITIVE
                    elif sentiment_str == 'negative':
                        sentiment = SentimentLabel.NEGATIVE
                    else:
                        sentiment = SentimentLabel.NEUTRAL
                    
                    # Ensure confidence is in valid range
                    confidence = max(0.5, min(0.95, confidence))
                    
                    # Cache the result
                    result = (sentiment, confidence)
                    self._manage_cache_size(self.sentiment_cache)
                    self.sentiment_cache[cache_key] = result
                    
                    logger.info(f"Sentiment analysis: {sentiment_str} ({confidence:.2f})")
                    return result
                    
                except json.JSONDecodeError:
                    # Fallback parsing if JSON fails
                    content_lower = content.lower()
                    if 'positive' in content_lower:
                        result = (SentimentLabel.POSITIVE, 0.75)
                    elif 'negative' in content_lower:
                        result = (SentimentLabel.NEGATIVE, 0.75)
                    else:
                        result = (SentimentLabel.NEUTRAL, 0.65)
                    
                    # Cache the fallback result
                    self._manage_cache_size(self.sentiment_cache)
                    self.sentiment_cache[cache_key] = result
                    return result
            
            # Fallback if no valid response
            result = self._fallback_sentiment(text)
            self._manage_cache_size(self.sentiment_cache)
            self.sentiment_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Ollama sentiment analysis failed: {e}")
            return self._fallback_sentiment(text)
    
    def generate_insights(self, processing_result: ProcessingResult) -> str:
        """
        Generate insights from sentiment analysis results using GPT OSS-12B
        
        Args:
            processing_result: Processing result with sentiment statistics
            
        Returns:
            Generated insights text
        """
        try:
            if not self.client:
                logger.warning("Ollama client not available, using fallback insights")
                return self._generate_fallback_insights(processing_result)
            
            # Prepare comprehensive prompt
            prompt = self._create_insights_prompt(processing_result)
            
            # Make API call for insights
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a business intelligence analyst specializing in sentiment analysis insights. Provide actionable, data-driven insights in bullet point format.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.3,
                    'num_predict': self.max_tokens  # Ollama uses num_predict instead of max_tokens
                }
            )
            
            logger.debug(f"Ollama insights response: {response}")
            
            if response and 'message' in response:
                insights = response['message']['content'].strip()
                logger.info("Generated insights using GPT OSS-12B model")
                return insights
            
            return self._generate_fallback_insights(processing_result)
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return self._generate_fallback_insights(processing_result)
    
    def translate_text(self, text: str, source_lang: str, target_lang: str = 'en') -> Dict:
        """
        Translate text using GPT OSS-12B model with caching
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code (default: English)
            
        Returns:
            Dictionary with translation results
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(f"{source_lang}_{target_lang}_{text}", "translation")
            if cache_key in self.translation_cache:
                logger.debug(f"Cache hit for translation: {text[:50]}...")
                return self.translation_cache[cache_key]
            
            if source_lang == target_lang:
                result = {
                    'original_text': text,
                    'translated_text': text,
                    'source_language': source_lang,
                    'was_translated': False
                }
                # Cache even the non-translated results to avoid repeated checks
                self._manage_cache_size(self.translation_cache)
                self.translation_cache[cache_key] = result
                return result
            
            if not self.client:
                return {
                    'original_text': text,
                    'translated_text': text,
                    'source_language': source_lang,
                    'was_translated': False,
                    'error': 'Translation service not available'
                }
            
            # Create translation prompt
            prompt = f"""Translate the following text from {source_lang} to {target_lang}. 
Provide ONLY the translation, no explanations or additional text.

Text to translate: "{text}"

Translation:"""
            
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.2,
                    'num_predict': max(100, min(len(text) * 3, 1000))  # More generous prediction length, minimum 100 tokens
                }
            )
            
            logger.debug(f"Ollama translation response: {response}")
            
            if response and 'message' in response:
                # Get translation from content or thinking field
                content = response['message'].get('content', '').strip()
                thinking = response['message'].get('thinking', '').strip()
                
                translated_text = content
                
                # If content is empty but thinking has translation, extract it
                if not translated_text and thinking:
                    # Extract the actual translation from thinking field
                    # Look for common translation patterns
                    lines = thinking.split('\n')
                    for line in lines:
                        line = line.strip()
                        # Look for quotes containing translation
                        if '"' in line and ('translation' not in line.lower() or 'translate' not in line.lower()):
                            # Extract text between quotes
                            import re
                            quoted_matches = re.findall(r'"([^"]+)"', line)
                            for match in quoted_matches:
                                # Skip if it's the original source text
                                if match != text and len(match) > 5:  # More lenient length check
                                    # Check if this looks like a translation
                                    if not any(word in match.lower() for word in ['translation', 'translate', 'português', 'english']):
                                        translated_text = match
                                        break
                        # Look for direct statements like "So translation: ..."
                        elif 'translation:' in line.lower():
                            parts = line.split('translation:', 1)
                            if len(parts) > 1:
                                candidate = parts[1].strip().strip('"').strip()
                                if candidate and candidate != text:
                                    translated_text = candidate
                                    break
                    
                    # If still no translation found, try to extract from end of thinking
                    if not translated_text:
                        # Look for the last meaningful sentence that could be a translation
                        sentences = thinking.split('.')
                        for sentence in reversed(sentences):
                            sentence = sentence.strip()
                            if (sentence and len(sentence) > 10 and 
                                'translation' not in sentence.lower() and
                                'portuguese' not in sentence.lower() and
                                sentence != text):
                                translated_text = sentence
                                break
                
                # Clean up translation
                if translated_text:
                    translated_text = self._clean_translation(translated_text)
                
                # If we still don't have a translation, use fallback
                if not translated_text:
                    logger.warning("No translation found in response, using original text")
                    translated_text = text
                    was_translated = False
                else:
                    was_translated = True
                
                result = {
                    'original_text': text,
                    'translated_text': translated_text,
                    'source_language': source_lang,
                    'was_translated': was_translated
                }
                
                # Cache the successful translation
                self._manage_cache_size(self.translation_cache)
                self.translation_cache[cache_key] = result
                return result
            
            # Fallback if translation fails
            result = {
                'original_text': text,
                'translated_text': text,
                'source_language': source_lang,
                'was_translated': False,
                'error': 'Translation failed'
            }
            self._manage_cache_size(self.translation_cache)
            self.translation_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            result = {
                'original_text': text,
                'translated_text': text,
                'source_language': source_lang,
                'was_translated': False,
                'error': str(e)
            }
            self._manage_cache_size(self.translation_cache)
            self.translation_cache[cache_key] = result
            return result
    
    def enhance_text_analysis(self, text: str) -> Dict:
        """
        Perform enhanced text analysis using GPT OSS-12B capabilities
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with enhanced analysis results
        """
        try:
            if not self.client:
                return {'error': 'Service not available'}
            
            prompt = f"""Perform a comprehensive analysis of the following text and provide insights in JSON format:

Text: "{text}"

Provide analysis including:
- sentiment (positive/negative/neutral)
- emotion (joy, anger, sadness, fear, surprise, disgust, trust, anticipation)
- key_themes (list of main topics)
- language_style (formal/informal/casual/professional)
- urgency_level (low/medium/high)
- customer_intent (complaint/praise/inquiry/suggestion)

Respond with ONLY a valid JSON object:"""
            
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.2,
                    'num_predict': 300  # Ollama uses num_predict instead of max_tokens
                }
            )
            
            logger.debug(f"Ollama enhanced analysis response: {response}")
            
            if response and 'message' in response:
                try:
                    analysis = json.loads(response['message']['content'].strip())
                    return analysis
                except json.JSONDecodeError:
                    return {'error': 'Failed to parse analysis'}
            
            return {'error': 'No response from model'}
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            return {'error': str(e)}
    
    def _create_insights_prompt(self, result: ProcessingResult) -> str:
        """Create comprehensive prompt for insights generation"""
        total = result.total_reviews
        positive_pct = (result.positive_count / total * 100) if total > 0 else 0
        negative_pct = (result.negative_count / total * 100) if total > 0 else 0
        neutral_pct = (result.neutral_count / total * 100) if total > 0 else 0
        
        dominant_sentiment = "positive" if result.positive_count >= result.negative_count and result.positive_count >= result.neutral_count else \
                           "negative" if result.negative_count >= result.neutral_count else "neutral"
        
        prompt = f"""Analyze these sentiment analysis results and provide strategic business insights:

**Dataset Overview:**
- Total Reviews: {total}
- Languages: {len(result.languages_detected)} ({', '.join(result.languages_detected)})
- Processing Time: {result.processing_time:.2f}s

**Sentiment Distribution:**
- Positive: {result.positive_count} reviews ({positive_pct:.1f}%)
- Negative: {result.negative_count} reviews ({negative_pct:.1f}%)
- Neutral: {result.neutral_count} reviews ({neutral_pct:.1f}%)
- Dominant Sentiment: {dominant_sentiment.title()}

Provide 4-6 bullet-point insights covering:
• Overall sentiment health assessment
• Customer satisfaction trends and patterns
• Risk areas and growth opportunities
• Multilingual market insights (if applicable)
• Specific actionable recommendations
• Benchmarking context and industry standards

Focus on actionable business intelligence. Be specific, data-driven, and strategic."""
        
        return prompt
    
    def _fallback_sentiment(self, text: str) -> Tuple[SentimentLabel, float]:
        """Fallback sentiment analysis when API is unavailable"""
        # Simple keyword-based fallback
        text_lower = text.lower()
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'worst', 'disappointing']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return SentimentLabel.POSITIVE, 0.7
        elif negative_count > positive_count:
            return SentimentLabel.NEGATIVE, 0.7
        else:
            return SentimentLabel.NEUTRAL, 0.6
    
    def _generate_fallback_insights(self, result: ProcessingResult) -> str:
        """Generate basic fallback insights"""
        total = result.total_reviews
        positive_pct = (result.positive_count / total * 100) if total > 0 else 0
        negative_pct = (result.negative_count / total * 100) if total > 0 else 0
        
        insights = f"""
• **Overall Assessment**: Analysis of {total} reviews shows {positive_pct:.1f}% positive sentiment
• **Customer Satisfaction**: {'High' if positive_pct > 60 else 'Moderate' if positive_pct > 40 else 'Low'} satisfaction levels based on sentiment distribution
• **Areas for Improvement**: {negative_pct:.1f}% negative feedback requires attention
• **Language Diversity**: Analysis covers {len(result.languages_detected)} languages: {', '.join(result.languages_detected)}
• **Recommendation**: {'Focus on scaling positive experiences' if positive_pct > 50 else 'Implement customer satisfaction improvement initiatives'}
        """
        return insights.strip()
    
    def _clean_translation(self, text: str) -> str:
        """Clean up translated text"""
        text = text.strip()
        
        # Remove quotes if the entire text is quoted
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        
        # Remove common translation artifacts
        if text.lower().startswith("translation:"):
            text = text[12:].strip()
        
        # Remove instruction fragments that sometimes appear at the end
        artifacts_to_remove = [
            '" Provide only',
            ' Provide only',
            ' Provide ONLY',
            '" ONLY',
            ' no explanations',
            ' no additional text',
            ' without any',
            ' Translation:'
        ]
        
        for artifact in artifacts_to_remove:
            if artifact in text:
                # Only remove if the artifact appears near the end (last 20% of text)
                artifact_pos = text.find(artifact)
                if artifact_pos > len(text) * 0.8:  # Only remove if near the end
                    text = text.split(artifact)[0].strip()
                    break  # Stop after first removal to avoid over-cleaning
        
        return text
    
    def batch_analyze_sentiment(self, texts: List[str]) -> List[Tuple[SentimentLabel, float]]:
        """
        Batch sentiment analysis for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of (SentimentLabel, confidence_score) tuples
        """
        if not texts:
            return []
        
        results = []
        cached_results = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text, "sentiment")
            if cache_key in self.sentiment_cache:
                cached_results.append((i, self.sentiment_cache[cache_key]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        logger.info(f"Batch sentiment analysis: {len(cached_results)} cached, {len(uncached_texts)} new")
        
        # Process uncached texts in batch
        if uncached_texts and self.client:
            batch_results = self._batch_sentiment_api_call(uncached_texts)
            
            # Store batch results in cache
            for j, (text, result) in enumerate(zip(uncached_texts, batch_results)):
                cache_key = self._get_cache_key(text, "sentiment")
                self._manage_cache_size(self.sentiment_cache)
                self.sentiment_cache[cache_key] = result
                cached_results.append((uncached_indices[j], result))
        else:
            # Fallback to individual processing for uncached texts
            for j, text in enumerate(uncached_texts):
                result = self._fallback_sentiment(text)
                cached_results.append((uncached_indices[j], result))
        
        # Sort results by original index and return
        cached_results.sort(key=lambda x: x[0])
        return [result for _, result in cached_results]
    
    def _batch_sentiment_api_call(self, texts: List[str]) -> List[Tuple[SentimentLabel, float]]:
        """
        Make batch API call for sentiment analysis
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        try:
            # Create batch prompt
            batch_prompt = "Analyze the sentiment of the following texts and respond with ONLY a JSON array:\n\n"
            for i, text in enumerate(texts):
                batch_prompt += f"{i+1}. \"{text[:500]}\"\n"  # Limit text length for batch processing
            
            batch_prompt += "\nRespond with a JSON array like: [{\"sentiment\": \"positive|negative|neutral\", \"confidence\": 0.85}, ...]"
            
            response = self.client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': batch_prompt}],
                options={'temperature': self.temperature, 'num_predict': len(texts) * 50}  # Scale response length
            )
            
            # Store response for potential JSON extraction
            self._last_response = response
            
            if response and 'message' in response:
                try:
                    content = response['message']['content'].strip()
                    
                    # Clean and extract JSON from response
                    json_content = self._extract_json_from_response(content)
                    if not json_content:
                        raise ValueError("No valid JSON found in response")
                        
                    results_json = json.loads(json_content)
                    
                    results = []
                    for result_data in results_json:
                        sentiment_str = result_data.get('sentiment', 'neutral').lower()
                        confidence = float(result_data.get('confidence', 0.7))
                        
                        if sentiment_str == 'positive':
                            sentiment = SentimentLabel.POSITIVE
                        elif sentiment_str == 'negative':
                            sentiment = SentimentLabel.NEGATIVE
                        else:
                            sentiment = SentimentLabel.NEUTRAL
                        
                        confidence = max(0.5, min(0.95, confidence))
                        results.append((sentiment, confidence))
                    
                    # Ensure we have results for all texts
                    while len(results) < len(texts):
                        results.append((SentimentLabel.NEUTRAL, 0.6))
                    
                    return results[:len(texts)]
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(f"Batch sentiment parsing failed: {e}, falling back to individual processing")
                    
        except Exception as e:
            logger.error(f"Batch sentiment API call failed: {e}")
        
        # Fallback: process individually
        results = []
        for text in texts:
            try:
                result = self.analyze_sentiment(text)
                results.append(result)
            except:
                results.append((SentimentLabel.NEUTRAL, 0.6))
        
        return results
    
    def _extract_json_from_response(self, content: str) -> str:
        """
        Extract valid JSON from potentially malformed API response
        
        Args:
            content: Raw response content
            
        Returns:
            Clean JSON string or empty string if not found
        """
        import re
        
        # Remove any markdown code block markers
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        
        # Try to find JSON array pattern
        json_patterns = [
            r'\[.*\]',  # Simple array pattern
            r'\[\s*\{.*\}\s*\]',  # Array with objects pattern
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                # Take the first (and hopefully only) match
                json_candidate = matches[0]
                
                # Try to validate it's proper JSON
                try:
                    json.loads(json_candidate)
                    return json_candidate
                except json.JSONDecodeError:
                    continue
        
        # If no valid JSON array found, try to extract from thinking field
        if hasattr(self, '_last_response') and self._last_response:
            thinking = self._last_response.get('message', {}).get('thinking', '')
            if thinking:
                for pattern in json_patterns:
                    matches = re.findall(pattern, thinking, re.DOTALL)
                    if matches:
                        try:
                            json.loads(matches[0])
                            return matches[0]
                        except json.JSONDecodeError:
                            continue
        
        # Last resort: try to build JSON from text analysis
        lines = content.split('\n')
        json_lines = []
        in_array = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('['):
                in_array = True
                json_lines = [line]
            elif in_array:
                json_lines.append(line)
                if line.endswith(']'):
                    break
        
        if json_lines:
            potential_json = '\n'.join(json_lines)
            try:
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
        
        logger.warning(f"Could not extract valid JSON from response: {content[:200]}...")
        return ""
    
    def get_service_stats(self) -> Dict:
        """Get service statistics"""
        return {
            "service": "Ollama GPT OSS-120B",
            "model": self.model,
            "host": self.host,
            "status": "active" if self.client else "unavailable",
            "capabilities": ["sentiment_analysis", "insights_generation", "translation", "text_analysis"],
            "cache_stats": {
                "sentiment_cache_size": len(self.sentiment_cache),
                "translation_cache_size": len(self.translation_cache),
                "max_cache_size": self.max_cache_size
            }
        }
