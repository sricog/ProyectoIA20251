#!/usr/bin/env python3
"""
Optimized Voice Sales App - Concise & Fast Responses
Integrates real product database with faster, shorter responses
"""

from flask import Flask, render_template, request, jsonify, session, send_file
import uuid
import logging
import os
import tempfile
import io
import asyncio
from threading import Thread
import time
import re
import base64
from io import BytesIO

# Import our LiveKit voice assistant
from sales_assistant import SalesAssistant

# Import our product database
from product_database import get_product_database

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'voice-sales-secret-key-change-this')

# Store assistant instances per session
assistants = {}
conversation_history = {}

# Initialize product database
product_db = None

def init_product_database():
    """Initialize product database"""
    global product_db
    try:
        product_db = get_product_database()
        logger.info(f"✅ Product database initialized with {len(product_db.df)} products")
    except Exception as e:
        logger.error(f"❌ Error initializing product database: {e}")

def get_assistant_for_session():
    """Get or create assistant for current session"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    session_id = session['session_id']

    if session_id not in assistants:
        assistants[session_id] = SalesAssistant()
        conversation_history[session_id] = []

    return assistants[session_id], conversation_history[session_id]

def add_to_conversation(session_id, role, message):
    """Add message to conversation history"""
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    conversation_history[session_id].append({
        'role': role,
        'content': message,
        'timestamp': time.time()
    })

    # Keep only last 20 messages to prevent context bloat
    if len(conversation_history[session_id]) > 20:
        conversation_history[session_id] = conversation_history[session_id][-20:]

def build_optimized_prompt(user_message, history, products, search_description=""):
    """Build concise prompt with essential context only"""

    # Recent conversation (last 4 messages max)
    recent_context = ""
    if history:
        recent_messages = history[-4:]
        for msg in recent_messages:
            role = "Usuario" if msg['role'] == 'user' else "Asistente"
            recent_context += f"{role}: {msg['content'][:100]}...\n"

    # Top 6 most relevant products (increased from 3)
    products_text = ""
    if products:
        # Check if this is an alternative suggestion
        if "No tenemos" in search_description:
            products_text = f"{search_description}\n"
        else:
            products_text = "PRODUCTOS RELEVANTES:\n"

        for i, p in enumerate(products[:6], 1):  # Increased from 3 to 6
            price = f"${p['price']:.0f}"
            if p['on_sale'] and p['original_price']:
                price = f"${p['price']:.0f} (¡oferta!)"
            products_text += f"{i}. {p['name']} - {p['brand']} - {price}\n"

    # Concise prompt
    prompt = f"""
CONTEXTO RECIENTE:
{recent_context}

{products_text}

USUARIO: {user_message}

