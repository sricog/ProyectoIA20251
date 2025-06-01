#!/usr/bin/env python3
"""
Sales Voice Assistant - Exactly like your notebook format
"""

import os
from livekit.agents import Agent
from livekit.plugins import openai, elevenlabs, silero

class SalesAssistant(Agent):
    def __init__(self) -> None:
        # Use the API key from environment
        api_key = os.getenv('OPENAI_API_KEY')

        llm = openai.LLM(model="gpt-4o", api_key=api_key)
        stt = openai.STT()

        try:
            tts = elevenlabs.TTS()
        except:
            tts = openai.TTS()

        silero_vad = silero.VAD.load()

        super().__init__(
            instructions="""
                Eres un asistente de ventas inteligente especializado en productos electrónicos y de consumo.

                PERSONALIDAD:
                - Amigable, entusiasta y profesional
                - Experto en productos de tecnología y consumo
                - Ayudas a encontrar el producto perfecto para cada cliente
                - Conversacional y natural en español

                INSTRUCCIONES:
                1. Saluda de manera amigable y pregunta cómo puedes ayudar
                2. Escucha atentamente las necesidades del cliente
                3. Recomienda productos específicos con precios
                4. Ofrece alternativas si el cliente busca algo diferente
                5. Mantén respuestas concisas pero informativas
                6. Siempre incluye precios cuando recomiendes productos
                7. Pregunta si necesitan más información o tienen otras dudas

            """,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=silero_vad,
        )

# Test the assistant
if __name__ == "__main__":
    print("🛍️ AGENTE DE VENTAS POR VOZ")
    print("=" * 40)

    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: No se encontró la API key de OpenAI")
        print("Por favor configura tu API key:")
        print("$env:OPENAI_API_KEY = 'tu-api-key-aqui'")
        exit(1)

    print("✅ API Key configurada")
    print("🎤 Agente de voz creado exitosamente")
    print("\n🎯 Características del agente:")
    print("- 🗣️  Speech-to-Text con Whisper")
    print("- 🧠  GPT-4o para inteligencia conversacional")
    print("- 🔊  Text-to-Speech de alta calidad")
    print("- 👂  Detección de actividad de voz")
    print("- 🛍️  Especializado en ventas")

    print("\n💡 Para usar en producción, integra este agente con:")
    print("- LiveKit room o WebRTC connection")
    print("- Interfaz web o aplicación móvil")
    print("- Sistema de gestión de inventario")

    # Create instance to test
    try:
        assistant = SalesAssistant()
        print("\n🎉 ¡Agente inicializado correctamente!")
    except Exception as e:
        print(f"\n❌ Error al inicializar: {e}")