#!/usr/bin/env python3
"""
Sistema de autenticação e autorização
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fasthtml.common import *
from fastlite import Database
from models.usuario import Usuario
import secrets
import hashlib

logger = logging.getLogger(__name__)

# Configurações de sessão
SESSION_COOKIE_NAME = 'viemar_session'
SESSION_TIMEOUT_HOURS = 24

class AuthManager:
    """Gerenciador de autenticação e sessões"""
    
    def __init__(self, db: Database):
        self.db = db
        self.sessions = {}  # Em produção, usar Redis ou banco
    
    def criar_sessao(self, usuario_id: int, usuario_email: str, tipo_usuario: str) -> str:
        """Cria uma nova sessão para o usuário"""
        
        session_id = secrets.token_urlsafe(32)
        session_data = {
            'usuario_id': usuario_id,
            'usuario_email': usuario_email,
            'tipo_usuario': tipo_usuario,
            'criado_em': datetime.now(),
            'expira_em': datetime.now() + timedelta(hours=SESSION_TIMEOUT_HOURS)
        }
        
        self.sessions[session_id] = session_data
        
        logger.info(f"Sessão criada para usuário {usuario_email} (ID: {usuario_id})")
        return session_id
    
    def obter_sessao(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtém dados da sessão se válida"""
        
        if not session_id or session_id not in self.sessions:
            return None
        
        session_data = self.sessions[session_id]
        
        # Verificar se a sessão expirou
        if datetime.now() > session_data['expira_em']:
            del self.sessions[session_id]
            logger.info(f"Sessão expirada removida: {session_id[:8]}...")
            return None
        
        return session_data
    
    def renovar_sessao(self, session_id: str) -> bool:
        """Renova o tempo de expiração da sessão"""
        
        if session_id in self.sessions:
            self.sessions[session_id]['expira_em'] = datetime.now() + timedelta(hours=SESSION_TIMEOUT_HOURS)
            return True
        return False
    
    def destruir_sessao(self, session_id: str) -> bool:
        """Remove a sessão"""
        
        if session_id in self.sessions:
            usuario_email = self.sessions[session_id].get('usuario_email', 'N/A')
            del self.sessions[session_id]
            logger.info(f"Sessão destruída para usuário {usuario_email}")
            return True
        return False
    
    def autenticar_usuario(self, email: str, senha: str) -> Optional[Dict[str, Any]]:
        """Autentica usuário com email e senha"""
        
        try:
            # Buscar usuário no banco
            result = self.db.execute(
                "SELECT id, email, senha_hash, nome, tipo_usuario, confirmado FROM usuarios WHERE email = ?",
                (email.lower().strip(),)
            ).fetchone()
            
            if not result:
                logger.warning(f"Tentativa de login com email inexistente: {email}")
                return None
            
            usuario_id, usuario_email, senha_hash, nome, tipo_usuario, confirmado = result
            
            # Verificar se o email foi confirmado (exceto para administradores)
            if tipo_usuario not in ['admin', 'administrador'] and not confirmado:
                logger.warning(f"Tentativa de login com email não confirmado: {email}")
                return None
            
            # Verificar senha usando bcrypt
            import bcrypt
            if not bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                logger.warning(f"Tentativa de login com senha incorreta: {email}")
                return None
            
            logger.info(f"Login bem-sucedido: {email} ({tipo_usuario})")
            
            return {
                'id': usuario_id,
                'email': usuario_email,
                'nome': nome,
                'tipo_usuario': tipo_usuario,
                'confirmado': confirmado
            }
            
        except Exception as e:
            logger.error(f"Erro na autenticação do usuário {email}: {e}")
            return None
    
    def obter_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados do usuário pelo ID"""
        
        try:
            result = self.db.execute(
                "SELECT id, email, nome, tipo_usuario, confirmado FROM usuarios WHERE id = ?",
                (usuario_id,)
            ).fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'email': result[1],
                    'nome': result[2],
                    'tipo_usuario': result[3],
                    'confirmado': result[4]
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter usuário por ID {usuario_id}: {e}")
        
        return None
    
    def limpar_sessoes_expiradas(self):
        """Remove sessões expiradas (executar periodicamente)"""
        
        agora = datetime.now()
        sessoes_expiradas = [
            session_id for session_id, data in self.sessions.items()
            if agora > data['expira_em']
        ]
        
        for session_id in sessoes_expiradas:
            del self.sessions[session_id]
        
        if sessoes_expiradas:
            logger.info(f"Removidas {len(sessoes_expiradas)} sessões expiradas")

# Instância global do gerenciador de autenticação
auth_manager = None

def init_auth(db: Database) -> AuthManager:
    """Inicializa o sistema de autenticação"""
    global auth_manager
    auth_manager = AuthManager(db)
    logger.info("Sistema de autenticação inicializado")
    return auth_manager

def setup_auth(app):
    """Configura autenticação na aplicação FastHTML"""
    # Esta função será chamada durante a inicialização da aplicação
    # Por enquanto, apenas um placeholder para compatibilidade
    pass

def get_auth_manager() -> AuthManager:
    """Obtém a instância do gerenciador de autenticação"""
    if auth_manager is None:
        raise RuntimeError("Sistema de autenticação não foi inicializado")
    return auth_manager

# Decoradores e middleware

def login_required(f):
    """Decorador que exige autenticação"""
    import asyncio
    import inspect
    
    if inspect.iscoroutinefunction(f):
        async def async_wrapper(request, **kwargs):
            session_id = request.cookies.get(SESSION_COOKIE_NAME)
            if not session_id:
                return RedirectResponse('/login?erro=login_requerido', status_code=302)
            
            session_data = get_auth_manager().obter_sessao(session_id)
            if not session_data:
                return RedirectResponse('/login?erro=sessao_expirada', status_code=302)
            
            # Renovar sessão
            get_auth_manager().renovar_sessao(session_id)
            
            # Adicionar dados do usuário ao request
            request.state.usuario = session_data
            
            return await f(request)
        
        return async_wrapper
    else:
        def wrapper(request, **kwargs):
            session_id = request.cookies.get(SESSION_COOKIE_NAME)
            if not session_id:
                return RedirectResponse('/login?erro=login_requerido', status_code=302)
            
            session_data = get_auth_manager().obter_sessao(session_id)
            if not session_data:
                return RedirectResponse('/login?erro=sessao_expirada', status_code=302)
            
            # Renovar sessão
            get_auth_manager().renovar_sessao(session_id)
            
            # Adicionar dados do usuário ao request
            request.state.usuario = session_data
            
            return f(request)
        
        return wrapper

def admin_required(f):
    """Decorador que exige autenticação de administrador"""
    import asyncio
    import inspect
    
    if inspect.iscoroutinefunction(f):
        async def async_wrapper(request, **kwargs):
            session_id = request.cookies.get(SESSION_COOKIE_NAME)
            if not session_id:
                return RedirectResponse('/login?erro=login_requerido', status_code=302)
            
            session_data = get_auth_manager().obter_sessao(session_id)
            if not session_data:
                return RedirectResponse('/login?erro=sessao_expirada', status_code=302)
            
            # Verificar se é administrador
            if session_data.get('tipo_usuario') not in ['admin', 'administrador']:
                return RedirectResponse('/login?erro=acesso_negado', status_code=302)
            
            # Renovar sessão
            get_auth_manager().renovar_sessao(session_id)
            
            # Adicionar dados do usuário ao request
            request.state.usuario = session_data
            
            return await f(request)
        
        return async_wrapper
    else:
        def wrapper(request, **kwargs):
            logger.info(f"admin_required: Verificando acesso para {request.url}")
            session_id = request.cookies.get(SESSION_COOKIE_NAME)
            logger.info(f"admin_required: session_id = {session_id}")
            if not session_id:
                logger.info("admin_required: Sem session_id, redirecionando para login")
                return RedirectResponse('/login?erro=login_requerido', status_code=302)
            
            session_data = get_auth_manager().obter_sessao(session_id)
            logger.info(f"admin_required: session_data = {session_data}")
            if not session_data:
                logger.info("admin_required: Sessão expirada, redirecionando para login")
                return RedirectResponse('/login?erro=sessao_expirada', status_code=302)
            
            # Verificar se é administrador
            tipo_usuario = session_data.get('tipo_usuario')
            logger.info(f"admin_required: tipo_usuario = {tipo_usuario}")
            if tipo_usuario not in ['admin', 'administrador']:
                logger.info("admin_required: Não é administrador, redirecionando")
                return RedirectResponse('/login?erro=acesso_negado', status_code=302)
            
            # Renovar sessão
            get_auth_manager().renovar_sessao(session_id)
            
            # Adicionar dados do usuário ao request
            request.state.usuario = session_data
            logger.info("admin_required: Acesso autorizado, chamando função")
            
            return f(request)
        
        return wrapper

def get_current_user(request) -> Optional[Dict[str, Any]]:
    """Obtém o usuário atual da sessão com dados completos"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        session_data = get_auth_manager().obter_sessao(session_id)
        if session_data:
            # Buscar dados completos do usuário no banco
            usuario_completo = get_auth_manager().obter_usuario_por_id(session_data['usuario_id'])
            if usuario_completo:
                # Combinar dados da sessão com dados do banco
                return {
                    **session_data,  # dados da sessão (usuario_id, usuario_email, tipo_usuario, etc.)
                    **usuario_completo  # dados do banco (nome, confirmado, etc.)
                }
            return session_data  # fallback para dados da sessão apenas
    return None

