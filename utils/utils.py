from models import db

def validate_required_fields(data, fields, context="Entrada"):
    """
    Valida que los campos requeridos existan y no sean None.
    """
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return None, f"{context}: Faltan campos obligatorios: {', '.join(missing)}"
    return data, None


def is_valid_email(email):
    """
    Verifica formato básico de email.
    """
    return isinstance(email, str) and "@" in email


def is_valid_year(year, min_year=1940, max_year=2025):
    """
    Verifica que el año esté en un rango válido.
    """
    try:
        year = int(year)
        return min_year <= year <= max_year
    except (ValueError, TypeError):
        return False


def standard_error(contexto, mensaje):
    """
    Crea un mensaje de error uniforme.
    """
    return f"{contexto}: {mensaje}"


def format_duplicate(existing_data: dict, new_data: dict, keys: list):
    """
    Arma un dict estándar de duplicados según una lista de claves relevantes.
    """
    return {
        "ya_existe": {k: existing_data.get(k) for k in keys},
        "nuevo": {k: new_data.get(k) for k in keys}
    }


def safe_commit():
    """
    Ejecuta commit seguro, con control de errores.
    """
    try:
        db.session.commit()
    except Exception as e:
        print(f"❌ Error al guardar en base de datos: {e}")
        db.session.rollback()


def handle_force_delete(model, filters):
    """
    Elimina instancias del modelo dado si force=True.
    """
    model.query.filter_by(**filters).delete()
    db.session.flush()


def standard_return(inserted=0, ignored=0, duplicated=None, errors=None):
    """
    Retorno estandarizado para loaders.
    """
    return {
        "inserted": inserted,
        "ignored": ignored,
        "duplicated": duplicated or [],
        "errors": errors or []
    }
