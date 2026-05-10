# from django.apps import AppConfig


# class AiCoreConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'ai_core'

#     def ready(self):
#         """Pre-warm the LLM provider at startup to eliminate first-query cold start."""
#         import threading

#         def _warmup():
#             import time
#             start_time = time.time()
#             try:
#                 # 1. Start the OpenAI connection
#                 from .services.llm.provider import get_provider, get_chat_model
#                 provider = get_provider()
#                 provider.client.models.list()
                
#                 # 2. Pre-import and cache heavy LangChain/AI modules 
#                 # This puts them in 'sys.modules' cache so they are ready instantly later.
#                 get_chat_model()
#                 elapsed = time.time() - start_time
#                 print(f"\n✅ AI Models pre-loaded in background ({elapsed:.1f}s). Chat is now ready and fast!")
#             except Exception:
#                 pass

#         # Run in background thread to not block 'runserver' startup/system checks
#         threading.Thread(target=_warmup, daemon=True).start()
