from app.config import get_setting

def test_config():
    # Test getting an existing setting
    api_prefix = get_setting('API_V1_STR')
    print(f"API_V1_STR = {api_prefix}")
    
    # Test getting a non-existent setting with default
    test_setting = get_setting('NON_EXISTENT', 'default_value')
    print(f"NON_EXISTENT (with default) = {test_setting}")
    
    # Test getting OpenAI settings
    openai_key = get_setting('OPENAI_API_KEY')
    print(f"OPENAI_API_KEY exists: {bool(openai_key)}")
    
    # Print all settings (be careful not to expose sensitive values)
    print("\nAll available settings keys:")
    from app.config import _settings
    print(list(_settings.keys())) 