def is_authenticated(request) -> bool:
    """Verifica se o usuário está autenticado"""
    return get_current_user(request) is not None

def is_admin(request) -> bool:
    """Verifica se o usuário é administrador"""
    user = get_current_user(request)
    return user is not None and user['tipo_usuario'] in ['admin', 'administrador']

# Funções auxiliares para tokens

def gerar_token_confirmacao() -> str:
    """Gera token para confirmação de email"""
    return secrets.token_urlsafe(32)

def gerar_token_reset_senha() -> str:
    """Gera token para reset de senha"""
    return secrets.token_urlsafe(32)

def validar_token(token: str, usuario_id: int, tipo_token: str) -> bool:
    """Valida token de confirmação ou reset"""
    try:
        db = get_auth_manager().db
        
        if tipo_token == 'confirmacao':
            result = db.execute(
                "SELECT id FROM usuarios WHERE id = ? AND token_confirmacao = ?",
                (usuario_id, token)
            ).fetchone()
        elif tipo_token == 'reset_senha':
            result = db.execute(
                "SELECT id FROM usuarios WHERE id = ? AND token_reset_senha = ?",
                (usuario_id, token)
            ).fetchone()
        else:
            return False
        
        return result is not None
        
    except Exception as e:
        logger.error(f"Erro ao validar token {tipo_token}: {e}")
        return False

def confirmar_email(usuario_id: int, token: str) -> bool:
    """Confirma o email do usuário"""
    try:
        if not validar_token(token, usuario_id, 'confirmacao'):
            return False
        
        db = get_auth_manager().db
        db.execute(
            "UPDATE usuarios SET confirmado = TRUE, token_confirmacao = NULL WHERE id = ?",
            (usuario_id,)
        )
        
        logger.info(f"Email confirmado para usuário ID: {usuario_id}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao confirmar email do usuário {usuario_id}: {e}")
        return False

def resetar_senha(usuario_id: int, token: str, nova_senha: str) -> bool:
    """Reseta a senha do usuário"""
    try:
        if not validar_token(token, usuario_id, 'reset_senha'):
            return False
        
        senha_hash = Usuario.criar_hash_senha(nova_senha)
        
        db = get_auth_manager().db
        db.execute(
            "UPDATE usuarios SET senha_hash = ?, token_reset_senha = NULL WHERE id = ?",
            (senha_hash, usuario_id)
        )
        
        logger.info(f"Senha resetada para usuário ID: {usuario_id}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao resetar senha do usuário {usuario_id}: {e}")
        return False