from google import genai
import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("API_KEY_GEMINI")
        if not api_key:
            raise ValueError("API_KEY_GEMINI environment variable not set")

        self.client = genai.Client(api_key=api_key)
        
        # Historial de conversación por sesión
        self.conversation_histories = {}

    def generate_response(self, prompt: str) -> str:
        """Genera respuesta simple sin contexto espacial (legacy)"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "parts": [
                        {"text": "You are a helpful visual assistant, you need to respond to the user's voice command accordingly in your language."},
                        {"text": prompt}
                    ]
                }
            ]
        )

        return response.text if response else ""

    def generate_visual_assistant_response(
        self,
        user_command: str,
        detected_objects: List[Dict],
        current_location: str,
        target_room: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        session_id: str = "default"
    ) -> Dict:
        """
        Genera respuesta como asistente visual con contexto espacial completo
        usando few-shot prompting
        """
        try:
            # Construir prompt con few-shot learning
            prompt = self._build_visual_assistant_prompt(
                user_command=user_command,
                detected_objects=detected_objects,
                current_location=current_location,
                target_room=target_room,
                conversation_history=conversation_history
            )
            
            # Generar respuesta con Gemini
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "parts": [
                            {"text": "Eres un asistente visual inteligente para personas con discapacidad visual. Respondes SIEMPRE en formato JSON válido, usando español. Eres claro, directo y empático."},
                            {"text": prompt}
                        ]
                    }
                ],
                config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": 1024,
                }
            )
            
            response_text = response.text if response else "{}"
            
            # Intentar parsear como JSON
            try:
                # Limpiar markdown si existe
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.replace("```", "").strip()
                
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error: {str(e)}")
                print(f"Raw response: {response_text[:200]}...")
                
                # Si no es JSON válido, crear respuesta estructurada
                result = {
                    "response_text": response_text,
                    "action": self._infer_action(user_command),
                    "priority": "medium",
                    "should_speak_immediately": True
                }
            
            # Agregar target_room si se detectó
            if not result.get('target_room'):
                result['target_room'] = self._extract_target_room(user_command)
            
            # Actualizar historial
            if session_id not in self.conversation_histories:
                self.conversation_histories[session_id] = []
            
            self.conversation_histories[session_id].append({
                "speaker": "User",
                "text": user_command
            })
            self.conversation_histories[session_id].append({
                "speaker": "Assistant",
                "text": result.get('response_text', '')
            })
            
            # Mantener solo últimos 10 mensajes
            self.conversation_histories[session_id] = self.conversation_histories[session_id][-10:]
            
            return result
            
        except Exception as e:
            print(f"❌ Error in generate_visual_assistant_response: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "response_text": "Lo siento, tuve un problema procesando tu comando.",
                "action": "inform",
                "priority": "low",
                "should_speak_immediately": True
            }

    def generate_proactive_alert(
        self,
        detected_object: Dict,
        priority: str = "medium"
    ) -> Dict:
        """
        Genera alerta proactiva breve para un objeto detectado
        """
        try:
            label = detected_object.get('label', 'objeto')
            distance = detected_object.get('distance', 0)
            position = detected_object.get('position', 'al frente')
            
            prompt = f"""Genera una alerta MUY BREVE (máximo 8 palabras) para este objeto detectado:

Objeto: {label}
Distancia: {distance:.1f} metros
Posición: {position}
Nivel de urgencia: {priority}

EJEMPLOS de alertas:
- Si distancia < 1m: "¡Cuidado! Silla a medio metro"
- Si distancia 1-2m: "Atención: mesa a 1.5 metros adelante"  
- Si distancia > 2m: "Mesa detectada a 2.3 metros"

Reglas:
- Máximo 8 palabras
- Directo y claro
- Sin explicaciones adicionales
- Solo el texto de la alerta

Tu alerta:"""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "parts": [
                            {"text": "Genera alertas muy breves y directas. Máximo 8 palabras."},
                            {"text": prompt}
                        ]
                    }
                ],
                config={
                    "temperature": 0.5,
                    "max_output_tokens": 50,
                }
            )
            
            alert_text = response.text.strip() if response else f"Atención: {label} a {distance:.1f} metros"
            
            # Remover comillas si las agregó
            alert_text = alert_text.replace('"', '').replace("'", "")
            
            return {
                "alert_text": alert_text,
                "object": detected_object,
                "priority": priority,
                "should_speak_immediately": True
            }
            
        except Exception as e:
            print(f"❌ Error generating alert: {str(e)}")
            # Fallback a alerta simple
            return {
                "alert_text": f"Atención: {detected_object.get('label', 'objeto')} a {detected_object.get('distance', 0):.1f} metros",
                "object": detected_object,
                "priority": priority,
                "should_speak_immediately": True
            }

    def generate_navigation_instruction(
        self,
        current_location: str,
        target_room: str,
        nearby_objects: List[Dict]
    ) -> Dict:
        """
        Genera UNA instrucción de navegación paso a paso
        """
        try:
            # Construir descripción de objetos
            objects_desc = self._format_objects_description(nearby_objects)
            
            prompt = f"""Genera UNA instrucción de navegación clara y específica.

