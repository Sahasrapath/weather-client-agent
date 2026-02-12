# Weather Agent Contributing Guide

## How to Contribute

### Setting Up Development Environment

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dev dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8 mypy
   ```

### Code Style

- Use PEP 8 style guide
- Format with Black: `black src/`
- Lint with Flake8: `flake8 src/`
- Type hints required for all functions

### Testing

- Write tests for new features
- Run tests: `pytest tests/ -v`
- Maintain 80%+ code coverage

### Documentation

- Update README.md for new features
- Add docstrings to all functions
- Include usage examples

### Pull Request Process

1. Create feature branch: `git checkout -b feature/description`
2. Make changes and commit with clear messages
3. Add tests for new functionality
4. Update documentation
5. Run all checks: `black`, `flake8`, `mypy`, `pytest`
6. Submit pull request with description

## Architecture

### MCP Client Layer
- Handles communication with MCP server
- Manages process lifecycle
- Parses JSON-RPC messages

### Weather Agent Layer
- Implements business logic
- Data validation and transformation
- Error handling and retries

### Configuration Layer
- Environment-based settings
- Feature flags
- Logging configuration

## Adding New Features

### Example: Adding a New Weather Tool

1. **In config/config.py**, add feature flag:
   ```python
   FEATURES = {
       "enable_new_feature": True
   }
   ```

2. **In weather_agent.py**, add method:
   ```python
   def get_new_feature(self, location: str) -> Optional[Dict]:
       # Implementation
       return self.mcp_client.call_tool("new_tool", {...})
   ```

3. **In tests/test_weather_agent.py**, add test:
   ```python
   def test_new_feature():
       # Test implementation
   ```

## Performance Optimization

- Implement caching for repeated queries
- Use async/await for concurrent requests
- Batch multiple location queries
- Monitor API rate limits

## Security Considerations

- Never commit API keys
- Use environment variables for secrets
- Validate all user inputs
- Sanitize error messages in logs
