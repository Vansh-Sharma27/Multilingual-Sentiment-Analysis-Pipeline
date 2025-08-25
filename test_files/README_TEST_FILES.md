# Test Files for Multilingual Sentiment Analysis Pipeline

## Overview
This directory contains comprehensive test files designed to validate the pagination functionality and performance optimizations of the multilingual sentiment analysis pipeline.

## Test Files

### 1. `multilingual_10_languages_reviews.csv` ⭐ **Large Dataset**
- **Format**: CSV with headers (text, rating, date, language)
- **Size**: 600 lines
- **Languages**: 12+ languages including Hindi, Telugu, Tamil, Chinese, Russian, Arabic, German, Dutch, English, Marathi
- **Purpose**: Large-scale testing and multilingual validation
- **Special Features**: Contains very long text entries for chunking tests

### 2. `multilingual_reviews_dataset.csv` ✅ **Medium Dataset**
- **Format**: CSV with headers (text, rating, date, language) 
- **Size**: 131 lines
- **Languages**: 8+ languages including Russian, Chinese, German, Dutch, Arabic, English, Spanish
- **Purpose**: Medium-scale testing and language detection validation

### 3. `review-analysis-2025-08-23.csv` 📊 **Analysis Output Example**
- **Format**: CSV with headers (ID, Text, Sentiment, Sentiment Score, Rating, Date, Topics, Key Phrases)
- **Size**: 212 lines
- **Purpose**: Example of analysis output format (not input data)
- **Note**: This appears to be generated output from a previous analysis run

## Test Scenarios

### Pagination Testing
- **Large file (600 lines)** = 60 pages (10 per page) for comprehensive pagination testing
- **Medium file (131 lines)** = 14 pages for moderate pagination testing
- **Navigation**: Previous/Next buttons across multiple pages
- **Page indicators**: Should show proper pagination for large datasets
- **Results range**: Should accurately display ranges for all dataset sizes

### Performance Testing
- **Processing time**: Monitor processing time for different file sizes
- **Memory usage**: Check memory usage with pagination
- **API calls**: Verify API call efficiency
- **Cache efficiency**: Monitor cache performance

### Multilingual Testing
- **Language detection**: Should work for all 7 languages
- **Translation**: Non-English reviews should be translated
- **Sentiment analysis**: Should work across all languages
- **Tokenization**: Should optimize for each language

## Language Distribution (Actual Test Data)

### `multilingual_10_languages_reviews.csv` (600 lines)
| Language | Sample Content | Script Type |
|----------|----------------|-------------|
| Hindi (hi) | इस होटल का अनुभव बहुत शानदार रहा | Devanagari |
| Telugu (te) | ఈ రెస్టారెంట్ డిలిషియస్ ఫుడ్ అందిస్తుంది | Telugu Script |
| Tamil (ta) | இந்த உணவகம் மிகவும் சிறந்த சுவைகளை வழங்குகிறது | Tamil Script |
| Chinese (zh) | 这家酒店的服务非常周到，员工都很热情 | Chinese Characters |
| English (en) | This place exceeded my expectations | Latin Script |
| Marathi (mr) | ह्या हॉटेलमध्ये सेवा उत्तम आहे | Devanagari |
| Russian (ru) | В этом отеле был отличный сервис | Cyrillic Script |

### `multilingual_reviews_dataset.csv` (131 lines)
| Language | Sample Content | Coverage |
|----------|----------------|----------|
| Russian (ru) | Исключительное качество! Обязательно вернусь | High |
| Chinese (zh) | 卓越的品质！我肯定会再来的 | Medium |
| German (de) | Durchschnittliches Restaurant. Nichts Besonderes | Medium |
| Dutch (nl) | Vreselijke ervaring. Het personeel was onbeleefd | Medium |
| Arabic (ar) | تجربة فظيعة. الموظفون كانوا وقحين | Medium |
| English (en) | Terrible experience. The staff was rude | High |
| Spanish (es) | Restaurante promedio. Nada especial | Medium |

## Expected Results

### Pagination Behavior
- **Page 1**: Reviews 1-10
- **Page 2**: Reviews 11-20  
- **Page 3**: Reviews 21-25
- **Navigation**: Should be smooth and responsive
- **Filters**: Should work with pagination

### Performance Metrics
- **Processing Time**: Target 3-5 seconds (vs 20+ seconds original)
- **Memory Usage**: 40-60% reduction
- **API Calls**: 5-10x fewer calls
- **Cache Hits**: 80% efficiency

### Sentiment Distribution
- **Positive**: Various positive reviews across languages
- **Negative**: Various negative reviews across languages
- **Neutral**: Various neutral reviews across languages

## Usage Instructions

1. **Large-scale Testing**: Use `multilingual_10_languages_reviews.csv` for performance and scalability testing
2. **Medium-scale Testing**: Use `multilingual_reviews_dataset.csv` for standard functionality validation
3. **Output Analysis**: Examine `review-analysis-2025-08-23.csv` to understand analysis output format
4. **Pagination Testing**: Navigate through multiple pages with large datasets (60+ pages)
5. **Multilingual Testing**: Verify language detection works across 12+ different languages and scripts
6. **Performance Monitoring**: Monitor processing times for different file sizes
7. **Export Testing**: Export AI insights in markdown format from comprehensive analyses

## Validation Checklist

- [ ] File upload works for both CSV and JSON
- [ ] Pagination shows 3 pages for 25 reviews
- [ ] Navigation buttons work correctly
- [ ] Page indicators show correct information
- [ ] Results range displays accurately
- [ ] Filters work with pagination
- [ ] Export functionality works
- [ ] Processing time is optimized
- [ ] All languages are detected correctly
- [ ] Translations work for non-English reviews
- [ ] Sentiment analysis is accurate across languages

## Performance Considerations

| Metric | Description | Notes |
|--------|-------------|-------|
| Processing Time | Varies by file size and content | Monitor for optimization opportunities |
| Memory Usage | Depends on file size and processing | Check memory usage during large file processing |
| API Calls | Batched for efficiency | Verify API call patterns |
| Cache Efficiency | LRU cache implementation | Monitor cache hit rates |
| UI Responsiveness | Real-time updates | Ensure smooth user experience |

## Notes
- All reviews are realistic product feedback from various e-commerce scenarios
- Reviews contain 4-6 lines of text for comprehensive testing
- Multiple languages test the multilingual capabilities
- Mixed sentiment distribution tests filtering functionality
- Large dataset size tests pagination functionality
