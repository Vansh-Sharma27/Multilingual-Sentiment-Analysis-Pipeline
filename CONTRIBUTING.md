# Contributing to Multilingual Sentiment Analysis Pipeline

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the Multilingual Sentiment Analysis Pipeline.

## 🚀 **Project Vision**

This project aims to provide a multilingual sentiment analysis solution with:
- Enhanced performance through caching and tokenization
- Support for 40+ languages with professional accuracy
- Modern web interface with comprehensive API integration
- Production-ready architecture with robust error handling

## 🛠️ **Development Setup**

### Prerequisites
- Python 3.8+
- Ollama API key
- Git

### Local Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/multilingual-sentiment-pipeline.git
   cd multilingual-sentiment-pipeline
   ```
3. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
6. Run tests:
   ```bash
   python -m pytest tests/ -v
   ```

## 📝 **Contribution Guidelines**

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include type hints where appropriate

### Testing Requirements
- All new features must include tests
- Existing tests must pass
- Maintain or improve test coverage
- Use meaningful test names and assertions

### Performance Standards
- New features should maintain reasonable processing times
- Leverage existing infrastructure (caching, tokenization)
- Consider multilingual implications for all text processing

## 🔧 **Types of Contributions**

### 1. **Language Support**
- Add support for new languages
- Improve language detection accuracy
- Enhance translation quality

### 2. **Performance Optimization**
- Improve processing speed
- Reduce memory usage
- Enhance caching strategies

### 3. **Feature Development**
- New analysis capabilities
- Enhanced API endpoints
- Frontend improvements

### 4. **Documentation**
- Code documentation
- API documentation
- User guides and tutorials

### 5. **Bug Fixes**
- Error handling improvements
- Edge case resolution
- Security enhancements

## 📋 **Pull Request Process**

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Thoroughly**
   ```bash
   python -m pytest tests/ -v
   python run.py  # Manual testing
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new language support for Vietnamese"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create pull request on GitHub
   - Use descriptive title and detailed description
   - Reference any related issues

## 🧪 **Testing Guidelines**

### Test Structure
- Unit tests for individual functions
- Integration tests for API endpoints
- Performance tests for optimization features

### Test Data
- Use existing test files in `test_files/`
- Create minimal test cases for specific scenarios
- Include multilingual test cases when relevant

### Performance Testing
- Measure processing time improvements
- Validate cache efficiency
- Test with various file sizes

## 📖 **Documentation Standards**

### Code Documentation
- Clear docstrings for all public functions
- Inline comments for complex logic
- Type hints for function parameters and returns

### API Documentation
- Update OpenAPI/Swagger specs if applicable
- Include request/response examples
- Document error conditions

### User Documentation
- Update README.md for new features
- Maintain FILE_FORMATS.md accuracy
- Include usage examples

## 🐛 **Bug Reporting**

### Before Reporting
- Check existing issues
- Test with latest version
- Gather relevant system information

### Bug Report Template
- **Description**: Clear problem description
- **Steps to Reproduce**: Detailed reproduction steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Sample Data**: Minimal failing example

## 🌟 **Feature Requests**

### Request Guidelines
- Search existing feature requests
- Provide clear use case and rationale
- Consider implementation complexity
- Include mockups or examples if applicable

## 📊 **Performance Benchmarking**

When contributing performance improvements:

1. **Baseline Measurements**
   - Document current performance metrics
   - Use consistent test data
   - Include processing time and memory usage

2. **Improvement Validation**
   - Demonstrate measurable improvements
   - Test across different dataset sizes
   - Validate multilingual performance

3. **Regression Testing**
   - Ensure accuracy is maintained
   - Verify all existing tests pass
   - Check edge cases aren't broken

## 🔐 **Security Considerations**

- Never commit API keys or sensitive data
- Validate all user inputs
- Follow secure coding practices
- Report security issues privately

## 💬 **Community Guidelines**

- Be respectful and constructive
- Help others learn and contribute
- Focus on technical merit
- Welcome newcomers and diverse perspectives

## 📞 **Getting Help**

- Check documentation first
- Search existing issues
- Ask questions in issue comments
- Provide context and examples when seeking help

## 🎯 **Contribution Recognition**

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation

Thank you for helping make this project better! 🙏
