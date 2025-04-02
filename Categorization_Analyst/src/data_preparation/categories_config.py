"""
Configuración de categorías y tipos para la clasificación de comentarios.
"""

CATEGORIES = {
    'Datos_Pasajero': {
        'description': 'Comentarios relacionados con el ingreso de los datos de los pasajeros',
        'types': ['Validación', 'Error', 'Incompleto', 'Corrección']
    },
    'Website': {
        'description': 'Comentarios asociados al proceso de compra general en el sitio web',
        'types': ['Usabilidad', 'Navegación', 'Error', 'Funcionalidad']
    },
    'Proceso_Pago': {
        'description': 'Comentarios asociados específicamente al proceso de pago',
        'types': ['Error', 'Proceso', 'Método', 'Confirmación']
    },
    'Discount_Club': {
        'description': 'Comentarios relacionados con la membresía Discount Club',
        'types': ['Beneficios', 'Registro', 'Renovación', 'Uso']
    },
    'Promociones': {
        'description': 'Comentarios relacionados con descuentos, ofertas y promociones',
        'types': ['Oferta', 'Descuento', 'Código', 'Vigencia']
    },
    'Precios': {
        'description': 'Comentarios asociados a los precios de vuelos, equipaje, etc.',
        'types': ['Alto', 'Bajo', 'Comparación', 'Transparencia']
    },
    'Disponibilidad_Vuelo': {
        'description': 'Comentarios sobre disponibilidad de horarios, destinos o conexiones',
        'types': ['Horarios', 'Destinos', 'Conexiones', 'Opciones']
    },
    'Aeropuerto': {
        'description': 'Temas relacionados con el aeropuerto externos al proceso de compra web',
        'types': ['Servicios', 'Ubicación', 'Instalaciones', 'Personal']
    },
    'Seats': {
        'description': 'Temas relacionados con los asientos del avión',
        'types': ['Selección', 'Comodidad', 'Tipo', 'Ubicación']
    },
    'Equipaje': {
        'description': 'Todo lo asociado a los equipajes',
        'types': ['Permitido', 'Exceso', 'Pérdida', 'Daño']
    },
    'Cambios_Devoluciones': {
        'description': 'Temas relacionados con cancelaciones y/o devoluciones de vuelos',
        'types': ['Cancelación', 'Devolución', 'Cambio', 'Política']
    },
    'Otros': {
        'description': 'Categoría para comentarios que no encajan en las anteriores',
        'types': ['General', 'Otro']
    }
}

# Palabras clave para identificar categorías
KEYWORDS = {
    'Datos_Pasajero': ['pasajero', 'datos', 'nombre', 'documento', 'identificación'],
    'Website': ['web', 'sitio', 'página', 'navegación', 'interfaz'],
    'Proceso_Pago': ['pago', 'tarjeta', 'transferencia', 'factura', 'cobro'],
    'Discount_Club': ['discount club', 'membresía', 'club', 'beneficios'],
    'Promociones': ['promoción', 'descuento', 'oferta', 'código', 'cupón'],
    'Precios': ['precio', 'costo', 'tarifa', 'caro', 'barato'],
    'Disponibilidad_Vuelo': ['disponible', 'horario', 'vuelo', 'ruta', 'conexión'],
    'Aeropuerto': ['aeropuerto', 'terminal', 'check-in', 'mostrador'],
    'Seats': ['asiento', 'silla', 'clase', 'comfort', 'ubicación'],
    'Equipaje': ['maleta', 'equipaje', 'bagaje', 'valija'],
    'Cambios_Devoluciones': ['cancelar', 'devolver', 'cambio', 'reembolso'],
    'Otros': []
}

# Palabras clave para identificar tipos
TYPE_KEYWORDS = {
    'Validación': ['validar', 'verificar', 'confirmar'],
    'Error': ['error', 'fallo', 'problema', 'incorrecto'],
    'Incompleto': ['incompleto', 'faltante', 'pendiente'],
    'Corrección': ['corregir', 'actualizar', 'modificar'],
    'Usabilidad': ['fácil', 'difícil', 'intuitivo', 'complejo'],
    'Navegación': ['navegar', 'menú', 'página', 'sección'],
    'Funcionalidad': ['funcionar', 'característica', 'opción'],
    'Proceso': ['proceso', 'paso', 'etapa'],
    'Método': ['método', 'forma', 'manera'],
    'Confirmación': ['confirmar', 'verificar', 'comprobar'],
    'Beneficios': ['beneficio', 'ventaja', 'privilegio'],
    'Registro': ['registro', 'inscripción', 'afiliación'],
    'Renovación': ['renovar', 'actualizar', 'renovación'],
    'Uso': ['usar', 'utilizar', 'aplicar'],
    'Oferta': ['oferta', 'promoción', 'descuento'],
    'Descuento': ['descuento', 'reducción', 'rebaja'],
    'Código': ['código', 'cupón', 'promo'],
    'Vigencia': ['válido', 'vigente', 'expirar'],
    'Alto': ['alto', 'caro', 'costoso'],
    'Bajo': ['bajo', 'barato', 'económico'],
    'Comparación': ['comparar', 'diferencia', 'otro'],
    'Transparencia': ['transparente', 'claro', 'visible'],
    'Horarios': ['hora', 'horario', 'tiempo'],
    'Destinos': ['destino', 'ruta', 'lugar'],
    'Conexiones': ['conexión', 'escala', 'parada'],
    'Opciones': ['opción', 'alternativa', 'disponible'],
    'Servicios': ['servicio', 'atención', 'asistencia'],
    'Ubicación': ['ubicación', 'lugar', 'sitio'],
    'Instalaciones': ['instalación', 'infraestructura', 'facilidad'],
    'Personal': ['personal', 'empleado', 'staff'],
    'Selección': ['seleccionar', 'elegir', 'escoger'],
    'Comodidad': ['cómodo', 'confort', 'espacio'],
    'Tipo': ['tipo', 'clase', 'categoría'],
    'Permitido': ['permitido', 'autorizado', 'aceptado'],
    'Exceso': ['exceso', 'sobrepeso', 'extra'],
    'Pérdida': ['pérdida', 'extraviado', 'desaparecido'],
    'Daño': ['daño', 'roto', 'deteriorado'],
    'Cancelación': ['cancelar', 'cancelación', 'anular'],
    'Devolución': ['devolver', 'reembolso', 'reembolsar'],
    'Cambio': ['cambiar', 'modificar', 'alterar'],
    'Política': ['política', 'norma', 'regla'],
    'General': ['general', 'otro', 'varios']
} 