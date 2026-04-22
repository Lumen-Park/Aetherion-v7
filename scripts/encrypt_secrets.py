from utils.secrets import SecretsManager
import os

# Set your master password here
os.environ["AETHERION_MASTER_KEY"] = "your-strong-master-password"

# Encrypt your actual secrets
print("SMTP_PASSWORD=" + SecretsManager.encrypt("your-actual-smtp-password"))
print("ALPHA_VANTAGE_KEY=" + SecretsManager.encrypt("your-actual-api-key"))
