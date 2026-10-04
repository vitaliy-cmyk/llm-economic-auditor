import json
import urllib.request
import os

# Работаем строго через LM Studio (порт 1234)
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

SYSTEM_JSON_PROMPT = """Вы — эксперт-разметчик экономических данных. Анализируйте предоставленный фрагмент отчета MD&A.
Оцените уровень следующих рисков для компании по шкале от 1 (риск отсутствует) до 5 (критическая угроза):
1. Interest_Rate_Risk (Процентный риск из-за высокой ставки ЦБ)
2. Currency_Risk (Валютный риск, курс рубля)
3. Labor_Shortage_Risk (Кадровый дефицит)
4. Supply_Chain_Risk (Проблемы с логистикой и оборудованием)

Вы обязаны вернуть ответ СТРОГО в формате JSON-объекта, без каких-либо вступлений, рассуждений и пояснений. Только чистый JSON.

Формат JSON на выходе:
{
  "Company": "Polyus",
  "Interest_Rate_Risk": 3,
  "Currency_Risk": 4,
  "Labor_Shortage_Risk": 2,
  "Supply_Chain_Risk": 3
}
"""

def get_risk_metrics_lm_studio(file_path, company_name):
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не найден в папке!")
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # УМНЫЙ ТРЮК: Ограничиваем текст первыми 15000 символов, 
    # чтобы гарантированно не перегрузить лимит контекста в LM Studio (избегаем ошибки 400)
    safe_content = content[:15000]
    
    print(f"⏳ Отправляем безопасный фрагмент {file_path} в LM Studio (Qwen 27b)...")
    
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": SYSTEM_JSON_PROMPT},
            {"role": "user", "content": f"ФРАГМЕНТ ОТЧЕТА {company_name}:\n{safe_content}"}
        ],
        "temperature": 0.1
    }
    
    data_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        LM_STUDIO_URL, 
        data=data_bytes, 
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            raw_text = res['choices'][0]['message']['content'].strip()
            
            # Очищаем от возможных markdown кавычек
            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                
            return json.loads(raw_text)
    except Exception as e:
        print(f"❌ Ошибка LM Studio при обработке {file_path}: {e}")
        return None

# =====================================================================
# СБОР ДАННЫХ И ФОРМИРОВАНИЕ МАТРИЦЫ
# =====================================================================

matrix_data = []

print("🤖 Запускаем разметку рисков через LM Studio и модель Qwen 27b...")
polyus_metrics = get_risk_metrics_lm_studio("polyus_mda.txt", "Polyus")
if polyus_metrics:
    print("✅ Полюс успешно размечен!")
    matrix_data.append(polyus_metrics)

print("\n🤖 Запускаем разметку рисков для СЕЛИГДАРА...")
seligdar_metrics = get_risk_metrics_lm_studio("seligdar_mda.txt", "Seligdar")
if seligdar_metrics:
    print("✅ Селигдар успешно размечен!")
    matrix_data.append(seligdar_metrics)

print("\n📊 Итоговая база данных рисков в формате JSON:")
print(json.dumps(matrix_data, indent=2, ensure_ascii=False))

with open("risk_matrix.json", "w", encoding="utf-8") as f:
    json.dump(matrix_data, f, indent=2, ensure_ascii=False)
print("\n💾 Файл risk_matrix.json сохранен на диск.")