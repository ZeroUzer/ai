import re
import json
from openai import OpenAI
from django.conf import settings

class HuggingFaceInference:
    def __init__(self):
        self.api_token = getattr(settings, 'HF_TOKEN', None)
        self.model = "Qwen/Qwen2.5-7B-Instruct"
        
        if self.api_token:
            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=self.api_token
            )
    
    def generate(self, prompt, temperature=0.7, max_tokens=500):
        if not self.api_token:
            return "Ошибка: не настроен HF_TOKEN"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            result = response.choices[0].message.content
            
            result = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f]+', '', result)
            result = re.sub(r'\s+', ' ', result).strip()
            
            return result
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def search_products(self, query, products_info):
        """Поиск товаров по запросу пользователя"""
        
        products_text = ""
        for p in products_info[:30]:
            products_text += f"- {p['name']} | {p['price']} руб. | {p['shop']} | ссылка: /shops/{p['shop_slug']}/product/{p['product_id']}/\n"
        
        prompt = f"""Ты - помощник по поиску товаров в интернет-магазинах.

Запрос пользователя: "{query}"

Доступные товары:
{products_text}

Найди товары, которые подходят под запрос пользователя.
Верни ответ в формате:
1. Сначала краткое вступление (1 предложение)
2. Затем список подходящих товаров с ценами и ссылками в формате /shops/название-магазина/product/id/
3. Если товаров нет, предложи альтернативу

Пример правильного ответа:
По вашему запросу найдены следующие товары:
1. Ноутбук ASUS - 45000 руб. - Магазин TechStore - /shops/techstore/product/1/
2. Ноутбук Acer - 35000 руб. - Магазин Electronics - /shops/electronics/product/5/

Ответ должен быть на русском языке, вежливым и полезным."""
        
        result = self.generate(prompt, temperature=0.7, max_tokens=500)
        
        if '/shops/' not in result:
            result += "\n\nПерейдите в магазин и посмотрите все товары."
        
        return result
    
    def generate_design_config(self, design_description=""):
        if not design_description:
            design_description = "современный, светлая тема, синие акценты"
        
        prompt = f"""Ты - дизайнер интерфейсов. Сгенерируй JSON-конфиг для оформления интернет-магазина.

Описание: {design_description}

Верни ТОЛЬКО валидный JSON:

{{
    "colors": {{
        "primary": "основной цвет hex",
        "primary_dark": "тёмный вариант hex",
        "secondary": "вторичный цвет hex",
        "background": "фон hex",
        "text": "цвет текста hex",
        "card_bg": "фон карточек hex",
        "accent": "акцентный цвет hex"
    }},
    "typography": {{
        "heading_font": "шрифт для заголовков",
        "body_font": "шрифт для текста"
    }},
    "layout": {{
        "card_radius": "скругление в px",
        "button_radius": "скругление в px",
        "shadow_intensity": "light/medium/strong",
        "spacing": "compact/comfortable/spacious"
    }},
    "effects": {{
        "gradient": true/false,
        "animation": true/false,
        "glassmorphism": true/false
    }}
}}

Пример премиум тёмного стиля:
{{
    "colors": {{
        "primary": "#D4AF37",
        "primary_dark": "#B8960C",
        "secondary": "#6c757d",
        "background": "#0a0a0a",
        "text": "#e0d5c1",
        "card_bg": "rgba(255,255,255,0.03)",
        "accent": "#FFD700"
    }},
    "typography": {{
        "heading_font": "Playfair Display",
        "body_font": "Inter"
    }},
    "layout": {{
        "card_radius": "16px",
        "button_radius": "12px",
        "shadow_intensity": "strong",
        "spacing": "comfortable"
    }},
    "effects": {{
        "gradient": true,
        "animation": true,
        "glassmorphism": true
    }}
}}"""
        
        result = self.generate(prompt, temperature=0.7, max_tokens=600)
        
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = result[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "colors": {
                "primary": "#4361ee",
                "primary_dark": "#3a56d4",
                "secondary": "#6c757d",
                "background": "#f8f9fa",
                "text": "#212529",
                "card_bg": "#ffffff",
                "accent": "#4361ee"
            },
            "typography": {
                "heading_font": "Inter",
                "body_font": "Inter"
            },
            "layout": {
                "card_radius": "12px",
                "button_radius": "8px",
                "shadow_intensity": "medium",
                "spacing": "comfortable"
            },
            "effects": {
                "gradient": True,
                "animation": True,
                "glassmorphism": False
            }
        }
    
    def generate_product_description(self, product_name, category_name=None, shop_name=None):
        prompt = f"Напиши привлекательное описание для товара '{product_name}' на русском языке. 2-3 предложения."
        
        if category_name:
            prompt = f"Напиши привлекательное описание для товара '{product_name}' в категории '{category_name}' на русском языке. 2-3 предложения."
        
        return self.generate(prompt, temperature=0.8, max_tokens=300)
    
    def generate_categories(self, shop_name, shop_description=""):
        prompt = f"""Магазин "{shop_name}". Предложи 5 категорий товаров на русском языке.
Категории на новой строке, без нумерации.
Пример:
Электроника
Одежда
Обувь
Аксессуары
Дом и сад"""
        
        response = self.generate(prompt, temperature=0.7, max_tokens=200)
        
        categories = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                line = line[1:].strip()
            if line and line[0].isdigit() and '.' in line[:3]:
                line = line.split('.', 1)[1].strip()
            if line and len(line) < 50:
                categories.append(line)
        
        if not categories:
            categories = ["Товары", "Новинки", "Акции", "Рекомендуемые", "Популярные"]
        
        return categories[:5]
    
    def generate_shop_description(self, shop_name, products_info=""):
        prompt = f"Напиши привлекательное описание для интернет-магазина '{shop_name}' на русском языке. 2-3 предложения."
        
        if products_info:
            prompt = f"Напиши привлекательное описание для интернет-магазина '{shop_name}', который продает {products_info} на русском языке. 2-3 предложения."
        
        result = self.generate(prompt, temperature=0.7, max_tokens=200)
        result = re.sub(r'Добро пожаловать.*?\n', '', result)
        result = result.strip()
        
        return result
    
    def chat_with_customer(self, question, products_info):
        if len(products_info) > 3000:
            products_info = products_info[:3000]
        
        prompt = f"""Ты - помощник в магазине.
Товары:
{products_info}

Вопрос: "{question}"

Ответь вежливо и полезно на русском языке."""
        
        return self.generate(prompt, temperature=0.7, max_tokens=300)