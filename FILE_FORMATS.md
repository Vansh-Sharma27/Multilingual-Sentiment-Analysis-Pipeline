# Supported File Formats for Sentiment Analysis

This document describes the supported file formats and their proper structure for the Multilingual Sentiment Analysis Pipeline.

## Overview

The application supports two file formats for batch sentiment analysis:
- **CSV** (Comma-Separated Values)
- **JSON** (JavaScript Object Notation)

All formats support multilingual content with automatic language detection and translation.

## CSV Format

### Structure Requirements
- Must have column headers in the first row
- Text content should be in columns with recognized names
- UTF-8 encoding recommended for multilingual content

### Recognized Column Names
The system automatically detects text content from columns named:
- `text` ✅ (Primary)
- `review` ✅ (Primary)
- `comment` ✅ (Primary)
- `feedback` ✅ (Primary)
- `content` ✅
- `message` ✅
- `description` ✅
- `summary` ✅
- `opinion` ✅

### Example Structure
```csv
text,rating,date,language
"This product is amazing! I love it so much.",5,2024-01-15,en
"La qualité est médiocre. Très déçu.",1,2024-01-16,fr
"Es ist okay, nichts Besonderes.",3,2024-01-17,de
"Excelente servicio al cliente.",5,2024-01-18,es
```

### Additional Features
- **Multiple text columns**: If multiple recognized columns exist, they will be combined
- **Metadata preservation**: Other columns (rating, date, etc.) are preserved as metadata
- **Language detection**: Automatic detection regardless of language column
- **Encoding support**: UTF-8, Latin-1, CP1252 encoding detection

### Best Practices
- Use UTF-8 encoding for international characters
- Quote text fields that contain commas or newlines
- Keep text length reasonable (under 10,000 characters per entry)
- Include context columns (rating, date) for better insights

## JSON Format

### Structure Requirements
- Valid JSON syntax
- UTF-8 encoding
- Text content in recognized field names

### Supported Structures

#### Array of Objects (Recommended)
```json
[
  {
    "id": 1,
    "text": "This product is amazing!",
    "rating": 5,
    "date": "2024-01-15",
    "language": "en"
  },
  {
    "id": 2,
    "text": "La qualité est médiocre.",
    "rating": 1,
    "date": "2024-01-16",
    "language": "fr"
  }
]
```

#### Object with Array Property
```json
{
  "reviews": [
    {
      "text": "Great product!",
      "sentiment": "positive"
    }
  ],
  "metadata": {
    "source": "customer_feedback",
    "date": "2024-01-15"
  }
}
```

#### Nested Structure
```json
{
  "data": {
    "customer_feedback": [
      {
        "review": "Amazing quality!",
        "details": {
          "rating": 5,
          "verified": true
        }
      }
    ]
  }
}
```

### Recognized Field Names
The system searches for text content in fields named:
- `text` ✅ (Primary)
- `review` ✅ (Primary)  
- `content` ✅ (Primary)
- `message` ✅ (Primary)
- `comment` ✅
- `feedback` ✅
- `description` ✅
- `body` ✅
- `summary` ✅

### Processing Features
- **Recursive scanning**: Searches through nested objects
- **Array detection**: Handles arrays at any level
- **Text extraction**: Prioritizes recognized field names
- **Metadata preservation**: Maintains structure context

## File Processing Features

### Chunking Process
- **Automatic chunking**: Large texts are split into manageable pieces
- **Overlap strategy**: 50-token overlap between chunks for context preservation
- **Sentence boundaries**: Respects sentence structure when possible
- **Configurable size**: Default 512 tokens per chunk (adjustable)

### Language Detection
- **Automatic detection**: Uses advanced language detection algorithms
- **Confidence scoring**: Provides confidence levels for detected languages
- **Fallback methods**: Multiple detection strategies for accuracy
- **Multilingual support**: Handles 40+ languages

### Translation Process
- **Smart translation**: Only translates non-English content
- **Quality preservation**: Maintains sentiment context during translation
- **Batch processing**: Efficient handling of multiple languages
- **Error handling**: Graceful fallback for unsupported languages

### Supported Languages (40+ Total)

**✅ Actively Tested in Current Dataset:**
- **Asian**: Hindi (हिंदी), Telugu (తెలుగు), Tamil (தமிழ்), Chinese Simplified (中文)
- **European**: English, German (Deutsch), Russian (Русский), Dutch (Nederlands), French, Spanish, Italian
- **Middle Eastern**: Arabic (العربية)  
- **Indian Regional**: Marathi (मराठी)

