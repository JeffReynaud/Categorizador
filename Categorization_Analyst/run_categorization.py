"""
Script principal para ejecutar el proceso de categorización de comentarios.
"""

import logging
from pathlib import Path
from src.data_preparation.check_environment import main as check_environment
from src.data_preparation.process_comments import main as process_comments

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('categorization_process.log'),
        logging.StreamHandler()
    ]
)

def main():
    """
    Función principal que ejecuta todo el proceso de categorización.
    """
    try:
        # Obtener el directorio raíz del proyecto
        project_root = Path(__file__).parent
        
        # Verificar entorno
        logging.info("Verificando entorno...")
        if not check_environment():
            logging.error("La verificación del entorno falló. Por favor, corrija los errores antes de continuar.")
            return False
        
        # Configurar rutas de archivos
        input_file = project_root.parent / 'Base' / 'Comentarios_CSAT_Resumen.xlsx'
        output_file = project_root / 'categorized_comments.xlsx'
        
        # Procesar comentarios
        logging.info("Iniciando procesamiento de comentarios...")
        process_comments(str(input_file), str(output_file))
        
        logging.info("Proceso de categorización completado exitosamente")
        return True
        
    except Exception as e:
        logging.error(f"Error durante el proceso de categorización: {str(e)}")
        return False

if __name__ == "__main__":
    main() 