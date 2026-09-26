from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0,str(PROJECT_ROOT))
from app.core.config import get_settings



settings = get_settings()

print(settings.app_name)
print(settings.environment)
print(settings.aws_region)
print(settings.bedrock_model_id)
print(settings.openai_model)
print(settings.openai_api_key)