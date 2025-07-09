import os
from supabase import create_client, Client

SUPABASE_URL = "https://gvgmhdxarjgvfykoyqyw.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd2Z21oZHhhcmpndmZ5a295cXl3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODQ2NTAyMywiZXhwIjoyMDY0MDQxMDIzfQ.FC-sEU-PU1kU38FiY_xCSMBxxldyi5lDLlgEAHEBQfg"

def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def listar_usuarios_supabase():
    """
    Devuelve una lista de usuarios de Supabase Auth con campos útiles.
    """
    supabase: Client = get_supabase_client()
    response = supabase.auth.admin.list_users()
    
    # Manejar diferentes tipos de respuesta
    if hasattr(response, 'users'):
        users_list = response.users
    elif isinstance(response, list):
        users_list = response
    elif hasattr(response, 'data') and hasattr(response.data, 'users'):
        users_list = response.data.users
    elif hasattr(response, 'data') and isinstance(response.data, list):
        users_list = response.data
    else:
        return []
    
    users_data = []
    for user in users_list:
        # Soportar tanto objeto como dict
        if hasattr(user, 'id'):
            user_dict = user.__dict__ if hasattr(user, '__dict__') else user
        else:
            user_dict = user

        # Extraer metadata de ambos posibles lugares
        meta = user_dict.get('user_metadata', {}) or user_dict.get('raw_user_meta_data', {})
        users_data.append({
            'id': user_dict.get('id', ''),
            'email': user_dict.get('email', ''),
            'nombre': meta.get('nombre', meta.get('name', '')),
            'role': meta.get('role', ''),
            'subscription': meta.get('subscription', ''),
            'created_at': user_dict.get('created_at', ''),
            'provider': user_dict.get('raw_app_meta_data', {}).get('provider', ''),
            'avatar_url': meta.get('avatar_url', meta.get('picture', '')),
        })
    return users_data

def actualizar_metadata_usuario_supabase(user_id, new_metadata: dict):
    """
    Actualiza el user_metadata de un usuario de Supabase Auth.
    """
    supabase: Client = get_supabase_client()
    # La clave correcta es 'attributes', no 'user_metadata'
    result = supabase.auth.admin.update_user_by_id(user_id, attributes={
        "user_metadata": new_metadata
    })
    return result