CONTEXTO:
- Ubicación actual: {self._format_location(current_location)}
- Destino: {self._format_location(target_room)}
- Objetos cercanos:
{objects_desc}

IMPORTANTE:
- Da SOLO el PRIMER paso necesario para avanzar hacia el destino
- Sé específico con dirección (adelante, izquierda, derecha) y distancia
- Menciona obstáculos a evitar si hay alguno < 2m
- Máximo 2-3 oraciones

Responde SOLO con un JSON válido en este formato exacto (sin markdown):
{{
  "action": "walk_forward",
  "description": "Camina recto por 2 metros, rodea la mesa por tu izquierda",
  "distance": 2.0,
  "targetRoom": "{target_room}",
  "obstacles": [],
  "priority": "high"
}}

Acciones válidas: walk_forward, turn_left, turn_right, stop
Prioridades válidas: high, medium, low

IMPORTANTE: Responde SOLO el JSON, sin texto adicional ni markdown.

Tu respuesta:"""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "parts": [
                            {"text": "Eres un asistente de navegación. Respondes SOLO con JSON válido, sin markdown."},
                            {"text": prompt}
                        ]
                    }
                ],
                config={
                    "temperature": 0.6,
                    "max_output_tokens": 300,
                }
            )
            
            response_text = response.text if response else "{}"
            
            # Limpiar markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.replace("```", "")
            
            instruction = json.loads(response_text)
            
            return instruction
            
        except Exception as e:
            print(f"❌ Error generating navigation: {str(e)}")
            # Fallback
            return {
                "action": "walk_forward",
                "description": f"Camina hacia {self._format_location(target_room)}",
                "distance": 2.0,
                "targetRoom": target_room,
                "obstacles": [],
                "priority": "medium"
            }

    def _build_visual_assistant_prompt(
        self,
        user_command: str,
        detected_objects: List[Dict],
        current_location: str,
        target_room: Optional[str],
        conversation_history: Optional[List[Dict]]
    ) -> str:
        """Construye el prompt con few-shot learning"""
        
        # Contexto espacial
        spatial_context = self._build_spatial_context(
            detected_objects, 
            current_location, 
            target_room
        )
        
        # Historial
        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            history_text = "\nHISTORIAL RECIENTE:\n"
            for msg in conversation_history[-5:]:  # Últimos 5 mensajes
                speaker = msg.get('speaker', 'User')
                text = msg.get('text', '')
                history_text += f"{speaker}: {text}\n"
        
        # Few-shot examples
        few_shot_examples = """
EJEMPLOS DE CÓMO RESPONDER (aprende de estos):

Ejemplo 1 - Navegación:
Usuario: "Llévame a la cocina"
Contexto: Ubicación: Sala. Objetos: Mesa 2.1m adelante, Silla 1.5m izquierda, Puerta 3.2m adelante-derecha
Respuesta:
{
  "response_text": "Entendido, te guiaré a la cocina. Camina recto por 2 metros, rodea la mesa por tu izquierda. La puerta de la cocina está a tu derecha.",
  "action": "navigate",
  "navigation_step": {
    "direction": "forward",
    "distance": 2.0,
    "description": "Camina recto 2 metros, rodea la mesa por la izquierda"
  },
  "priority": "high",
  "should_speak_immediately": true,
  "target_room": "kitchen"
}

Ejemplo 2 - Consulta:
Usuario: "¿Qué hay cerca?"
Contexto: Silla 0.8m adelante, Mesa 1.2m derecha, Sofá 2.5m atrás
Respuesta:
{
  "response_text": "Detecto una silla muy cerca, a menos de un metro frente a ti. Ten cuidado. También hay una mesa a tu derecha a 1.2 metros.",
  "action": "inform",
  "priority": "high",
  "should_speak_immediately": true
}

Ejemplo 3 - Detener:
Usuario: "Detente"
Respuesta:
{
  "response_text": "De acuerdo, deteniendo la navegación. Estás en el pasillo.",
  "action": "stop",
  "priority": "medium",
  "should_speak_immediately": true,
  "target_room": null
}

Ejemplo 4 - Ubicar objeto:
Usuario: "¿Dónde está la puerta?"
Contexto: Puerta 2.8m adelante-izquierda
Respuesta:
{
  "response_text": "La puerta está a 2.8 metros hacia tu frente, ligeramente a la izquierda. Gira unos 15 grados a tu izquierda y camina recto.",
  "action": "inform",
  "priority": "medium",
  "should_speak_immediately": true
}
"""
        
        # Prompt completo
        prompt = f"""Eres un asistente visual para personas con discapacidad visual. Tu misión es ayudarles a navegar de forma segura.

{few_shot_examples}

CONTEXTO ACTUAL:
{spatial_context}
{history_text}

