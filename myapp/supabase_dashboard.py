import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://TU-PROYECTO.supabase.co")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "TU_SERVICE_ROLE_KEY")

def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def listar_usuarios_supabase():
    """
    Devuelve una lista de usuarios de Supabase Auth con campos útiles.
    """
    supabase: Client = get_supabase_client()
    users = supabase.auth.admin.list_users()
    users_data = []
    for user in users.users:
        users_data.append({
            'id': user.id,
            'email': user.email,
            'nombre': user.user_metadata.get('nombre', ''),
            'role': user.user_metadata.get('role', ''),
            'subscription': user.user_metadata.get('subscription', ''),
            'created_at': user.created_at,
        })
    return users_data

def actualizar_metadata_usuario_supabase(user_id, new_metadata: dict):
    """
    Actualiza el user_metadata de un usuario de Supabase Auth.
    """
    supabase: Client = get_supabase_client()
    result = supabase.auth.admin.update_user_by_id(user_id, user_metadata=new_metadata)
    return result