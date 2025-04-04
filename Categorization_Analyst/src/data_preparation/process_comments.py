"""
Script principal para procesar y categorizar comentarios de clientes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from typing import Dict, List, Tuple
import logging
from .categories_config import CATEGORIES, KEYWORDS, TYPE_KEYWORDS
import time
from collections import defaultdict
from datetime import datetime
import concurrent.futures
from functools import lru_cache
import json
import os

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comment_processing.log'),
        logging.StreamHandler()
    ]
)

# Ruta al archivo de aprendizaje
LEARNING_FILE = 'learning_data.json'

class LearningSystem:
    def __init__(self):
        self.learning_data = self._load_learning_data()
        
    def _load_learning_data(self) -> Dict:
        """Carga los datos de aprendizaje desde el archivo."""
        if os.path.exists(LEARNING_FILE):
            with open(LEARNING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'examples': [],
            'category_weights': defaultdict(float),
            'type_weights': defaultdict(float)
        }
    
    def _save_learning_data(self):
        """Guarda los datos de aprendizaje en el archivo."""
        with open(LEARNING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
    
    def add_example(self, text: str, category: str, type_name: str):
        """Agrega un nuevo ejemplo al sistema de aprendizaje."""
        example = {
            'text': text,
            'category': category,
            'type': type_name,
            'timestamp': datetime.now().isoformat()
        }
        self.learning_data['examples'].append(example)
        
        # Actualizar pesos
        self.learning_data['category_weights'][category] += 1
        self.learning_data['type_weights'][type_name] += 1
        
        self._save_learning_data()
    
    def get_weights(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Retorna los pesos actuales de categorías y tipos."""
        return (self.learning_data['category_weights'], 
                self.learning_data['type_weights'])

def print_progress_bar(current, total, start_time, bar_length=50):
    """
    Imprime una barra de progreso con información detallada.
    
    Args:
        current (int): Valor actual
        total (int): Valor total
        start_time (float): Tiempo de inicio
        bar_length (int): Longitud de la barra
    """
    elapsed_time = time.time() - start_time
    progress = current / total
    filled_length = int(bar_length * progress)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    
    # Calcular velocidad y tiempo estimado
    comments_per_second = current / elapsed_time if elapsed_time > 0 else 0
    remaining_comments = total - current
    estimated_time = remaining_comments / comments_per_second if comments_per_second > 0 else 0
    
    # Formatear tiempo estimado
    if estimated_time > 3600:
        time_str = f"{estimated_time/3600:.1f} horas"
    elif estimated_time > 60:
        time_str = f"{estimated_time/60:.1f} minutos"
    else:
        time_str = f"{estimated_time:.0f} segundos"
    
    # Imprimir barra de progreso
    print(f"\rProgreso: [{bar}] {progress*100:.1f}% | "
          f"Procesados: {current}/{total} | "
          f"Velocidad: {comments_per_second:.1f} com/seg | "
          f"Tiempo restante: {time_str} | "
          f"Hora actual: {datetime.now().strftime('%H:%M:%S')}", end='')