INSTRUCCIONES CRÍTICAS:
1. Responde SIEMPRE con un JSON válido (sin markdown, sin comillas triples)
2. Menciona distancias en metros con un decimal (ej: "1.5 metros")
3. Usa direcciones claras: adelante, atrás, izquierda, derecha
4. Alerta sobre obstáculos críticos (< 1 metro) inmediatamente
5. Para navegación, da UN paso a la vez
6. Tono amigable pero directo
7. Si detectas objeto peligroso (< 1.5m), avisa proactivamente

COMANDO DEL USUARIO: "{user_command}"

Responde SOLO con un JSON válido (sin ```json ni ```):
{{
  "response_text": "Tu respuesta en lenguaje natural",
  "action": "navigate|alert|inform|stop",
  "navigation_step": {{
    "direction": "forward|left|right|backward",
    "distance": 2.5,
    "description": "Descripción del paso"
  }},
  "priority": "high|medium|low",
  "should_speak_immediately": true,
  "target_room": "kitchen|bedroom|bathroom|living_room|null"
}}

Tu respuesta JSON:"""
        
        return prompt

    def _build_spatial_context(
        self, 
        objects: List[Dict], 
        location: str, 
        target: Optional[str]
    ) -> str:
        """Construye descripción del contexto espacial"""
        
        context = f"Ubicación actual: {self._format_location(location)}\n"
        
        if target:
            context += f"Destino objetivo: {self._format_location(target)}\n"
        
        if not objects or len(objects) == 0:
            context += "\nNo hay objetos detectados en el campo visual inmediato."
            return context
        
        # Clasificar objetos por distancia
        critical = [o for o in objects if o.get('distance', 999) < 1.0]
        warning = [o for o in objects if 1.0 <= o.get('distance', 999) < 2.0]
        info = [o for o in objects if o.get('distance', 999) >= 2.0]
        
        context += "\nOBJETOS DETECTADOS:\n"
        
        if critical:
            context += "\n[CRÍTICO - Muy cerca, < 1m]:\n"
            for obj in critical:
                context += f"  - {obj.get('label', 'objeto')}: {obj.get('distance', 0):.1f}m, {obj.get('position', 'al frente')}\n"
        
        if warning:
            context += "\n[PRECAUCIÓN - Cerca, 1-2m]:\n"
            for obj in warning:
                context += f"  - {obj.get('label', 'objeto')}: {obj.get('distance', 0):.1f}m, {obj.get('position', 'al frente')}\n"
        
        if info:
            context += "\n[INFORMACIÓN - Distancia media, > 2m]:\n"
            for obj in info[:5]:  # Limitar a 5
                context += f"  - {obj.get('label', 'objeto')}: {obj.get('distance', 0):.1f}m, {obj.get('position', 'al frente')}\n"
        
        return context

    def _format_objects_description(self, objects: List[Dict]) -> str:
        """Formatea lista de objetos para prompt"""
        if not objects:
            return "  Ninguno"
        
        desc = ""
        for obj in objects[:5]:
            label = obj.get('label', 'objeto')
            distance = obj.get('distance', 0)
            position = obj.get('position', 'adelante')
            desc += f"  - {label}: {distance:.1f}m {position}\n"
        
        return desc.strip()

    def _format_location(self, location: str) -> str:
        """Traduce nombres de ubicaciones"""
        translations = {
            'kitchen': 'Cocina',
            'bedroom': 'Dormitorio',
            'bathroom': 'Baño',
            'living_room': 'Sala',
            'hallway': 'Pasillo',
            'dining_room': 'Comedor',
            'unknown': 'Ubicación desconocida',
        }
        return translations.get(location, location)

    def _extract_target_room(self, command: str) -> Optional[str]:
        """Extrae habitación objetivo del comando"""
        command_lower = command.lower()
        
        room_keywords = {
            'cocina': 'kitchen',
            'kitchen': 'kitchen',
            'dormitorio': 'bedroom',
            'bedroom': 'bedroom',
            'cuarto': 'bedroom',
            'habitación': 'bedroom',
            'baño': 'bathroom',
            'bathroom': 'bathroom',
            'sala': 'living_room',
            'living': 'living_room',
            'salón': 'living_room',
            'pasillo': 'hallway',
            'hallway': 'hallway',
            'comedor': 'dining_room',
            'dining': 'dining_room'
        }
        
        for keyword, room in room_keywords.items():
            if keyword in command_lower:
                return room
        
        return None

    def _infer_action(self, command: str) -> str:
        """Infiere la acción del comando"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['lleva', 'ir a', 'guía', 'navega', 'vamos', 'llévame']):
            return 'navigate'
        elif any(word in command_lower for word in ['detén', 'para', 'stop', 'alto', 'detente']):
            return 'stop'
        elif any(word in command_lower for word in ['cuidado', 'peligro', 'alerta']):
            return 'alert'
        else:
            return 'inform'

    def clear_history(self, session_id: str = "default"):
        """Limpia el historial de una sesión"""
        if session_id in self.conversation_histories:
            del self.conversation_histories[session_id]
    
    def get_history(self, session_id: str = "default") -> List[Dict]:
        """Obtiene el historial de una sesión"""
        return self.conversation_histories.get(session_id, [])