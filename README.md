# 🛍️ Asistente de Ventas por Voz

Un asistente de ventas inteligente con capacidades de voz que combina inteligencia artificial avanzada con una base de datos de productos para ofrecer recomendaciones personalizadas en tiempo real.

## 🎯 Características Principales

### 🎤 Capacidades de Voz
- **Speech-to-Text** con Whisper de OpenAI
- **Text-to-Speech** con ElevenLabs (fallback a OpenAI TTS)
- **Detección de Actividad de Voz** con Silero VAD
- **Conversación Natural** en español

### 🧠 Inteligencia Artificial
- **GPT-4o** para conversaciones complejas
- **GPT-4o-mini** para respuestas optimizadas y rápidas
- **Contexto conversacional** con historial de mensajes
- **Recomendaciones inteligentes** basadas en productos reales

### 🚀 Optimizaciones
- **Respuestas concisas** (2-3 oraciones máximo)
- **Búsqueda inteligente** de productos
- **Hasta 6 productos** por recomendación
- **Tiempo de respuesta optimizado**
- **Interfaz web moderna**

## 🏗️ Estructura del Proyecto

```
ProyectoIA20251/
├── sales_assistant.py          # Clase principal del asistente de voz
├── voice_sales_app_optimized.py # Aplicación web Flask
├── product_database.py         # Base de datos de productos
├── requirements.txt            # Dependencias del proyecto
├── data/                       # Datos de productos
├── templates/                  # Plantillas HTML
│   └── voice_index.html        # Interfaz web
├── .gitignore                  # Archivos ignorados por Git
└── README.md                   # Este archivo
```

## 📋 Requisitos

### Dependencias Python
Las dependencias están listadas en `requirements.txt`:
```
flask
livekit-agents
livekit-plugins-openai
livekit-plugins-elevenlabs
livekit-plugins-silero
openai
pandas
numpy
```

### APIs y Claves
- **OpenAI API Key** (obligatorio)
- **ElevenLabs API Key** (opcional, fallback a OpenAI TTS)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/sricog/ProyectoIA20251.git
cd ProyectoIA20251
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "tu-api-key-de-openai"
$env:ELEVENLABS_API_KEY = "tu-api-key-de-elevenlabs"  # Opcional

# Linux/Mac
export OPENAI_API_KEY="tu-api-key-de-openai"
export ELEVENLABS_API_KEY="tu-api-key-de-elevenlabs"  # Opcional
```

## 🎮 Uso

### Modo Standalone (Solo Asistente)
```bash
python sales_assistant.py
```

### Aplicación Web Completa
```bash
python voice_sales_app_optimized.py
```

Luego abre tu navegador en: `http://localhost:5000`

## 📡 API Endpoints

### `POST /api/greet`
Inicializa la conversación con un saludo personalizado
- **Response**: Saludo con productos destacados

### `POST /api/chat`
Procesa mensajes de texto
- **Body**: `{"message": "tu mensaje"}`
- **Response**: Respuesta del asistente con productos recomendados

### `POST /api/voice/chat`
Procesa audio de voz y responde con audio
- **Form Data**:
  - `audio`: archivo de audio
  - `voice`: tipo de voz (alloy, echo, fable, etc.)
  - `session_id`: ID de sesión
- **Response**: Transcripción, respuesta de texto y audio en base64

### `GET /api/products`
Obtiene productos por categoría o búsqueda
- **Query Params**:
  - `category`: categoría de productos
  - `search`: término de búsqueda
  - `max_results`: número máximo de resultados

## 🎯 Personalidad del Asistente

El asistente está diseñado con las siguientes características:

- **Amigable y profesional** en todas las interacciones
- **Experto en productos** electrónicos y de consumo
- **Conversacional** con respuestas naturales en español
- **Enfocado en ventas** con menciones de precios y ofertas
- **Conciso** pero informativo

## ⚙️ Configuración Avanzada

### Personalizar la Personalidad
Edita las `instructions` en `sales_assistant.py`:

```python
instructions="""
Tu personalidad personalizada aquí...
"""
```

### Ajustar Optimizaciones
En `voice_sales_app_optimized.py`:

```python
# Cambiar número de productos mostrados
products[:6]  # Modifica este número

# Ajustar longitud de respuesta
max_tokens=150  # Modifica para respuestas más largas/cortas

# Velocidad de speech
speed=1.1  # Ajusta velocidad del TTS
```

## 🔧 Configuración de Voz

### Voces Disponibles (OpenAI TTS)
- `alloy` - Voz balanceada
- `echo` - Voz masculina
- `fable` - Voz femenina suave
- `onyx` - Voz masculina profunda
- `nova` - Voz femenina enérgica
- `shimmer` - Voz femenina cálida

### Configurar ElevenLabs
Para mejor calidad de voz, configura ElevenLabs:
```bash
$env:ELEVENLABS_API_KEY = "tu-api-key"
```

## 🐛 Troubleshooting

### Error: "No se encontró la API key de OpenAI"
```bash
$env:OPENAI_API_KEY = "tu-api-key-aqui"
```

### Error al inicializar ElevenLabs
El sistema automáticamente usa OpenAI TTS como fallback.

### Problemas con archivos de audio
Asegúrate de que el navegador soporte grabación de audio y que tengas permisos de micrófono.

### Base de datos de productos no encontrada
El archivo `product_database.py` ya está incluido en el repositorio y debería funcionar automáticamente.

## 📊 Métricas de Rendimiento

- **Tiempo de respuesta de texto**: ~1-2 segundos
- **Tiempo de procesamiento de voz**: ~3-5 segundos
- **Productos por recomendación**: Hasta 6
- **Contexto conversacional**: Últimos 20 mensajes
- **Longitud de respuesta**: 2-3 oraciones optimizadas

## 🤝 Contribuir

1. Fork el proyecto desde [GitHub](https://github.com/sricog/ProyectoIA20251)
2. Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo `LICENSE` para detalles.

## 🙏 Reconocimientos

- **OpenAI** por GPT-4o y Whisper
- **ElevenLabs** por TTS de alta calidad
- **LiveKit** por la infraestructura de voz en tiempo real
- **Silero** por la detección de actividad de voz

---

## 🚀 ¡Empieza Ahora!

```bash
# Clonar el repositorio
git clone https://github.com/sricog/ProyectoIA20251.git
cd ProyectoIA20251

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
$env:OPENAI_API_KEY = "tu-api-key"

# Ejecutar la aplicación
python voice_sales_app_optimized.py

# Abrir navegador en http://localhost:5000
```

**¡Tu asistente de ventas por voz está listo! 🎉**

## 🔗 Enlaces

- **Repositorio**: [https://github.com/sricog/ProyectoIA20251](https://github.com/sricog/ProyectoIA20251)
- **Documentación OpenAI**: [https://platform.openai.com/docs](https://platform.openai.com/docs)
- **ElevenLabs API**: [https://elevenlabs.io/docs](https://elevenlabs.io/docs)
- **LiveKit Agents**: [https://docs.livekit.io/agents](https://docs.livekit.io/agents)