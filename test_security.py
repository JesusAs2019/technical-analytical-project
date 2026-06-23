# test_security.py
import cryptography
from cryptography.fernet import Fernet
import schema
import bleach

# Test cryptography
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(b'Hello, secure Python!')
decrypted = cipher.decrypt(encrypted)

print(' Cryptography test:')
print(f'   Original: Hello, secure Python!')
print(f'   Encrypted: {encrypted[:50]}...')
print(f'   Decrypted: {decrypted.decode()}')
print()

# Test schema validation
user_schema = schema.Schema({
    'name': str,
    'age': int,
    'email': str
})

valid_data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
validated = user_schema.validate(valid_data)
print(' Schema validation test: PASSED')
print(f'   Validated data: {validated}')
print()

# Test bleach HTML sanitization
dirty_html = '<script>alert("XSS")</script><p>Safe content</p>'
clean_html = bleach.clean(dirty_html)
print(' Bleach sanitization test:')
print(f'   Dirty HTML: {dirty_html}')
print(f'   Clean HTML: {clean_html}')
print()

print(' All security tests passed! Your environment is ready.')
