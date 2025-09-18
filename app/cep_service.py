"""
Serviço para consulta de CEP usando a API ViaCEP.

Este módulo implementa a integração com a API ViaCEP para consulta
de endereços a partir do CEP fornecido pelo usuário.
"""

import httpx
import asyncio
from typing import Dict, Optional, Tuple
from app.logger import logger


class CEPService:
    """Serviço para consulta de CEP usando a API ViaCEP."""
    
    BASE_URL = "https://viacep.com.br/ws"
    TIMEOUT = 10.0
    
    @classmethod
    async def consultar_cep(cls, cep: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Consulta um CEP na API ViaCEP.
        Documentação oficial: https://viacep.com.br/
        
        Args:
            cep: CEP com 8 dígitos numéricos (somente números)
            
        Returns:
            Tuple contendo:
            - Dict com dados do endereço se sucesso, None se erro
            - String com mensagem de erro se houver, None se sucesso
        """
        # Limpar CEP (remover caracteres não numéricos) conforme documentação ViaCEP
        import re
        cep_limpo = re.sub(r'\D', '', cep) if cep else ''
        
        # Validação rigorosa conforme documentação ViaCEP
        if not cep_limpo:
            return None, "CEP é obrigatório"
            
        if len(cep_limpo) != 8:
            return None, "CEP deve ter exatamente 8 dígitos numéricos"
            
        if not cep_limpo.isdigit():
            return None, "CEP deve conter apenas números"
            
        # Validar se não é um CEP inválido conhecido
        if cep_limpo == '00000000' or cep_limpo == '11111111':
            return None, "CEP inválido"
        
        # URL conforme documentação oficial ViaCEP
        url = f"{cls.BASE_URL}/{cep_limpo}/json/"
        
        try:
            logger.info(f"Consultando CEP {cep_limpo} na API ViaCEP")
            
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(url)
                
                # Verificar status HTTP conforme documentação ViaCEP
                if response.status_code == 400:
                    logger.warning(f"CEP {cep_limpo} tem formato inválido")
                    return None, "CEP tem formato inválido"
                
                if response.status_code != 200:
                    logger.error(f"Erro HTTP {response.status_code} ao consultar CEP {cep_limpo}")
                    return None, f"Erro na consulta: serviço ViaCEP indisponível"
                
                # Parse do JSON
                data = response.json()
                
                # Verificar se CEP existe (ViaCEP retorna campo 'erro' quando não encontra)
                if data.get('erro'):
                    logger.warning(f"CEP {cep_limpo} não encontrado na base de dados ViaCEP")
                    return None, "CEP não encontrado"
                
                # Validar campos essenciais retornados pela ViaCEP
                if not data.get('localidade') or not data.get('uf'):
                    logger.warning(f"CEP {cep_limpo} retornou dados incompletos da ViaCEP")
                    return None, "Dados do CEP estão incompletos"
                
                logger.info(f"CEP {cep_limpo} consultado com sucesso: {data['localidade']}/{data['uf']}")
                
                # Retornar dados normalizados conforme estrutura ViaCEP
                return {
                    'cep': data.get('cep', cep_limpo),
                    'logradouro': data.get('logradouro', ''),
                    'complemento': data.get('complemento', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('localidade', ''),  # ViaCEP usa 'localidade' para cidade
                    'uf': data.get('uf', ''),
                    'estado': data.get('estado', ''),
                    'regiao': data.get('regiao', ''),
                    'ibge': data.get('ibge', ''),
                    'gia': data.get('gia', ''),
                    'ddd': data.get('ddd', ''),
                    'siafi': data.get('siafi', '')
                }, None
                
        except httpx.TimeoutException:
            logger.error(f"Timeout ao consultar CEP {cep_limpo} na ViaCEP")
            return None, "Timeout na consulta do CEP - tente novamente"
            
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao consultar CEP {cep_limpo} na ViaCEP: {e}")
            return None, "Erro de conexão com o serviço ViaCEP"
            
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar CEP {cep_limpo} na ViaCEP: {e}")
            return None, "Erro interno na consulta do CEP"
    
    @classmethod
    def consultar_cep_sync(cls, cep: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Versão síncrona da consulta de CEP usando ViaCEP.
        Documentação oficial: https://viacep.com.br/
        
        Args:
            cep: CEP com 8 dígitos numéricos (somente números)
            
        Returns:
            Tuple contendo:
            - Dict com dados do endereço se sucesso, None se erro
            - String com mensagem de erro se houver, None se sucesso
        """
        try:
            # Executar a versão assíncrona de forma síncrona
            return asyncio.run(cls.consultar_cep(cep))
        except Exception as e:
            logger.error(f"Erro ao executar consulta síncrona de CEP {cep} na ViaCEP: {e}")
            return None, "Erro interno na consulta do CEP"


# Função de conveniência para uso direto
async def consultar_cep(cep: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Função de conveniência para consultar CEP usando ViaCEP.
    Documentação oficial: https://viacep.com.br/
    
    Args:
        cep: CEP com 8 dígitos numéricos (somente números)
        
    Returns:
        Tuple contendo dados do endereço e mensagem de erro
    """
    return await CEPService.consultar_cep(cep)


def consultar_cep_sync(cep: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Função de conveniência para consultar CEP de forma síncrona usando ViaCEP.
    Documentação oficial: https://viacep.com.br/
    
    Args:
        cep: CEP com 8 dígitos numéricos (somente números)
        
    Returns:
        Tuple contendo dados do endereço e mensagem de erro
    """
    return CEPService.consultar_cep_sync(cep)