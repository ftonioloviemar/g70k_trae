#!/usr/bin/env python3
"""
Script de manutenção para o sistema de garantia Viemar
Executa tarefas periódicas como notificações de vencimento
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastlite import Database
from app.config import Config
from app.logger import setup_logging, get_logger
from app.email_service import send_warranty_expiry_notification, send_admin_notification

# Configurar logging
setup_logging()
logger = get_logger(__name__)

def check_warranty_expiry():
    """Verifica garantias próximas do vencimento"""
    logger.info("Iniciando verificação de vencimento de garantias")
    
    try:
        db = Database(Config.DATABASE_PATH)
        
        # Buscar garantias que vencem em 30, 15 e 7 dias
        notification_days = [30, 15, 7]
        total_notifications = 0
        
        for days in notification_days:
            target_date = datetime.now() + timedelta(days=days)
            target_date_str = target_date.strftime('%Y-%m-%d')
            
            # Query para buscar garantias que vencem na data alvo
            query = """
            SELECT 
                g.id,
                g.data_vencimento,
                u.nome as usuario_nome,
                u.email as usuario_email,
                p.descricao as produto_nome,
                v.marca || ' ' || v.modelo || ' - ' || v.placa as veiculo_info
            FROM garantias g
            JOIN usuarios u ON g.usuario_id = u.id
            JOIN produtos p ON g.produto_id = p.id
            JOIN veiculos v ON g.veiculo_id = v.id
            WHERE DATE(g.data_vencimento) = DATE(?)
            AND g.ativo = 1
            AND u.ativo = 1
            """
            
            garantias = db.execute(query, (target_date_str,)).fetchall()
            
            for garantia in garantias:
                # Enviar notificação por email
                success = send_warranty_expiry_notification(
                    user_email=garantia['usuario_email'],
                    user_name=garantia['usuario_nome'],
                    produto_nome=garantia['produto_nome'],
                    veiculo_info=garantia['veiculo_info'],
                    days_until_expiry=days
                )
                
                if success:
                    logger.info(f"Notificação enviada para {garantia['usuario_email']} - Garantia vence em {days} dias")
                    total_notifications += 1
                else:
                    logger.error(f"Falha ao enviar notificação para {garantia['usuario_email']}")
        
        # Enviar relatório para administrador
        if total_notifications > 0:
            send_admin_notification(
                subject=f"Relatório de Notificações - {datetime.now().strftime('%d/%m/%Y')}",
                message=f"Foram enviadas {total_notifications} notificações de vencimento de garantias hoje."
            )
        
        logger.info(f"Verificação concluída. {total_notifications} notificações enviadas.")
        return total_notifications
        
    except Exception as e:
        logger.error(f"Erro na verificação de vencimento: {e}")
        send_admin_notification(
            subject="Erro no Sistema de Garantias",
            message=f"Erro na verificação de vencimento de garantias: {e}"
        )
        return 0

def cleanup_expired_sessions():
    """Remove sessões expiradas do banco"""
    logger.info("Iniciando limpeza de sessões expiradas")
    
    try:
        db = Database(Config.DATABASE_PATH)
        
        # Remover sessões expiradas (mais de 24 horas)
        expiry_time = datetime.now() - timedelta(hours=24)
        
        # Assumindo que existe uma tabela de sessões
        # Se não existir, esta parte pode ser removida
        try:
            result = db.execute(
                "DELETE FROM sessions WHERE created_at < ?",
                (expiry_time.isoformat(),)
            )
            logger.info(f"Removidas {result.rowcount} sessões expiradas")
        except Exception:
            # Tabela de sessões pode não existir ainda
            logger.info("Tabela de sessões não encontrada, pulando limpeza")
        
    except Exception as e:
        logger.error(f"Erro na limpeza de sessões: {e}")

def generate_daily_report():
    """Gera relatório diário do sistema"""
    logger.info("Gerando relatório diário")
    
    try:
        db = Database(Config.DATABASE_PATH)
        
        # Estatísticas do dia
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Novas garantias ativadas hoje
        new_warranties = db.execute(
            "SELECT COUNT(*) as count FROM garantias WHERE DATE(data_cadastro) = DATE(?)",
            (today,)
        ).fetchone()['count']
        
        # Novos usuários cadastrados hoje
        new_users = db.execute(
            "SELECT COUNT(*) as count FROM usuarios WHERE DATE(data_cadastro) = DATE(?)",
            (today,)
        ).fetchone()['count']
        
        # Total de garantias ativas
        total_warranties = db.execute(
            "SELECT COUNT(*) as count FROM garantias WHERE ativo = 1"
        ).fetchone()['count']
        
        # Total de usuários ativos
        total_users = db.execute(
            "SELECT COUNT(*) as count FROM usuarios WHERE ativo = 1"
        ).fetchone()['count']
        
        # Garantias que vencem nos próximos 30 dias
        expiring_soon = db.execute(
            "SELECT COUNT(*) as count FROM garantias WHERE data_vencimento BETWEEN DATE('now') AND DATE('now', '+30 days') AND ativo = 1"
        ).fetchone()['count']
        
        report = f"""
Relatório Diário - Sistema de Garantias Viemar
Data: {datetime.now().strftime('%d/%m/%Y')}

=== ATIVIDADE DO DIA ===
- Novas garantias ativadas: {new_warranties}
- Novos usuários cadastrados: {new_users}

=== ESTATÍSTICAS GERAIS ===
- Total de garantias ativas: {total_warranties}
- Total de usuários ativos: {total_users}
- Garantias vencendo em 30 dias: {expiring_soon}

=== ALERTAS ===
"""        
        
        if expiring_soon > 10:
            report += f"- ATENÇÃO: {expiring_soon} garantias vencem nos próximos 30 dias\n"
        
        if new_warranties == 0:
            report += "- Nenhuma garantia foi ativada hoje\n"
        
        # Enviar relatório para administrador
        send_admin_notification(
            subject=f"Relatório Diário - {datetime.now().strftime('%d/%m/%Y')}",
            message=report
        )
        
        logger.info("Relatório diário gerado e enviado")
        
    except Exception as e:
        logger.error(f"Erro na geração do relatório: {e}")

def main():
    """Função principal do script de manutenção"""
    logger.info("=== Iniciando script de manutenção ===")
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        task = sys.argv[1]
        
        if task == "check-expiry":
            check_warranty_expiry()
        elif task == "cleanup":
            cleanup_expired_sessions()
        elif task == "report":
            generate_daily_report()
        elif task == "all":
            check_warranty_expiry()
            cleanup_expired_sessions()
            generate_daily_report()
        else:
            print("Uso: python maintenance.py [check-expiry|cleanup|report|all]")
            sys.exit(1)
    else:
        # Executar todas as tarefas por padrão
        check_warranty_expiry()
        cleanup_expired_sessions()
        generate_daily_report()
    
    logger.info("=== Script de manutenção concluído ===")

if __name__ == "__main__":
    main()