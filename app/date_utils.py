"""
Utilitários para formatação de datas e horas no padrão brasileiro.

Este módulo centraliza todas as formatações de data e hora do sistema,
garantindo consistência no padrão brasileiro:
- Data: dd/MM/yyyy
- Hora: HH:mm:ss
- Data/hora: dd/MM/yyyy HH:mm:ss

Para logs, mantém o formato yyyy-MM-dd HH:mm:ss.
"""

from datetime import datetime
from typing import Optional, Union


def format_date_br(date_value: Union[str, datetime, None]) -> str:
    """
    Formata uma data para exibição no padrão brasileiro (dd/MM/yyyy).
    
    Args:
        date_value: Data a ser formatada (string ISO, datetime ou None)
        
    Returns:
        Data formatada no padrão brasileiro ou 'N/A' se inválida
    """
    if not date_value:
        return 'N/A'
    
    try:
        if isinstance(date_value, str):
            # Tenta diferentes formatos de entrada
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
                try:
                    date_obj = datetime.strptime(date_value, fmt).date()
                    return date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            return date_value  # Retorna original se não conseguir converter
        else:
            # Assume que é um objeto datetime ou date
            if hasattr(date_value, 'date'):
                return date_value.date().strftime('%d/%m/%Y')
            else:
                return date_value.strftime('%d/%m/%Y')
    except Exception:
        return 'N/A'


