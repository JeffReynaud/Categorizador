"""
Script para validar el entorno y las dependencias necesarias.
"""

import sys
import logging
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_python_version():
    """Verifica la versión de Python."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        logging.error(f"Se requiere Python {required_version[0]}.{required_version[1]} o superior")
        return False
    return True

def check_required_packages():
    """Verifica las dependencias requeridas."""
    required_packages = {
        'pandas': '1.5.0',
        'numpy': '1.21.0',
        'openpyxl': '3.0.9'
    }
    
    missing_packages = []
    for package, required_version in required_packages.items():
        try:
            installed_version = version(package)
            if installed_version < required_version:
                logging.warning(f"La versión de {package} ({installed_version}) no cumple con los requisitos mínimos ({required_version})")
                missing_packages.append(f"{package}>={required_version}")
        except PackageNotFoundError:
            logging.error(f"El paquete {package} no está instalado")
            missing_packages.append(f"{package}>={required_version}")
    
    return missing_packages

def check_file_structure():
    """Verifica la estructura de directorios necesaria."""
    base_dir = Path(__file__).parent.parent.parent
    required_dirs = [
        base_dir / 'data',
        base_dir / 'src' / 'data_preparation',
        base_dir / 'src' / 'topic_modeling',
        base_dir / 'src' / 'visualization',
        base_dir / 'notebooks'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not dir_path.exists():
            missing_dirs.append(str(dir_path))
    
    return missing_dirs

def check_input_files():
    """Verifica la existencia de los archivos de entrada necesarios."""
    base_dir = Path(__file__).parent.parent.parent.parent
    required_files = [
        base_dir / 'Base' / 'Comentarios_CSAT_Resumen.xlsx',
        base_dir / 'Base' / 'Ejemplo_Categoria.xlsx'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    return missing_files

def main():
    """Función principal para validar el entorno."""
    logging.info("Iniciando validación del entorno...")
    
    # Verificar versión de Python
    if not check_python_version():
        logging.error("La versión de Python no cumple con los requisitos")
        return False
    
    # Verificar paquetes requeridos
    missing_packages = check_required_packages()
    if missing_packages:
        logging.error("Faltan los siguientes paquetes:")
        for package in missing_packages:
            logging.error(f"- {package}")
        return False
    
    # Verificar estructura de directorios
    missing_dirs = check_file_structure()
    if missing_dirs:
        logging.error("Faltan los siguientes directorios:")
        for dir_path in missing_dirs:
            logging.error(f"- {dir_path}")
        return False
    
    # Verificar archivos de entrada
    missing_files = check_input_files()
    if missing_files:
        logging.error("Faltan los siguientes archivos:")
        for file_path in missing_files:
            logging.error(f"- {file_path}")
        return False
    
    logging.info("Validación del entorno completada exitosamente")
    return True

if __name__ == "__main__":
    main() 