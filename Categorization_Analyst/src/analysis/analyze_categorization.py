"""
Script para analizar las categorizaciones y calcular el score de confianza.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from typing import Dict, List, Tuple
import logging
import os
import sys
import json
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

# Agregar el directorio raíz al path de Python
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.data_preparation.categories_config import CATEGORIES, KEYWORDS, TYPE_KEYWORDS

# Crear directorios necesarios
def create_directories():
    """Crea los directorios necesarios para el análisis."""
    directories = [
        'Categorization_Analyst/data/logs',
        'Categorization_Analyst/data/summaries',
        'Categorization_Analyst/data/output',
        'Categorization_Analyst/data/learning'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Configuración de logging
def setup_logging():
    """Configura el sistema de logging."""
    log_file = 'Categorization_Analyst/data/logs/analysis.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

class CategorizationAnalyzer:
    def __init__(self):
        self.categories = CATEGORIES
        self.keywords = KEYWORDS
        self.type_keywords = TYPE_KEYWORDS
        
        # Cargar pesos aprendidos si existen
        self.weights_file = 'Categorization_Analyst/data/learning/category_weights.json'
        self.learned_weights = self._load_weights()
        
        # Compilar expresiones regulares
        self.text_cleaner = re.compile(r'[^a-z\s]')
        self.space_cleaner = re.compile(r'\s+')
        
        # Crear tabla de traducción para acentos
        self.accents_table = str.maketrans('áéíóú', 'aeiou')
        
        # Inicializar NLTK
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        # Cargar stopwords en español
        self.stopwords = set(stopwords.words('spanish'))
        
        # Inicializar stemmer
        self.stemmer = SnowballStemmer('spanish')
        
        # Patrones de contexto mejorados y específicos por categoría
        self.context_patterns = {
            'Website': {
                'Lentitud': r'((?:muy\s+)?(?:lento|lenta|tarda|demora|pega|se pega|lentitud|tardar|esperar|espera|esperando|carga|cargando)(?:\s+mucho)?)',
                'Confuso': r'((?:muy\s+)?(?:confuso|confusa|confusion|dificil de entender|confundir|entorpecer|complicado|no entiendo|no se entiende|poco claro|dificil|complejo))',
                'Error': r'((?:hay un |tiene |da |sale |aparece |muestra )?(?:error|fallo|problema|incorrecto|falla|no funciona|no sirve|no carga|no responde|se cae|crashea|bug|error 404|pantalla azul))',
                'Login': r'((?:el |la |el proceso de |la página de )?(?:login|entrar|acceso|autenticar|autenticación|cliente banco|tarjeta|contraseña|usuario|cuenta|iniciar sesión|registro)(?:\s+(?:no funciona|falla|error|problema))?)',
                'Experiencia': r'((?:mala |pésima |horrible |terrible )?(?:experiencia|molesto|molesta|entorpecer|confundir|cargado|publicidad|interfaz|diseño|usabilidad|navegación|proceso)(?:\s+(?:complicado|difícil|malo|pésimo))?)'
            },
            'Proceso_Pago': {
                'Rechazo': r'((?:me |se |el pago |la tarjeta |el banco )?(?:rechazo|rechazado|rechazan|rechazar|no acepta|no pasa|no procesa|no procesa el pago|tarjeta rechazada|declina|declined))',
                'Error': r'((?:error|fallo|problema|incorrecto|falla|no funciona|no sirve|no carga|no responde|se cae|pago fallido|transacción fallida)(?:\s+(?:al pagar|en el pago|durante el pago|con el pago))?)',
                'Proceso': r'((?:el |la |el proceso de |la forma de )?(?:pago|compra|transacción|cargo|cobro)(?:\s+(?:es complicado|es difícil|no funciona|falla|tiene problemas))?)'
            },
            'Precios': {
                'Cambia': r'((?:el |los |el precio |los precios )?(?:cambia|aumenta|aumentan|varia|varian|diferente|distinto|otro precio|precio diferente|sube|suben|incrementa|incrementan)(?:\s+(?:mucho|constantemente|siempre))?)',
                'Alto': r'((?:muy |demasiado |extremadamente )?(?:alto|caro|costoso|elevado|muy caro|excesivo|demasiado|mucho dinero|precio alto|precios altos|tarifas altas))',
                'Tarifa': r'((?:la |las |el cobro de |el cargo por )?(?:tarifa|excesivo|irracional|abusivo|aprovechar|monopolio|impuesto|cargo|cargos adicionales|costos extra|cargos ocultos))'
            },
            'Aeropuerto': {
                'Ubicación': r'((?:el |la |en el |en la )?(?:aeropuerto|terminal|pista|vuelo|avion|aeronave|aerolinea|aeropuertos|sala de espera|puerta de embarque))',
                'Servicios': r'((?:mal |pésimo |horrible |terrible )?(?:servicio|servicios|atencion|personal|empleados|staff|asistencia|ayuda|counter|mostrador))'
            },
            'Equipaje': {
                'Daño': r'((?:mi |el |la |mi equipaje |mi maleta )?(?:daño|dañado|roto|rompio|maltrato|maltratado|destrozado|destruido|golpeado|deteriorado))',
                'Pérdida': r'((?:mi |el |la |mi equipaje |mi maleta )?(?:perdida|perdido|extraviado|desaparecido|no llego|no aparece|no encuentro|perdieron|extraviaron))',
                'Exceso': r'((?:cobro |cargo |precio |tarifa )?(?:por exceso|exceso de peso|sobrepeso|equipaje extra|maleta adicional|cargo adicional))'
            },
            'Seats': {
                'Comodidad': r'((?:muy |poco |nada |super )?(?:asiento|asientos|silla|sillas|comodo|comoda|incomodo|incomoda|espacio|espacios|apretado|estrecho))',
                'Selección': r'((?:no pude |no puedo |imposible |difícil )?(?:seleccion|elegir|elegido|elegida|escoger|escogido|escogida|asignado|asignada|reservar asiento|cambiar asiento))'
            },
            'Disponibilidad_Vuelo': {
                'Horarios': r'((?:los |el |la |los horarios |el horario )?(?:hora|horario|tiempo|disponible|disponibilidad|vuelo|vuelos|salida|llegada)(?:\s+(?:no hay|no existen|limitados|pocos))?)',
                'Destinos': r'((?:los |el |la |los destinos |el destino )?(?:destino|ruta|lugar|ciudad|vuelo directo|conexión|escala)(?:\s+(?:no hay|no existen|limitados|pocos))?)',
                'Opciones': r'((?:pocas |limitadas |sin )?(?:opcion|opciones|alternativa|alternativas|vuelo|vuelos|ruta|rutas)(?:\s+(?:disponibles|existentes))?)'
            }
        }
        
        # Patrones de negación mejorados
        self.negation_patterns = [
            r'no\s+',
            r'nunca\s+',
            r'jamás\s+',
            r'ningún\s+',
            r'ninguna\s+',
            r'ningunos\s+',
            r'ningunas\s+',
            r'ni\s+',
            r'tampoco\s+',
            r'sin\s+',
            r'nada\s+de\s+'
        ]
        
        # Compilar patrones de negación
        self.negation_regex = re.compile('|'.join(self.negation_patterns), re.IGNORECASE)
        
        # Pesos base por categoría
        self.category_weights = {
            'Website': {'keyword': 0.5, 'context': 0.3, 'type': 0.2},
            'Proceso_Pago': {'keyword': 0.4, 'context': 0.4, 'type': 0.2},
            'Precios': {'keyword': 0.6, 'context': 0.3, 'type': 0.1},
            'Aeropuerto': {'keyword': 0.3, 'context': 0.5, 'type': 0.2},
            'Equipaje': {'keyword': 0.4, 'context': 0.4, 'type': 0.2},
            'Seats': {'keyword': 0.3, 'context': 0.5, 'type': 0.2},
            'Disponibilidad_Vuelo': {'keyword': 0.4, 'context': 0.4, 'type': 0.2},
            'Discount_Club': {'keyword': 0.5, 'context': 0.3, 'type': 0.2},
            'Promociones': {'keyword': 0.5, 'context': 0.3, 'type': 0.2},
            'Datos_Pasajero': {'keyword': 0.4, 'context': 0.4, 'type': 0.2},
            'Cambios_Devoluciones': {'keyword': 0.4, 'context': 0.4, 'type': 0.2},
            'Otros': {'keyword': 0.4, 'context': 0.4, 'type': 0.2}
        }
        
        # Patrones de contexto adicionales para mejorar la detección
        self.additional_context_patterns = {
            'Website': r'(web|sitio|página|página web|navegador|internet|online|en línea|aplicación|app|móvil|celular|teléfono)',
            'Proceso_Pago': r'(pago|tarjeta|crédito|débito|banco|transferencia|efectivo|dinero|costo|precio|monto|importe)',
            'Precios': r'(precio|costo|tarifa|monto|importe|valor|pago|caro|barato|económico|costoso|excesivo)',
            'Aeropuerto': r'(aeropuerto|terminal|pista|vuelo|avion|aeronave|aerolinea|aeropuertos|sala|puerta)',
            'Equipaje': r'(equipaje|maleta|valija|bolso|mochila|bulto|carga|peso|sobrepeso|exceso)',
            'Seats': r'(asiento|silla|asientos|sillas|comodidad|espacio|pasillo|ventana|fila|fila de asientos)',
            'Disponibilidad_Vuelo': r'(vuelo|vuelos|disponibilidad|disponible|horario|hora|fecha|destino|ruta|conexión|escala)',
            'Discount_Club': r'(club|descuento|beneficio|beneficios|membresía|miembro|socio|descuentos|promoción)',
            'Promociones': r'(promoción|promociones|oferta|ofertas|descuento|descuentos|beneficio|beneficios|regalo|regalos)',
            'Datos_Pasajero': r'(pasajero|pasajeros|datos|información|nombre|apellido|documento|pasaporte|identidad|identificación)',
            'Cambios_Devoluciones': r'(cambio|cambios|devolución|devoluciones|reembolso|reembolsos|cancelación|cancelaciones|modificar|modificación)'
        }
        
        # Compilar patrones adicionales
        self.additional_context_regex = {k: re.compile(v, re.IGNORECASE) for k, v in self.additional_context_patterns.items()}
        
        # Patrones de intensidad para mejorar la detección de contexto
        self.intensity_patterns = [
            r'muy\s+',
            r'demasiado\s+',
            r'extremadamente\s+',
            r'super\s+',
            r'ultra\s+',
            r'hiper\s+',
            r'máximo\s+',
            r'total\s+',
            r'completamente\s+',
            r'absolutamente\s+'
        ]
        
        # Compilar patrones de intensidad
        self.intensity_regex = re.compile('|'.join(self.intensity_patterns), re.IGNORECASE)
        
        # Patrones de emoción para mejorar la detección de contexto
        self.emotion_patterns = [
            r'enojado|enojada|enfadado|enfadada|molesto|molesta|irritado|irritada|frustrado|frustrada',
            r'feliz|contento|contenta|satisfecho|satisfecha|alegre|encantado|encantada|encantado|encantada',
            r'triste|decepcionado|decepcionada|desilusionado|desilusionada|deprimido|deprimida',
            r'sorprendido|sorprendida|asombrado|asombrada|impresionado|impresionada|increíble|increible',
            r'preocupado|preocupada|ansioso|ansiosa|nervioso|nerviosa|inquieto|inquieta'
        ]
        
        # Compilar patrones de emoción
        self.emotion_regex = re.compile('|'.join(self.emotion_patterns), re.IGNORECASE)
        
        # Cargar o crear diccionario de sinónimos
        self.synonyms_file = 'Categorization_Analyst/data/learning/synonyms.json'
        self.synonyms = self._load_synonyms()
        
        # Cargar o crear diccionario de coocurrencias
        self.cooccurrence_file = 'Categorization_Analyst/data/learning/cooccurrences.json'
        self.cooccurrences = self._load_cooccurrences()

    def _load_weights(self) -> Dict:
        """Carga los pesos aprendidos del archivo JSON."""
        if os.path.exists(self.weights_file):
            with open(self.weights_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_weights(self, weights: Dict) -> None:
        """Guarda los pesos aprendidos en un archivo JSON."""
        with open(self.weights_file, 'w') as f:
            json.dump(weights, f, indent=4)
            
    def _load_synonyms(self) -> Dict:
        """Carga el diccionario de sinónimos del archivo JSON."""
        if os.path.exists(self.synonyms_file):
            with open(self.synonyms_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_synonyms(self, synonyms: Dict) -> None:
        """Guarda el diccionario de sinónimos en un archivo JSON."""
        with open(self.synonyms_file, 'w') as f:
            json.dump(synonyms, f, indent=4)
            
    def _load_cooccurrences(self) -> Dict:
        """Carga el diccionario de coocurrencias del archivo JSON."""
        if os.path.exists(self.cooccurrence_file):
            with open(self.cooccurrence_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_cooccurrences(self, cooccurrences: Dict) -> None:
        """Guarda el diccionario de coocurrencias en un archivo JSON."""
        with open(self.cooccurrence_file, 'w') as f:
            json.dump(cooccurrences, f, indent=4)

    def _update_weights(self, df: pd.DataFrame) -> None:
        """Actualiza los pesos basado en el análisis de los resultados."""
        # Calcular la efectividad de cada componente por categoría
        category_effectiveness = defaultdict(lambda: {'keyword': [], 'context': [], 'type': []})
        
        # Actualizar sinónimos y coocurrencias
        self._update_synonyms_and_cooccurrences(df)
        
        for _, row in df.iterrows():
            category = row['Categoría']
            if pd.isna(category) or category == 'Otros':
                continue
                
            text = self.clean_text(row['Comentario'])
            type_name = row['Tipo']
            
            # Calcular scores individuales
            keyword_score = self.calculate_keyword_score(text, category)
            context_score = self.calculate_context_score(text, category, type_name)
            type_score = self.calculate_type_score(text, type_name)
            
            # Normalizar scores
            max_keyword_score = len(self.keywords[category]) * 2.5
            max_context_score = 4.0
            max_type_score = len(self.type_keywords.get(type_name, [])) * 1.5
            
            normalized_keyword = keyword_score / max_keyword_score if max_keyword_score > 0 else 0
            normalized_context = context_score / max_context_score if max_context_score > 0 else 0
            normalized_type = type_score / max_type_score if max_type_score > 0 else 0
            
            # Almacenar scores normalizados
            category_effectiveness[category]['keyword'].append(normalized_keyword)
            category_effectiveness[category]['context'].append(normalized_context)
            category_effectiveness[category]['type'].append(normalized_type)
        
        # Calcular nuevos pesos basados en la efectividad
        new_weights = {}
        for category, scores in category_effectiveness.items():
            keyword_mean = np.mean(scores['keyword']) if scores['keyword'] else 0.4
            context_mean = np.mean(scores['context']) if scores['context'] else 0.4
            type_mean = np.mean(scores['type']) if scores['type'] else 0.2
            
            total = keyword_mean + context_mean + type_mean
            if total > 0:
                new_weights[category] = {
                    'keyword': round(keyword_mean / total, 2),
                    'context': round(context_mean / total, 2),
                    'type': round(type_mean / total, 2)
                }
        
        # Guardar nuevos pesos
        self._save_weights(new_weights)
        self.learned_weights = new_weights
        
    def _update_synonyms_and_cooccurrences(self, df: pd.DataFrame) -> None:
        """Actualiza los diccionarios de sinónimos y coocurrencias."""
        # Actualizar sinónimos
        new_synonyms = defaultdict(set)
        for _, row in df.iterrows():
            category = row['Categoría']
            if pd.isna(category) or category == 'Otros':
                continue
                
            text = self.clean_text(row['Comentario'])
            words = set(text.split())
            
            # Agregar palabras como sinónimos si aparecen juntas en el mismo comentario
            for word1 in words:
                for word2 in words:
                    if word1 != word2 and len(word1) > 3 and len(word2) > 3:
                        new_synonyms[word1].add(word2)
        
        # Convertir a diccionario normal
        synonyms_dict = {k: list(v) for k, v in new_synonyms.items()}
        
        # Combinar con sinónimos existentes
        for word, syns in synonyms_dict.items():
            if word in self.synonyms:
                self.synonyms[word] = list(set(self.synonyms[word] + syns))
            else:
                self.synonyms[word] = syns
        
        # Guardar sinónimos actualizados
        self._save_synonyms(self.synonyms)
        
        # Actualizar coocurrencias
        new_cooccurrences = defaultdict(lambda: defaultdict(int))
        for _, row in df.iterrows():
            category = row['Categoría']
            if pd.isna(category) or category == 'Otros':
                continue
                
            text = self.clean_text(row['Comentario'])
            words = text.split()
            
            # Contar coocurrencias de palabras con categorías
            for word in words:
                if len(word) > 3 and word not in self.stopwords:
                    new_cooccurrences[word][category] += 1
        
        # Convertir a diccionario normal
        cooccurrences_dict = {k: dict(v) for k, v in new_cooccurrences.items()}
        
        # Combinar con coocurrencias existentes
        for word, cats in cooccurrences_dict.items():
            if word in self.cooccurrences:
                for cat, count in cats.items():
                    self.cooccurrences[word][cat] = self.cooccurrences[word].get(cat, 0) + count
            else:
                self.cooccurrences[word] = cats
        
        # Guardar coocurrencias actualizadas
        self._save_cooccurrences(self.cooccurrences)

    def clean_text(self, text: str) -> str:
        """Limpia el texto del comentario."""
        if not isinstance(text, str):
            return ""
        
        text = text.lower().translate(self.accents_table)
        text = self.text_cleaner.sub(' ', text)
        text = self.space_cleaner.sub(' ', text)
        
        return text.strip()

    def has_negation(self, text: str, keyword: str) -> bool:
        """Verifica si hay una negación antes de la palabra clave."""
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return False
        
        text_before = text[:keyword_pos]
        return bool(self.negation_regex.search(text_before))
    
    def has_intensity(self, text: str, keyword: str) -> bool:
        """Verifica si hay un intensificador antes de la palabra clave."""
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return False
        
        text_before = text[:keyword_pos]
        return bool(self.intensity_regex.search(text_before))
    
    def has_emotion(self, text: str) -> bool:
        """Verifica si hay palabras de emoción en el texto."""
        return bool(self.emotion_regex.search(text))
    
    def get_synonyms(self, word: str) -> List[str]:
        """Obtiene los sinónimos de una palabra."""
        return self.synonyms.get(word, [])
    
    def get_category_cooccurrence(self, word: str, category: str) -> int:
        """Obtiene la coocurrencia de una palabra con una categoría."""
        if word in self.cooccurrences and category in self.cooccurrences[word]:
            return self.cooccurrences[word][category]
        return 0
    
    def get_additional_context_score(self, text: str, category: str) -> float:
        """Calcula el puntaje basado en patrones de contexto adicionales."""
        if category in self.additional_context_regex:
            pattern = self.additional_context_regex[category]
            matches = len(re.findall(pattern, text))
            return matches * 0.5
        return 0.0

    def calculate_keyword_score(self, text: str, category: str) -> float:
        """Calcula el puntaje basado en palabras clave."""
        score = 0.0
        words = set(text.split())
        
        # Puntaje por palabras clave
        for keyword in self.keywords[category]:
            if keyword in text:
                # Verificar si hay negación
                if self.has_negation(text, keyword):
                    score -= 1.0  # Penalización por negación
                else:
                    score += 1.5  # Aumentado de 1.0 a 1.5
                    # Bonus por coincidencia exacta
                    if keyword in words:
                        score += 1.0  # Aumentado de 0.5 a 1.0
                    
                    # Bonus por intensidad
                    if self.has_intensity(text, keyword):
                        score += 0.5
                    
                    # Bonus por sinónimos
                    synonyms = self.get_synonyms(keyword)
                    for synonym in synonyms:
                        if synonym in text:
                            score += 0.3
                    
                    # Bonus por coocurrencia con la categoría
                    cooccurrence = self.get_category_cooccurrence(keyword, category)
                    if cooccurrence > 0:
                        score += min(0.5, cooccurrence * 0.1)
        
        return score

    def calculate_context_score(self, text: str, category: str, type_name: str) -> float:
        """Calcula el puntaje basado en contexto."""
        score = 0.0
        
        # Puntaje por patrones de contexto específicos
        if category in self.context_patterns:
            pattern = self.context_patterns[category].get(type_name)
            if pattern and re.search(pattern, text):
                score += 3.0  # Aumentado de 2.0 a 3.0
                
                # Bonus por múltiples coincidencias
                matches = len(re.findall(pattern, text))
                if matches > 1:
                    score += 0.5 * (matches - 1)  # Bonus por cada coincidencia adicional
        
        # Puntaje por patrones de contexto adicionales
        additional_score = self.get_additional_context_score(text, category)
        score += additional_score
        
        # Bonus por emoción
        if self.has_emotion(text):
            score += 0.5
        
        return score

    def calculate_type_score(self, text: str, type_name: str) -> float:
        """Calcula el puntaje basado en el tipo."""
        score = 0.0
        words = set(text.split())
        
        if type_name in self.type_keywords:
            keywords = self.type_keywords[type_name]
            matches = sum(1 for keyword in keywords if keyword in words)
            score = matches * 1.0  # Aumentado de 0.5 a 1.0
            
            # Bonus por múltiples coincidencias
            if matches > 1:
                score += 0.5 * (matches - 1)
            
            # Bonus por sinónimos
            for keyword in keywords:
                synonyms = self.get_synonyms(keyword)
                for synonym in synonyms:
                    if synonym in words:
                        score += 0.3
        
        return score

    def calculate_confidence_score(self, row: pd.Series) -> float:
        """
        Calcula el score de confianza para una categorización.
        
        Args:
            row (pd.Series): Fila del DataFrame con la categorización
            
        Returns:
            float: Score de confianza entre 0 y 1
        """
        text = self.clean_text(row['Comentario'])
        category = row['Categoría']
        type_name = row['Tipo']
        
        # Si no hay categoría o tipo, confianza mínima
        if pd.isna(category) or pd.isna(type_name):
            return 0.0
        
        # Calcular diferentes componentes del score
        keyword_score = self.calculate_keyword_score(text, category)
        context_score = self.calculate_context_score(text, category, type_name)
        type_score = self.calculate_type_score(text, type_name)
        
        # Normalizar scores
        max_keyword_score = len(self.keywords[category]) * 2.5
        max_context_score = 4.0
        max_type_score = len(self.type_keywords.get(type_name, [])) * 1.5
        
        normalized_keyword = keyword_score / max_keyword_score if max_keyword_score > 0 else 0
        normalized_context = context_score / max_context_score if max_context_score > 0 else 0
        normalized_type = type_score / max_type_score if max_type_score > 0 else 0
        
        # Obtener pesos específicos para la categoría
        weights = self.learned_weights.get(category, self.category_weights[category])
        
        # Ponderar componentes con pesos específicos
        final_score = (
            weights['keyword'] * normalized_keyword +
            weights['context'] * normalized_context +
            weights['type'] * normalized_type
        )
        
        # Aplicar factor de escala para aumentar scores
        final_score = final_score * 2.0  # Aumentado de 1.75 a 2.0
        
        return min(1.0, final_score)  # Asegurar que no exceda 1.0

    def analyze_categorizations(self, input_file: str, output_file: str) -> None:
        """
        Analiza las categorizaciones y agrega el score de confianza.
        
        Args:
            input_file (str): Ruta al archivo de entrada con las categorizaciones
            output_file (str): Ruta al archivo de salida con los scores
        """
        try:
            # Leer archivo de entrada
            logging.info(f"Leyendo archivo de entrada: {input_file}")
            df = pd.read_excel(input_file)
            
            # Verificar columnas requeridas
            required_columns = ['Comentario', 'Categoría', 'Tipo']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"El archivo debe contener las columnas: {required_columns}")
            
            # Actualizar pesos basado en datos existentes
            print("\nActualizando pesos de categorías...")
            self._update_weights(df)
            
            # Calcular scores de confianza
            print("Calculando scores de confianza...")
            df['Confianza'] = df.apply(self.calculate_confidence_score, axis=1)
            
            # Guardar resultados
            print("Guardando resultados...")
            logging.info(f"Guardando resultados en: {output_file}")
            df.to_excel(output_file, index=False)
            
            # Generar resumen de confianza
            self._generate_confidence_summary(df)
            
            print("\nAnálisis completado exitosamente.")
            
        except Exception as e:
            logging.error(f"Error en el análisis: {str(e)}")
            raise

    def _generate_confidence_summary(self, df: pd.DataFrame) -> None:
        """
        Genera un resumen de los scores de confianza.
        
        Args:
            df (pd.DataFrame): DataFrame con los resultados
        """
        summary_file = 'Categorization_Analyst/data/summaries/confidence_summary.txt'
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Resumen de Confianza en Categorizaciones\n")
            f.write("=====================================\n\n")
            
            # Estadísticas generales
            f.write("Estadísticas Generales:\n")
            f.write("--------------------\n")
            f.write(f"Total de comentarios: {len(df)}\n")
            f.write(f"Confianza promedio: {df['Confianza'].mean():.2%}\n")
            f.write(f"Confianza mediana: {df['Confianza'].median():.2%}\n")
            f.write(f"Desviación estándar: {df['Confianza'].std():.2%}\n\n")
            
            # Distribución de confianza
            f.write("Distribución de Confianza:\n")
            f.write("------------------------\n")
            confidence_ranges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
            for i in range(len(confidence_ranges)-1):
                count = len(df[(df['Confianza'] >= confidence_ranges[i]) & 
                             (df['Confianza'] < confidence_ranges[i+1])])
                percentage = (count / len(df)) * 100
                f.write(f"{confidence_ranges[i]:.1f}-{confidence_ranges[i+1]:.1f}: "
                       f"{count} comentarios ({percentage:.1f}%)\n")
            
            # Confianza por categoría
            f.write("\nConfianza por Categoría:\n")
            f.write("----------------------\n")
            category_stats = df.groupby('Categoría')['Confianza'].agg(['mean', 'count'])
            for category, stats in category_stats.iterrows():
                f.write(f"{category}:\n")
                f.write(f"  - Cantidad: {stats['count']} comentarios\n")
                f.write(f"  - Confianza promedio: {stats['mean']:.2%}\n")
            
            # Confianza por tipo
            f.write("\nConfianza por Tipo:\n")
            f.write("-----------------\n")
            type_stats = df.groupby('Tipo')['Confianza'].agg(['mean', 'count'])
            for type_name, stats in type_stats.iterrows():
                if pd.notna(type_name):  # Solo mostrar tipos no nulos
                    f.write(f"{type_name}:\n")
                    f.write(f"  - Cantidad: {stats['count']} comentarios\n")
                    f.write(f"  - Confianza promedio: {stats['mean']:.2%}\n")

def main():
    """Función principal del script."""
    try:
        # Crear directorios necesarios
        create_directories()
        
        # Configurar logging
        setup_logging()
        
        # Inicializar analizador
        analyzer = CategorizationAnalyzer()
        
        # Definir rutas de archivos
        input_file = Path("Categorization_Analyst/data/output/categorized_comments_v2.xlsx")
        output_file = Path("Categorization_Analyst/data/output/categorized_comments_with_confidence.xlsx")
        
        # Verificar archivo de entrada
        if not input_file.exists():
            raise FileNotFoundError(f"No se encontró el archivo de entrada: {input_file}")
        
        # Ejecutar análisis
        analyzer.analyze_categorizations(str(input_file), str(output_file))
        
    except Exception as e:
        logging.error(f"Error en la ejecución del script: {str(e)}")
        raise

if __name__ == "__main__":
    main() 