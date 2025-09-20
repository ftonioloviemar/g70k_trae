"""
Teste para verificar a formatação de data/hora na interface de usuários cadastrados.
Confirma que o formato está correto: dd/MM/yyyy HH:mm:ss
"""

import pytest
from datetime import datetime
from app.date_utils import format_datetime_br


def test_format_datetime_br_format():
    """Testa se a função format_datetime_br retorna o formato correto dd/MM/yyyy HH:mm:ss"""
    
    # Teste com datetime object
    test_datetime = datetime(2025, 9, 20, 14, 30, 45)
    result = format_datetime_br(test_datetime)
    expected = "20/09/2025 14:30:45"
    
    print(f"Teste com datetime object:")
    print(f"Input: {test_datetime}")
    print(f"Output: {result}")
    print(f"Expected: {expected}")
    print(f"Match: {result == expected}")
    
    assert result == expected, f"Esperado '{expected}', mas obteve '{result}'"
    
    # Teste com string ISO
    test_string = "2025-09-17 18:51:50"
    result = format_datetime_br(test_string)
    expected = "17/09/2025 18:51:50"
    
    print(f"\nTeste com string ISO:")
    print(f"Input: {test_string}")
    print(f"Output: {result}")
    print(f"Expected: {expected}")
    print(f"Match: {result == expected}")
    
    assert result == expected, f"Esperado '{expected}', mas obteve '{result}'"
    
    # Teste com string ISO sem segundos
    test_string_no_sec = "2025-09-17 18:51"
    result = format_datetime_br(test_string_no_sec)
    expected = "17/09/2025 18:51:00"
    
    print(f"\nTeste com string ISO sem segundos:")
    print(f"Input: {test_string_no_sec}")
    print(f"Output: {result}")
    print(f"Expected: {expected}")
    print(f"Match: {result == expected}")
    
    assert result == expected, f"Esperado '{expected}', mas obteve '{result}'"


def test_format_verification():
    """Verifica se o formato está exatamente como solicitado: dd/MM/yyyy HH:mm:ss"""
    
    test_cases = [
        (datetime(2025, 1, 1, 0, 0, 0), "01/01/2025 00:00:00"),
        (datetime(2025, 12, 31, 23, 59, 59), "31/12/2025 23:59:59"),
        ("2025-09-18T15:02:39.832026", "18/09/2025 15:02:39"),
        ("2025-09-17 14:50:54", "17/09/2025 14:50:54"),
    ]
    
    print("\n=== VERIFICAÇÃO DE FORMATO ===")
    print("Formato esperado: dd/MM/yyyy HH:mm:ss")
    print("Onde:")
    print("- dd: dia com 2 dígitos")
    print("- MM: mês com 2 dígitos") 
    print("- yyyy: ano com 4 dígitos")
    print("- HH: hora com 2 dígitos (24h)")
    print("- mm: minutos com 2 dígitos")
    print("- ss: segundos com 2 dígitos")
    print("=" * 40)
    
    for i, (input_val, expected) in enumerate(test_cases, 1):
        result = format_datetime_br(input_val)
        
        print(f"\nTeste {i}:")
        print(f"Input: {input_val}")
        print(f"Output: {result}")
        print(f"Expected: {expected}")
        
        # Verifica o formato usando regex
        import re
        pattern = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$'
        format_match = re.match(pattern, result)
        
        print(f"Formato correto (dd/MM/yyyy HH:mm:ss): {'✓' if format_match else '✗'}")
        print(f"Conteúdo correto: {'✓' if result == expected else '✗'}")
        
        assert format_match, f"Formato incorreto: '{result}' não segue o padrão dd/MM/yyyy HH:mm:ss"
        assert result == expected, f"Esperado '{expected}', mas obteve '{result}'"


if __name__ == "__main__":
    print("TESTE DE VERIFICAÇÃO DA FORMATAÇÃO DE DATA/HORA")
    print("=" * 50)
    
    test_format_datetime_br_format()
    test_format_verification()
    
    print("\n" + "=" * 50)
    print("✓ TODOS OS TESTES PASSARAM!")
    print("✓ Formato confirmado: dd/MM/yyyy HH:mm:ss")
    print("✓ A formatação está correta na interface!")