RESPUESTA (máximo 2-3 oraciones, específica con precios, promociona productos relevantes):"""

    return prompt

async def generate_optimized_response(assistant, prompt):
    """Generate fast, concise response"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Faster model
            messages=[
                {
                    "role": "system",
                    "content": """Eres un asistente de ventas conciso y efectivo.

REGLAS ESTRICTAS:
- Máximo 3-4 oraciones por respuesta
- Siempre menciona precios específicos
- Promociona 2-4 productos por respuesta (más variedad)
- Usa lenguaje directo y persuasivo
- Resalta ofertas cuando existan
- No repitas información ya mencionada
- Ordena productos por relevancia y precio

EJEMPLOS:
"Te ofrezco iPhone 13 Pro a $1,284, iPhone 13 a $7,833 (¡oferta!) y iPhone 12 Pro Max a $9,580. ¿Cuál prefieres?"
"En electrónicos tengo: iPhone 13 Pro $1,284, iPhone SE $5,015 (oferta) y iPhone 13 mini $4,991. Todos con garantía Apple."
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=150,  # Increased from 100 to accommodate more products
            temperature=0.7,
            presence_penalty=0.6,  # Avoid repetition
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "¿En qué producto específico estás interesado? Tengo excelentes ofertas."

@app.route('/')
def index():
    """Main page with voice interface"""
    return render_template('voice_index.html')

@app.route('/api/greet', methods=['POST'])
def greet():
    """Fast greeting with featured products"""
    try:
        assistant, history = get_assistant_for_session()
        session_id = session['session_id']

        # Get 6 featured products (increased from 3)
        featured_products = product_db.get_featured_products(max_results=6)

        # Quick greeting
        greeting = f"¡Hola! Soy tu asistente de ventas con {len(product_db.df)} productos disponibles. ¿Buscas algo específico? Tengo ofertas en {featured_products[0]['name']} a ${featured_products[0]['price']:.0f}."

        add_to_conversation(session_id, 'assistant', greeting)

        return jsonify({
            'success': True,
            'greeting': greeting,
            'message': greeting,
            'mentioned_products': featured_products,
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Error in greet: {e}")
        return jsonify({'error': 'Error initializing assistant'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle text chat with optimized responses"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        assistant, history = get_assistant_for_session()
        session_id = session['session_id']

        # Add user message
        add_to_conversation(session_id, 'user', user_message)

        # Enhanced product search (increased from 5 to 8)
        products, search_description = product_db.smart_search(user_message, max_results=8)

        # Build optimized prompt
        context_prompt = build_optimized_prompt(user_message, history, products, search_description)

        # Generate fast response
        response = asyncio.run(generate_optimized_response(assistant, context_prompt))

        # Add response to history
        add_to_conversation(session_id, 'assistant', response)

        return jsonify({
            'success': True,
            'response': response,
            'mentioned_products': products[:6],  # Show max 6 products (increased from 3)
            'conversation': history[-6:],  # Show last 6 messages only
        })

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': 'Error processing message'}), 500

@app.route('/api/voice/chat', methods=['POST'])
def voice_chat():
    """Handle voice chat with fast responses"""
    try:
        session_id = request.form.get('session_id')
        voice = request.form.get('voice', 'alloy')
        audio_file = request.files.get('audio')

        if not audio_file:
            return jsonify({'error': 'No audio file provided'}), 400

        # Get conversation history
        history = conversation_history.get(session_id, [])
        assistant = assistants.get(session_id)

        # Save audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            # Convert to text
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            with open(temp_path, 'rb') as audio_data:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data
                )

            user_input = transcript.text
            logger.info(f"Voice input: {user_input}")

            # Add to conversation
            add_to_conversation(session_id, 'user', user_input)

            # Enhanced product search
            products, search_description = product_db.smart_search(user_input, max_results=8)

            # Generate optimized response
            context_prompt = build_optimized_prompt(user_input, history, products, search_description)
            response_text = asyncio.run(generate_optimized_response(assistant, context_prompt))

            # Add to conversation
            add_to_conversation(session_id, 'assistant', response_text)

            # Generate audio response
            audio_response = client.audio.speech.create(
                model="tts-1",  # Faster TTS model
                voice=voice,
                input=response_text,
                speed=1.1  # Slightly faster speech
            )

            # Convert to base64
            audio_data = base64.b64encode(audio_response.content).decode()

            return jsonify({
                'success': True,
                'user_message': user_input,
                'response_text': response_text,
                'audio_data': audio_data,
                'mentioned_products': products[:6],  # Show max 6 products (increased from 3)
                'processing_time': 'optimized'
            })

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error in voice chat: {e}")
        return jsonify({'error': 'Error processing voice message'}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get product recommendations"""
    try:
        category = request.args.get('category', '')
        search_term = request.args.get('search', '')
        max_results = int(request.args.get('max_results', 5))

        if search_term:
            products, _ = product_db.smart_search(search_term, max_results=max_results)
        elif category:
            products = product_db.get_by_category(category, max_results=max_results)
        else:
            products = product_db.get_featured_products(max_results=max_results)

        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })

    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({'error': 'Error retrieving products'}), 500

if __name__ == '__main__':
    # Initialize database
    init_product_database()

    if not product_db:
        print("❌ Failed to initialize product database")
        exit(1)

    print("🚀 OPTIMIZED VOICE SALES APP")
    print("=" * 40)
    print(f"✅ {len(product_db.df)} products loaded")
    print(f"✅ {len(product_db.categories)} categories available")
    print(f"✅ Optimized for fast, concise responses")
    print("\n🎯 Optimizations:")
    print("- 🚀 GPT-4o-mini for faster responses")
    print("- ⚡ max_tokens=100 for conciseness")
    print("- 🎯 Top 3 products maximum per response")
    print("- 📝 2-3 sentences maximum")
    print("- 💨 TTS-1 for faster audio generation")
    print("\n🌐 Open http://localhost:5000")

    app.run(debug=True, host='0.0.0.0', port=5000)