class CommentProcessor:
    def __init__(self):
        self.categories = CATEGORIES
        self.keywords = KEYWORDS
        self.type_keywords = TYPE_KEYWORDS
        self.learning_system = LearningSystem()
        
        # Optimización: Crear diccionarios de búsqueda más eficientes
        self.keyword_to_category = {}
        self.type_to_keywords = {}
        self.category_types = {}
        
        # Preprocesar palabras clave para búsqueda más rápida
        self._initialize_lookup_tables()
        
        # Compilar expresiones regulares
        self.text_cleaner = re.compile(r'[^a-z\s]')
        self.space_cleaner = re.compile(r'\s+')
        
        # Crear tabla de traducción para acentos
        self.accents_table = str.maketrans('áéíóú', 'aeiou')
        
        # Patrones de contexto
        self.context_patterns = {
            'Website': {
                'Lentitud': r'(lento|lenta|tarda|demora|pega|se pega)',
                'Confuso': r'(confuso|confusa|confusion|dificil de entender|confundir|entorpecer)',
                'Error': r'(error|fallo|problema|incorrecto|falla|no funciona)',
                'Login': r'(login|entrar|acceso|autenticar|autenticación|cliente banco|tarjeta)',
                'Experiencia': r'(experiencia|molesto|molesta|entorpecer|confundir|cargado|publicidad)'
            },
            'Proceso_Pago': {
                'Rechazo': r'(rechazo|rechazado|rechazan|rechazar|no acepta)',
                'Error': r'(error|fallo|problema|incorrecto|falla|no funciona)'
            },
            'Precios': {
                'Cambia': r'(cambia|aumenta|aumentan|varia|varian)',
                'Alto': r'(alto|caro|costoso|elevado|muy caro)',
                'Tarifa': r'(tarifa|excesivo|irracional|abusivo|aprovechar|monopolio)'
            }
        }

    def _initialize_lookup_tables(self):
        """Inicializa las tablas de búsqueda optimizadas."""
        # Diccionario inverso de palabras clave
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                self.keyword_to_category[keyword] = category
        
        # Diccionario inverso de tipos
        for type_name, keywords in self.type_keywords.items():
            self.type_to_keywords[type_name] = set(keywords)
        
        # Diccionario de tipos por categoría
        for category, info in self.categories.items():
            self.category_types[category] = set(info['types'])

    @lru_cache(maxsize=10000)
    def clean_text(self, text: str) -> str:
        """
        Limpia el texto del comentario con caché para evitar reprocesamiento.
        
        Args:
            text (str): Texto a limpiar
            
        Returns:
            str: Texto limpio
        """
        if not isinstance(text, str):
            return ""
        
        # Optimización: Usar translate para reemplazar acentos
        text = text.lower().translate(self.accents_table)
        
        # Optimización: Usar regex compilado
        text = self.text_cleaner.sub(' ', text)
        text = self.space_cleaner.sub(' ', text)
        
        return text.strip()

    def _analyze_context(self, text: str, category: str) -> str:
        """
        Analiza el contexto del texto para determinar el tipo más apropiado.
        
        Args:
            text (str): Texto del comentario
            category (str): Categoría principal
            
        Returns:
            str: Tipo determinado por contexto
        """
        if category in self.context_patterns:
            for type_name, pattern in self.context_patterns[category].items():
                if re.search(pattern, text):
                    return type_name
        return None

    def _score_category(self, text: str, category: str) -> float:
        """
        Calcula un puntaje para una categoría basado en palabras clave y contexto.
        
        Args:
            text (str): Texto del comentario
            category (str): Categoría a evaluar
            
        Returns:
            float: Puntaje de la categoría
        """
        score = 0.0
        words = set(text.split())
        
        # Obtener pesos del sistema de aprendizaje
        category_weights, _ = self.learning_system.get_weights()
        
        # Puntaje por palabras clave
        for keyword in self.keywords[category]:
            if keyword in text:
                score += 1.0
                # Bonus por coincidencia exacta
                if keyword in words:
                    score += 0.5
        
        # Bonus por contexto
        context_type = self._analyze_context(text, category)
        if context_type:
            score += 2.0
        
        # Aplicar peso de aprendizaje
        if category in category_weights:
            score *= (1 + category_weights[category] / 100)
        
        return score

    def identify_category(self, text: str) -> Tuple[str, str, str]:
        """
        Identifica la categoría principal, subcategoría y tipo del comentario.
        
        Args:
            text (str): Texto del comentario
            
        Returns:
            Tuple[str, str, str]: (categoría principal, subcategoría, tipo)
        """
        text = self.clean_text(text)
        words = set(text.split())
        
        # Calcular puntajes para cada categoría
        category_scores = {}
        for category in self.categories:
            if category != 'Otros':  # Ignorar categoría Otros en la puntuación
                score = self._score_category(text, category)
                if score > 0:
                    category_scores[category] = score
        
        # Si no hay coincidencias, retornar Otros
        if not category_scores:
            return 'Otros', None, None
        
        # Obtener categoría principal
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Determinar tipo basado en contexto y palabras clave
        best_type = None
        category_types = self.category_types[best_category]
        
        # Primero intentar determinar por contexto
        context_type = self._analyze_context(text, best_category)
        if context_type and context_type in category_types:
            best_type = context_type
        else:
            # Si no hay tipo por contexto, buscar por palabras clave
            for type_name in category_types:
                if type_name in self.type_to_keywords:
                    keywords = self.type_to_keywords[type_name]
                    if any(keyword in words for keyword in keywords):
                        best_type = type_name
                        break
        
        # Determinar subcategoría
        secondary_scores = [(cat, score) for cat, score in category_scores.items() 
                          if cat != best_category and score > 0]
        
        best_subcategory = max(secondary_scores, key=lambda x: x[1])[0] if secondary_scores else None
        
        return best_category, best_subcategory, best_type

    def process_batch(self, batch: pd.DataFrame) -> List[Dict]:
        """
        Procesa un lote de comentarios.
        """
        results = []
        for _, row in batch.iterrows():
            category, subcategory, type_class = self.identify_category(row['Comentario'])
            results.append({
                'PNR': row['pnr'],
                'Comentario': row['Comentario'],
                'Categoría': category,
                'Subcategoría': subcategory,
                'Tipo': type_class
            })
        return results

    def process_file(self, input_file: str, output_file: str, batch_size: int = 1000) -> None:
        """
        Procesa el archivo de entrada en lotes para mejor rendimiento.
        
        Args:
            input_file (str): Ruta al archivo de entrada
            output_file (str): Ruta al archivo de salida
        """
        try:
            # Leer archivo de entrada
            logging.info(f"Leyendo archivo de entrada: {input_file}")
            df = pd.read_excel(input_file)
            
            # Verificar columnas requeridas
            required_columns = ['pnr', 'Comentario']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"El archivo debe contener las columnas: {required_columns}")
            
            total_comments = len(df)
            start_time = time.time()
            
            print("\nIniciando procesamiento de comentarios...")
            print(f"Total de comentarios a procesar: {total_comments}")
            print(f"Hora de inicio: {datetime.now().strftime('%H:%M:%S')}\n")
            
            # Procesar en lotes
            results = []
            processed_count = 0
            
            for i in range(0, total_comments, batch_size):
                batch = df.iloc[i:i + batch_size]
                batch_results = self.process_batch(batch)
                results.extend(batch_results)
                
                processed_count += len(batch)
                if processed_count % 100 == 0:
                    print_progress_bar(processed_count, total_comments, start_time)
            
            # Crear DataFrame de resultados
            results_df = pd.DataFrame(results)
            
            # Guardar resultados
            print("\n\nGuardando resultados...")
            logging.info(f"Guardando resultados en: {output_file}")
            results_df.to_excel(output_file, index=False)
            
            # Generar resumen
            print("Generando resumen de categorización...")
            self._generate_summary(results_df)
            
            # Mostrar tiempo total
            total_time = time.time() - start_time
            print(f"\nProceso completado en {total_time/60:.1f} minutos")
            print(f"Hora de finalización: {datetime.now().strftime('%H:%M:%S')}")
            logging.info(f"Proceso completado en {total_time/60:.1f} minutos")
            
        except Exception as e:
            logging.error(f"Error procesando archivo: {str(e)}")
            raise

    def _generate_summary(self, df: pd.DataFrame) -> None:
        """
        Genera un resumen de las categorizaciones.
        
        Args:
            df (pd.DataFrame): DataFrame con los resultados
        """
        summary_file = 'categorization_summary.txt'
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Resumen de Categorización de Comentarios\n")
            f.write("=====================================\n\n")
            
            # Resumen por categoría
            f.write("Distribución por Categoría:\n")
            f.write("------------------------\n")
            category_counts = df['Categoría'].value_counts()
            for category, count in category_counts.items():
                f.write(f"{category}: {count} comentarios\n")
            
            f.write("\nDistribución por Subcategoría:\n")
            f.write("----------------------------\n")
            subcategory_counts = df['Subcategoría'].value_counts()
            for subcategory, count in subcategory_counts.items():
                if pd.notna(subcategory):  # Solo mostrar subcategorías no nulas
                    f.write(f"{subcategory}: {count} comentarios\n")
            
            f.write("\nDistribución por Tipo:\n")
            f.write("----------------------\n")
            type_counts = df['Tipo'].value_counts()
            for type_name, count in type_counts.items():
                if pd.notna(type_name):  # Solo mostrar tipos no nulos
                    f.write(f"{type_name}: {count} comentarios\n")

