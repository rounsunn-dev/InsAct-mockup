import os
from dotenv import load_dotenv

print("🔍 Testing environment setup...")

# Load environment variables
load_dotenv()

# Check all env vars
print("Environment variables:")
for key in ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'OPENAI_API_KEY']:
    value = os.getenv(key)
    if value:
        if 'API_KEY' in key:
            print(f"  {key}: {value[:10]}...{value[-5:]} (hidden)")
        else:
            print(f"  {key}: {value}")
    else:
        print(f"  {key}: ❌ NOT FOUND")

# Test OpenAI import
try:
    from openai import OpenAI
    print("\n✅ OpenAI imported successfully!")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith('sk-'):
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
        
        # Test a simple API call
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'hello' if this API key works"}],
                max_tokens=10
            )
            print("✅ API key works! Response:", response.choices[0].message.content)
        except Exception as e:
            print(f"❌ API key test failed: {e}")
    else:
        print("❌ Invalid or missing OpenAI API key")
        
except ImportError as e:
    print(f"❌ Failed to import OpenAI: {e}")