"""
Componente de filtro reutilizável para telas de listagem.
"""

from fasthtml.common import *
from monsterui.all import *
from typing import Optional, List, Dict, Any


def filter_component(
    fields: list[dict],
    current_filters: dict = None,
    action_url: str = "",
    placeholder_text: str = "Filtrar..."
) -> Div:
    """
    Componente de filtro reutilizável para telas de listagem.
    
    Args:
        fields: Lista de dicionários com 'name', 'label' e 'type' dos campos
        current_filters: Filtros atualmente aplicados
        action_url: URL para onde enviar o formulário de filtro
        placeholder_text: Texto placeholder para campos de texto
    
    Returns:
        Div: Componente de filtro HTML
    """
    if current_filters is None:
        current_filters = {}
    
    filter_inputs = []
    
    for field in fields:
        field_name = field.get('name', '')
        field_label = field.get('label', field_name.title())
        field_type = field.get('type', 'text')
        field_options = field.get('options', [])
        current_value = current_filters.get(field_name, '')
        
        if field_type == 'select':
            options = [Option("Todos", value="", selected=(current_value == ""))]
            for option in field_options:
                if isinstance(option, dict):
                    opt_value = option.get('value', '')
                    opt_label = option.get('label', opt_value)
                else:
                    opt_value = opt_label = str(option)
                
                options.append(
                    Option(opt_label, value=opt_value, selected=(current_value == opt_value))
                )
            
            filter_inputs.append(
                Div(
                    Label(field_label, cls="block text-sm font-medium text-gray-700 mb-1"),
                    Select(
                        *options,
                        name=field_name,
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    ),
                    cls="flex-1 min-w-0"
                )
            )
        else:
            filter_inputs.append(
                Div(
                    Label(field_label, cls="block text-sm font-medium text-gray-700 mb-1"),
                    Input(
                        type=field_type,
                        name=field_name,
                        value=current_value,
                        placeholder=f"{placeholder_text} {field_label.lower()}",
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    ),
                    cls="flex-1 min-w-0"
                )
            )
    
    return Div(
        Card(
            H3("Filtros", cls="text-lg font-semibold text-gray-900 mb-4"),
            Form(
                Div(
                    *filter_inputs,
                    cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-4"
                ),
                Div(
                    Button(
                        "🔍 Filtrar",
                        type="submit",
                        cls="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
                    ),
                    Button(
                        "🗑️ Limpar",
                        type="button",
                        onclick="window.location.href = window.location.pathname",
                        cls="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md font-medium transition-colors ml-2"
                    ),
                    cls="flex justify-start"
                ),
                method="get",
                action=action_url,
                cls="space-y-4",
                id="filter-form"
            ),
            cls="p-6"
        ),
        # Script para capturar Enter nos campos de input
        Script("""
            document.addEventListener('DOMContentLoaded', function() {
                // Aguardar menos tempo para resposta mais rápida
                setTimeout(function() {
                    const form = document.getElementById('filter-form');
                    if (form) {
                        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="number"]');
                        
                        // Função para lidar com Enter
                        function handleEnterPress(e) {
                            if (e.key === 'Enter') {
                                e.preventDefault();
                                e.stopPropagation();
                                
                                // Debug log
                                console.log('Enter pressionado no campo:', e.target.name || e.target.id);
                                
                                // Encontrar o botão de submit e clicar nele
                                const submitBtn = form.querySelector('button[type="submit"]');
                                if (submitBtn) {
                                    submitBtn.click();
                                } else {
                                    // Fallback para form.submit() se não houver botão
                                    form.submit();
                                }
                            }
                        }
                        
                        // Função para lidar com input (quando o usuário digita)
                        function handleInputChange(e) {
                            const input = e.target;
                            
                            // Garantir que o campo mantenha foco após digitar
                            setTimeout(function() {
                                if (document.activeElement !== input) {
                                    input.focus();
                                }
                            }, 10);
                        }
                        
                        inputs.forEach(function(input) {
                            // Remover listeners existentes para evitar duplicação
                            input.removeEventListener('keydown', handleEnterPress);
                            input.removeEventListener('keypress', handleEnterPress);
                            input.removeEventListener('input', handleInputChange);
                            
                            // Adicionar listeners - usar keydown em vez de keypress (mais confiável)
                            input.addEventListener('keydown', handleEnterPress, true);
                            input.addEventListener('input', handleInputChange);
                            
                            // Debug: adicionar log quando o campo ganha/perde foco
                            input.addEventListener('focus', function() {
                                console.log('Campo ganhou foco:', input.name || input.id);
                            });
                            
                            input.addEventListener('blur', function() {
                                console.log('Campo perdeu foco:', input.name || input.id);
                            });
                        });
                        
                        console.log('Filtro Enter: Listeners adicionados a', inputs.length, 'campos');
                    } else {
                        console.error('Filtro Enter: Formulário filter-form não encontrado');
                    }
                }, 50); // Timeout reduzido para 50ms
            });
        """),
        cls="mb-6"
    )