**🌍 Additional Supported Languages:**
- **Asian**: Japanese, Korean, Chinese Traditional, Vietnamese, Thai, Indonesian, Malay
- **European**: Portuguese, Polish, Swedish, Danish, Norwegian, Finnish
- **Middle Eastern**: Hebrew, Turkish, Persian
- **Others**: Czech, Hungarian, Romanian, Bulgarian, Croatian, Serbian, Slovak, Lithuanian, Latvian, Estonian

## File Size Limits

| Format | Maximum Size | Maximum Items | Recommended Size |
|--------|-------------|---------------|------------------|
| CSV    | 2 MB        | 500 rows      | 1-2 MB          |
| JSON   | 2 MB        | 500 objects   | 1-2 MB          |

## Error Handling

### Common Issues and Solutions

#### CSV Format Issues
- **Invalid encoding**: Use UTF-8 encoding
- **Missing headers**: Ensure first row contains column names
- **No text columns**: Include at least one recognized text column
- **Malformed CSV**: Check for unescaped quotes or commas

#### JSON Format Issues
- **Invalid syntax**: Validate JSON structure before upload
- **No text fields**: Include recognized text field names
- **Encoding issues**: Save as UTF-8 with BOM if needed
- **File too large**: Split large files into smaller chunks



## Performance Optimization

### Best Practices for File Processing
1. **Keep files under 2MB** for optimal processing
2. **Structure data properly** for efficient analysis
3. **Include metadata** in CSV/JSON for richer analysis
4. **Pre-validate** file structure before upload
5. **Monitor processing time** and adjust file size accordingly

### Processing Considerations
- **File size**: Smaller files process more efficiently
- **Text length**: Shorter individual texts process more quickly
- **Language diversity**: More languages require more translation time
- **Chunking enabled**: May increase processing time but improves accuracy

## Example Files

Comprehensive test datasets are provided in the `test_files/` directory:

| File | Size | Records | Languages | Purpose |
|------|------|---------|-----------|---------|
| `multilingual_10_languages_1000_reviews.csv` | 1.6MB | 600 lines | **12+ languages** | Large-scale performance testing |
| `multilingual_reviews_dataset.csv` | 12KB | 131 lines | **8+ languages** | Medium dataset validation |
| `review-analysis-2025-08-23.csv` | 24KB | 212 lines | Mixed | Analysis output example |

### **Languages Represented in Test Data:**
- **Asian**: Hindi (हिंदी), Telugu (తెలుగు), Tamil (தமிழ்), Chinese Simplified (中文), Japanese
- **European**: English, German (Deutsch), Russian (Русский), Dutch (Nederlands), French, Spanish, Italian  
- **Middle Eastern**: Arabic (العربية)
- **Indian Regional**: Marathi (मराठी), and other regional languages

### **Actual CSV Structure (Input Format):**
```csv
text,rating,date,language
"This product is amazing! Excellent quality and fast delivery.",5,2024-01-15,en
"इस होटल का अनुभव बहुत शानदार रहा। कर्मचारी बहुत सहयोगी थे।",4,2024-02-23,hi
"Terrible experience. Staff was rude and food arrived cold.",1,2024-01-03,en
"这家酒店的服务非常周到，员工都很热情。房间干净整洁。",5,2024-02-16,zh
```

### **Analysis Output Format (Generated):**
```csv
ID,Text,Sentiment,Sentiment Score,Rating,Date,Topics,Key Phrases
"review-1","Amazing product quality","positive",0.9,5,"2024-01-15","product,quality","amazing,excellent"
"review-2","Terrible service experience","negative",0.8,1,"2024-01-03","service,experience","terrible,rude"
```

These files demonstrate comprehensive multilingual coverage and provide realistic testing scenarios for the sentiment analysis pipeline.

## API Integration

### Upload Endpoint
```
POST /api/upload/file/analyze
Content-Type: multipart/form-data

Parameters:
- file: File upload (required)
- chunk_large_texts: boolean (optional, default: true)
- translate: boolean (optional, default: true)  
- generate_insights: boolean (optional, default: true)
```

### Response Format
```json
{
  "results": [
    {
      "text": "Analyzed text",
      "original_text": "Original if translated",
      "translated_text": "English translation", 
      "sentiment": "Positive|Negative|Neutral",
      "confidence": 0.85,
      "language": "Detected language",
      "was_translated": true|false,
      "translation_info": {
        "source_language": "fr",
        "target_language": "en",
        "was_translated": true
      }
    }
  ],
  "summary": {
    "positive": 5,
    "negative": 2, 
    "neutral": 3
  },
  "insights": [
    "AI-generated insight 1",
    "AI-generated insight 2"
  ],
  "file_info": {
    "filename": "uploaded_file.csv",
    "format": "csv",
    "total_texts": 10,
    "languages_detected": ["English", "French", "Spanish"]
  }
}
```

## Troubleshooting

For specific format issues, check the application logs or use the `/api/test` endpoint to verify connectivity before uploading files.
