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
        'types': ['Usabilidad', 'Navegación', 'Error', 'Funcionalidad', 'Lentitud', 'Confuso', 'Experiencia', 'Login']
    },
    'Proceso_Pago': {
        'description': 'Comentarios asociados específicamente al proceso de pago',
        'types': ['Error', 'Proceso', 'Método', 'Confirmación', 'Rechazo']
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
        'types': ['Alto', 'Bajo', 'Comparación', 'Transparencia', 'Cambia', 'Tarifa']
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
        'types': ['Selección', 'Comodidad', 'Tipo', 'Ubicación', 'Precio']
    },
    'Equipaje': {
        'description': 'Todo lo asociado a los equipajes',
        'types': ['Permitido', 'Exceso', 'Pérdida', 'Daño', 'Precio']
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
    'Datos_Pasajero': ['pasajero', 'datos', 'nombre', 'documento', 'identificación', 'información'],
    'Website': ['web', 'sitio', 'página', 'navegación', 'interfaz', 'plataforma', 'sistema', 'pega', 'lento', 'confuso', 'login', 'entrar', 'acceso', 'autenticar', 'confundir', 'experiencia'],
    'Proceso_Pago': ['pago', 'tarjeta', 'transferencia', 'factura', 'cobro', 'rechazo', 'rechazado', 'rechazan', 'rechazar'],
    'Discount_Club': ['discount club', 'membresía', 'club', 'beneficios', 'descuento', 'miembro'],
    'Promociones': ['promoción', 'descuento', 'oferta', 'código', 'cupón', 'rebaja', 'reducción'],
    'Precios': ['precio', 'costo', 'tarifa', 'caro', 'barato', 'económico', 'costoso', 'aumentan', 'aumento', 'excesivo', 'irracional', 'abusivo'],
    'Disponibilidad_Vuelo': ['disponible', 'horario', 'vuelo', 'ruta', 'conexión', 'escala'],
    'Aeropuerto': ['aeropuerto', 'terminal', 'check-in', 'mostrador', 'counter'],
    'Seats': ['asiento', 'silla', 'clase', 'comfort', 'ubicación', 'selección', 'elegir', 'escoger'],
    'Equipaje': ['maleta', 'equipaje', 'bagaje', 'valija', 'carry on', 'carry-on', 'mochila', 'bolso'],
    'Cambios_Devoluciones': ['cancelar', 'devolver', 'cambio', 'reembolso', 'cancelación'],
    'Otros': []
}

# Palabras clave para identificar tipos
TYPE_KEYWORDS = {
    'Validación': ['validar', 'verificar', 'confirmar', 'validación'],
    'Error': ['error', 'fallo', 'problema', 'incorrecto', 'falla', 'no funciona'],
    'Incompleto': ['incompleto', 'faltante', 'pendiente', 'falta'],
    'Corrección': ['corregir', 'actualizar', 'modificar', 'cambiar'],
    'Usabilidad': ['fácil', 'difícil', 'intuitivo', 'complejo', 'complicado'],
    'Navegación': ['navegar', 'menú', 'página', 'sección', 'buscar'],
    'Funcionalidad': ['funcionar', 'característica', 'opción', 'función'],
    'Lentitud': ['lento', 'lenta', 'tarda', 'demora', 'pega', 'se pega'],
    'Confuso': ['confuso', 'confusa', 'confusión', 'difícil de entender', 'confundir', 'entorpecer'],
    'Experiencia': ['experiencia', 'molesto', 'molesta', 'entorpecer', 'confundir', 'cargado', 'publicidad'],
    'Login': ['login', 'entrar', 'acceso', 'autenticar', 'autenticación', 'cliente banco', 'tarjeta'],
    'Proceso': ['proceso', 'paso', 'etapa', 'tramite', 'trámite'],
    'Método': ['método', 'forma', 'manera', 'medio'],
    'Confirmación': ['confirmar', 'verificar', 'comprobar', 'confirmación'],
    'Rechazo': ['rechazo', 'rechazado', 'rechazan', 'rechazar', 'no acepta'],
    'Beneficios': ['beneficio', 'ventaja', 'privilegio', 'descuento'],
    'Registro': ['registro', 'inscripción', 'afiliación', 'registrar'],
    'Renovación': ['renovar', 'actualizar', 'renovación', 'actualización'],
    'Uso': ['usar', 'utilizar', 'aplicar', 'usar'],
    'Oferta': ['oferta', 'promoción', 'descuento', 'rebaja'],
    'Descuento': ['descuento', 'reducción', 'rebaja', 'descuento'],
    'Código': ['código', 'cupón', 'promo', 'promoción'],
    'Vigencia': ['válido', 'vigente', 'expirar', 'expiración'],
    'Alto': ['alto', 'caro', 'costoso', 'elevado', 'muy caro'],
    'Bajo': ['bajo', 'barato', 'económico', 'accesible'],
    'Comparación': ['comparar', 'diferencia', 'otro', 'otros'],
    'Transparencia': ['transparente', 'claro', 'visible', 'entendible'],
    'Cambia': ['cambia', 'aumenta', 'aumentan', 'varía', 'varían'],
    'Tarifa': ['tarifa', 'excesivo', 'irracional', 'abusivo', 'aprovechar', 'monopolio'],
    'Horarios': ['hora', 'horario', 'tiempo', 'disponible'],
    'Destinos': ['destino', 'ruta', 'lugar', 'ciudad'],
    'Conexiones': ['conexión', 'escala', 'parada', 'conectar'],
    'Opciones': ['opción', 'alternativa', 'disponible', 'opciones'],
    'Servicios': ['servicio', 'atención', 'asistencia', 'ayuda'],
    'Ubicación': ['ubicación', 'lugar', 'sitio', 'posición'],
    'Instalaciones': ['instalación', 'infraestructura', 'facilidad', 'equipamiento'],
    'Personal': ['personal', 'empleado', 'staff', 'atendente'],
    'Selección': ['seleccionar', 'elegir', 'escoger', 'selección'],
    'Comodidad': ['cómodo', 'confort', 'espacio', 'comodidad'],
    'Tipo': ['tipo', 'clase', 'categoría', 'modelo'],
    'Permitido': ['permitido', 'autorizado', 'aceptado', 'permite'],
    'Exceso': ['exceso', 'sobrepeso', 'extra', 'sobrepasa'],
    'Pérdida': ['pérdida', 'extraviado', 'desaparecido', 'perdido'],
    'Daño': ['daño', 'roto', 'deteriorado', 'maltratado'],
    'Cancelación': ['cancelar', 'cancelación', 'anular', 'cancelado'],
    'Devolución': ['devolver', 'reembolso', 'reembolsar', 'devolución'],
    'Cambio': ['cambiar', 'modificar', 'alterar', 'cambio'],
    'Política': ['política', 'norma', 'regla', 'condición'],
    'General': ['general', 'otro', 'varios', 'diversos']
} 