def main(input_file=None, output_file=None):
    """
    Función principal del script.
    
    Args:
        input_file (str, optional): Ruta al archivo de entrada. Por defecto None.
        output_file (str, optional): Ruta al archivo de salida. Por defecto None.
    """
    processor = CommentProcessor()
    
    # Si no se proporcionan rutas, usar las predeterminadas
    if input_file is None:
        input_file = Path("Base/Comentarios_CSAT_Resumen.xlsx")
    if output_file is None:
        output_file = Path("Categorization_Analyst/data/categorized_comments.xlsx")
    
    # Procesar archivo
    processor.process_file(str(input_file), str(output_file))

if __name__ == "__main__":
    # Crear instancia del procesador
    processor = CommentProcessor()
    
    # Agregar ejemplos de aprendizaje
    examples = [
        {
            "text": "Soy usuaria de jetsmart no presisamente por que me guste sino que por motivos de trabajo mio y estudios de mi hijo debo ocupar la linea aerea que viaja a temuco direscto, pero de pagar $100.000 aprox. a pagar $204.000 por un pasaje solo de ida para mi hijo, me parece una falta de irracionalidad completa, se aprovechan ya que es la inuca empresa que realiza ese recorrido, pero realmente se pasan. Realizare la denuncia correspondiente.",
            "category": "Precios",
            "type": "Tarifa"
        },
        {
            "text": "la pagina esta muy cargada de informacion a proposito para confundir al usuario...botones por todos lados, secuencias de selecciones, ofertas, publicidades de promos y packs y pelotudeces para gastar mas que molestan y entorpecen la compra, lo cual tambien a muchas personas las confunden y ellas sin saber apretar y terminan pagando mas sin necesidad. se aprovechan de la situacion de manejo de plataformas y webs en general.",
            "category": "Website",
            "type": "Experiencia"
        },
        {
            "text": "No sé porque hace poco tiempo no puedo o lo hago con intermitencia entrar como cliente banco estado Smart+ me ayudaron del banco a borrar mis historial pero me deja una o dos veces y después me sale error y me pide autentificar de nuevo como cliente banco estado tengo mis tarjetas al día .espero respuesta ,he tenido que comprar en otras aerolíneas y no es la idea",
            "category": "Website",
            "type": "Login"
        }
    ]
    
    # Agregar ejemplos al sistema de aprendizaje
    for example in examples:
        processor.learning_system.add_example(
            example["text"],
            example["category"],
            example["type"]
        )
    
    # Procesar archivo
    main() 