def format_time_br(time_value: Union[str, datetime, None]) -> str:
    """
    Formata uma hora para exibição no padrão brasileiro (HH:mm:ss).
    
    Args:
        time_value: Hora a ser formatada (string ISO, datetime ou None)
        
    Returns:
        Hora formatada no padrão brasileiro ou 'N/A' se inválida
    """
    if not time_value:
        return 'N/A'
    
    try:
        if isinstance(time_value, str):
            # Tenta diferentes formatos de entrada
            for fmt in ['%H:%M:%S', '%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
                try:
                    time_obj = datetime.strptime(time_value, fmt)
                    return time_obj.strftime('%H:%M:%S')
                except ValueError:
                    continue
            return time_value  # Retorna original se não conseguir converter
        else:
            # Assume que é um objeto datetime
            return time_value.strftime('%H:%M:%S')
    except Exception:
        return 'N/A'


def format_datetime_br(datetime_value: Union[str, datetime, None]) -> str:
    """
    Formata um datetime para exibição no padrão brasileiro (dd/MM/yyyy HH:mm:ss).
    
    Args:
        datetime_value: DateTime a ser formatado (string ISO, datetime ou None)
        
    Returns:
        DateTime formatado no padrão brasileiro ou 'N/A' se inválido
    """
    if not datetime_value:
        return 'N/A'
    
    try:
        if isinstance(datetime_value, str):
            # Tenta diferentes formatos de entrada
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
                try:
                    dt_obj = datetime.strptime(datetime_value, fmt)
                    return dt_obj.strftime('%d/%m/%Y %H:%M:%S')
                except ValueError:
                    continue
            return datetime_value  # Retorna original se não conseguir converter
        else:
            # Assume que é um objeto datetime
            return datetime_value.strftime('%d/%m/%Y %H:%M:%S')
    except Exception:
        return 'N/A'


def format_datetime_br_short(datetime_value: Union[str, datetime, None]) -> str:
    """
    Formata um datetime para exibição no padrão brasileiro curto (dd/MM/yyyy HH:mm).
    
    Args:
        datetime_value: DateTime a ser formatado (string ISO, datetime ou None)
        
    Returns:
        DateTime formatado no padrão brasileiro curto ou 'N/A' se inválido
    """
    if not datetime_value:
        return 'N/A'
    
    try:
        if isinstance(datetime_value, str):
            # Tenta diferentes formatos de entrada
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
                try:
                    dt_obj = datetime.strptime(datetime_value, fmt)
                    return dt_obj.strftime('%d/%m/%Y %H:%M')
                except ValueError:
                    continue
            return datetime_value  # Retorna original se não conseguir converter
        else:
            # Assume que é um objeto datetime
            return datetime_value.strftime('%d/%m/%Y %H:%M')
    except Exception:
        return 'N/A'


def format_for_database(date_value: Union[str, datetime, None]) -> Optional[str]:
    """
    Formata uma data para armazenamento no banco de dados (yyyy-MM-dd).
    
    Args:
        date_value: Data a ser formatada
        
    Returns:
        Data no formato ISO para banco de dados ou None se inválida
    """
    if not date_value:
        return None


def format_date_iso(date_value: Union[str, datetime, None]) -> str:
    """
    Formata uma data para o padrão ISO (yyyy-MM-dd).
    
    Args:
        date_value: Data a ser formatada (string, datetime ou None)
        
    Returns:
        Data formatada no padrão ISO ou 'N/A' se inválida
    """
    if not date_value:
        return 'N/A'
    
    try:
        if isinstance(date_value, str):
            # Tenta diferentes formatos de entrada
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d/%m/%Y']:
                try:
                    date_obj = datetime.strptime(date_value, fmt).date()
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return date_value  # Retorna original se não conseguir converter
        else:
            # Assume que é um objeto datetime ou date
            if hasattr(date_value, 'date'):
                return date_value.date().strftime('%Y-%m-%d')
            else:
                return date_value.strftime('%Y-%m-%d')
    except Exception:
        return 'N/A'


def format_datetime_iso(datetime_value: Union[str, datetime, None]) -> str:
    """
    Formata uma data/hora para o padrão ISO (yyyy-MM-dd HH:mm:ss).
    
    Args:
        datetime_value: Data/hora a ser formatada (string, datetime ou None)
        
    Returns:
        Data/hora formatada no padrão ISO ou 'N/A' se inválida
    """
    if not datetime_value:
        return 'N/A'
    
    try:
        if isinstance(datetime_value, str):
            # Tenta diferentes formatos de entrada
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y']:
                try:
                    dt_obj = datetime.strptime(datetime_value, fmt)
                    return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            return datetime_value  # Retorna original se não conseguir converter
        else:
            # Assume que é um objeto datetime
            return datetime_value.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return 'N/A'


def parse_iso_date(date_str: str) -> Optional[datetime]:
    """
    Converte uma string de data ISO para objeto datetime.
    
    Args:
        date_str: String de data no formato ISO (yyyy-MM-dd)
        
    Returns:
        Objeto datetime ou None se inválida
    """
    if not date_str or date_str == 'N/A':
        return None
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None
    
    try:
        if isinstance(date_value, str):
            # Se já está no formato correto
            if len(date_value) == 10 and date_value.count('-') == 2:
                return date_value
            # Tenta converter do formato brasileiro
            try:
                dt_obj = datetime.strptime(date_value, '%d/%m/%Y')
                return dt_obj.strftime('%Y-%m-%d')
            except ValueError:
                return date_value
        else:
            # Assume que é um objeto datetime ou date
            if hasattr(date_value, 'date'):
                return date_value.date().strftime('%Y-%m-%d')
            else:
                return date_value.strftime('%Y-%m-%d')
    except Exception:
        return None


def format_datetime_for_database(datetime_value: Union[str, datetime, None]) -> Optional[str]:
    """
    Formata um datetime para armazenamento no banco de dados (yyyy-MM-dd HH:mm:ss).
    
    Args:
        datetime_value: DateTime a ser formatado
        
    Returns:
        DateTime no formato ISO para banco de dados ou None se inválido
    """
    if not datetime_value:
        return None
    
    try:
        if isinstance(datetime_value, str):
            # Se já está no formato correto
            if len(datetime_value) >= 19 and datetime_value.count('-') == 2 and datetime_value.count(':') == 2:
                return datetime_value
            # Tenta converter do formato brasileiro
            for fmt in ['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M']:
                try:
                    dt_obj = datetime.strptime(datetime_value, fmt)
                    return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            return datetime_value
        else:
            # Assume que é um objeto datetime
            return datetime_value.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return None