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

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comment_processing.log'),
        logging.StreamHandler()
    ]
)

class CommentProcessor:
    def __init__(self):
        self.categories = CATEGORIES
        self.keywords = KEYWORDS
        self.type_keywords = TYPE_KEYWORDS

    def clean_text(self, text: str) -> str:
        """
        Limpia el texto del comentario.
        
        Args:
            text (str): Texto a limpiar
            
        Returns:
            str: Texto limpio
        """
        if not isinstance(text, str):
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Eliminar caracteres especiales y números
        text = re.sub(r'[^a-záéíóúñ\s]', ' ', text)
        
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar acentos
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        
        return text.strip()

    def identify_category(self, text: str) -> Tuple[str, str]:
        """
        Identifica la categoría y subcategoría del comentario.
        
        Args:
            text (str): Texto del comentario
            
        Returns:
            Tuple[str, str]: (categoría, subcategoría)
        """
        text = self.clean_text(text)
        max_matches = 0
        best_category = 'Otros'
        best_subcategory = None
        
        for category, keywords in self.keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > max_matches:
                max_matches = matches
                best_category = category
                
                # Identificar subcategoría
                for type_name, type_keywords in self.type_keywords.items():
                    if type_name in self.categories[category]['types']:
                        if any(keyword in text for keyword in type_keywords):
                            best_subcategory = type_name
                            break
        
        return best_category, best_subcategory

    def process_file(self, input_file: str, output_file: str) -> None:
        """
        Procesa el archivo de entrada y genera el archivo de salida con las categorizaciones.
        
        Args:
            input_file (str): Ruta al archivo de entrada
            output_file (str): Ruta al archivo de salida
        """
        try:
            # Leer archivo de entrada
            logging.info(f"Leyendo archivo de entrada: {input_file}")
            df = pd.read_excel(input_file)
            
            # Verificar columnas requeridas
            required_columns = ['PNR', 'comentarios']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"El archivo debe contener las columnas: {required_columns}")
            
            # Procesar cada comentario
            results = []
            total_comments = len(df)
            
            for idx, row in df.iterrows():
                if idx % 100 == 0:
                    logging.info(f"Procesando comentario {idx + 1} de {total_comments}")
                
                comment = row['comentarios']
                pnr = row['PNR']
                
                category, subcategory = self.identify_category(comment)
                
                results.append({
                    'PNR': pnr,
                    'Comentario': comment,
                    'Categoría': category,
                    'Subcategoría': subcategory,
                    'Tipo': subcategory
                })
            
            # Crear DataFrame de resultados
            results_df = pd.DataFrame(results)
            
            # Guardar resultados
            logging.info(f"Guardando resultados en: {output_file}")
            results_df.to_excel(output_file, index=False)
            
            # Generar resumen
            self._generate_summary(results_df)
            
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
            
            f.write("\nDistribución por Tipo:\n")
            f.write("----------------------\n")
            type_counts = df['Tipo'].value_counts()
            for type_name, count in type_counts.items():
                f.write(f"{type_name}: {count} comentarios\n")

def main():
    """
    Función principal del script.
    """
    processor = CommentProcessor()
    
    # Rutas de archivos
    input_file = Path("Base/Comentarios_CSAT_Resumen.xlsx")
    output_file = Path("Categorization_Analyst/data/categorized_comments.xlsx")
    
    # Procesar archivo
    processor.process_file(str(input_file), str(output_file))

if __name__ == "__main__":
    main() 