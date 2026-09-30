import json
import urllib.request
import time
import os

# --- ИСПРАВЛЕННЫЕ АДРЕСА ПОД СТАНДАРТЫ ДВИЖКОВ ---
OLLAMA_URL = "http://localhost:11434/api/chat" # Нативный эндпоинт Ollama
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions" # Эндпоинт LM Studio

MODEL_GENERATOR = "qwen3.5:9b"   # Имя вашей модели в Ollama
MODEL_AUDITOR = "local-model" # LM Studio автоматически подставит запущенную Qwen 27b

def send_to_ollama(system_prompt, user_content):
    """Специальная функция для Ollama (формат /api/chat)"""
    payload = {
        "model": MODEL_GENERATOR,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "options": {"temperature": 0.7}
    }
    data_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data_bytes, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['message']['content'] # Специфичный для Ollama разбор
    except Exception as e:
        print(f"Ошибка Ollama: {e}")
        return None

def send_to_lm_studio(system_prompt, user_content):
    """Специальная функция для LM Studio с исправленным извлечением JSON"""
    payload = {
        "model": MODEL_AUDITOR,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1
    }
    data_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(LM_STUDIO_URL, data=data_bytes, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            # ИСПРАВЛЕНО: Добавлен индекс [0] для корректного чтения списка choices
            return res['choices'][0]['message']['content']
    except Exception as e:
        print(f"Ошибка LM Studio: {e}")
        return None

# =====================================================================
# ЗАПУСК СЦЕНАРИЯ
# =====================================================================

ECONOMIC_TASK = """
Проанализируй ситуацию: Золотодобывающая компания 'Альфа' имеет рублевый долг 10 млрд рублей 
по плавающей ставке (КС ЦБ + 3%). Центробанк резко повышает ключевую ставку с 16% до 21%. 
При этом мировые цены на золото вырастают на 15%. Как эти два фактора одновременно повлияют 
на чистую прибыль компании и её ликвидность в краткосрочном периоде?
"""

print("🚀 ШАГ 1: Запускаем Qwen 3.5-9b в Ollama для базового анализа...")
sys_prompt_gen = "Ты - корпоративный финансовый аналитик. Дай подробный экономический ответ на вопрос пользователя."

start_time = time.time()
generated_reply = send_to_ollama(sys_prompt_gen, ECONOMIC_TASK)

if generated_reply:
    print(f"⏱️ Ollama ответила за {round(time.time() - start_time, 1)} сек.")
    print("\n--- ОТВЕТ ИЗ OLLAMA (НА ПРОВЕРКУ): ---")
    print(generated_reply)
    print("-" * 50)
else:
    print("❌ Шаг 1 сорван: Ollama не вернула текст. Проверьте имя модели в Ollama (команда 'ollama list').")
    # Если Ollama не сработала, подставим заглушку, чтобы протестировать тяжелую модель в LM Studio
    generated_reply = "Рост цен на золото полностью компенсирует рост процентных расходов по долгу."

print("\n⏳ Пауза 2 секунды...")
time.sleep(2)

print("\n🧠 ШАГ 2: Передаем ответ в тяжелую Qwen 3.8-27b (LM Studio) для поиска ошибок...")
sys_prompt_audit = """
Вы — старший аудитор и AI-тренер. Ваша задача — проверить предоставленный экономический ответ на прочность.
Найдите в тексте логические или экономические ошибки и поверхностные выводы.
Выведите свой жесткий вердикт на РУССКОМ языке: перечислите пункты, где модель сглупила, и напишите свой эталонный, глубокий вариант вывода.
"""

start_time = time.time()
auditor_verdict = send_to_lm_studio(sys_prompt_audit, f"ОТВЕТ НА ПРОВЕРКУ:\n{generated_reply}")

print(f"⏱️ LM Studio (27b) ответила за {round(time.time() - start_time, 1)} сек.")
print("\n==================================================================")
print("🎯 ВЕРДИКТ ГЛАВНОГО АУДИТОРА (Qwen 3.8-27b):")
print("==================================================================")
print(auditor_verdict if auditor_verdict else "Ошибка извлечения текста.")
