"""
Teste para verificar se a paginação está com layout horizontal
"""
import pytest
from playwright.sync_api import Page, expect
import time


def test_pagination_horizontal_layout(page: Page):
    """Testa se a paginação está com layout horizontal"""
    
    # Navegar para a página de usuários (que tem paginação)
    page.goto("http://localhost:8000/admin/usuarios")
    
    # Aguardar a página carregar completamente
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Verificar se o container de paginação existe
    pagination_container = page.locator(".pagination-container")
    expect(pagination_container).to_be_visible()
    
    # Verificar se o container tem display flex
    container_styles = page.evaluate("""
        () => {
            const container = document.querySelector('.pagination-container');
            if (!container) return null;
            const styles = window.getComputedStyle(container);
            return {
                display: styles.display,
                flexDirection: styles.flexDirection,
                alignItems: styles.alignItems,
                justifyContent: styles.justifyContent
            };
        }
    """)
    
    assert container_styles is not None, "Container de paginação não encontrado"
    assert container_styles["display"] == "flex", f"Display deveria ser flex, mas é {container_styles['display']}"
    assert container_styles["flexDirection"] == "row", f"Flex direction deveria ser row, mas é {container_styles['flexDirection']}"
    
    # Verificar se os elementos estão na mesma linha (posição Y similar)
    pagination_info = page.locator(".pagination-container .col").first
    pagination_nav = page.locator(".pagination-container .col").nth(1)
    page_size_selector = page.locator(".pagination-container .col").nth(2)
    
    # Obter as posições Y dos elementos
    info_box = pagination_info.bounding_box()
    nav_box = pagination_nav.bounding_box()
    selector_box = page_size_selector.bounding_box()
    
    assert info_box is not None, "Elemento de informação não encontrado"
    assert nav_box is not None, "Elemento de navegação não encontrado"
    assert selector_box is not None, "Elemento seletor não encontrado"
    
    # Verificar se estão aproximadamente na mesma linha (diferença máxima de 20px)
    y_diff_info_nav = abs(info_box["y"] - nav_box["y"])
    y_diff_nav_selector = abs(nav_box["y"] - selector_box["y"])
    
    assert y_diff_info_nav <= 20, f"Elementos não estão na mesma linha: diferença Y entre info e nav = {y_diff_info_nav}px"
    assert y_diff_nav_selector <= 20, f"Elementos não estão na mesma linha: diferença Y entre nav e selector = {y_diff_nav_selector}px"
    
    # Verificar se os elementos estão distribuídos horizontalmente
    assert info_box["x"] < nav_box["x"], "Elemento de informação deveria estar à esquerda da navegação"
    assert nav_box["x"] < selector_box["x"], "Elemento de navegação deveria estar à esquerda do seletor"
    
    print("✅ Teste de layout horizontal da paginação passou!")


def test_pagination_responsive_behavior(page: Page):
    """Testa o comportamento responsivo da paginação"""
    
    # Navegar para a página de usuários
    page.goto("http://localhost:8000/admin/usuarios")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Testar em desktop (1200px)
    page.set_viewport_size({"width": 1200, "height": 800})
    time.sleep(1)
    
    pagination_container = page.locator(".pagination-container")
    expect(pagination_container).to_be_visible()
    
    # Verificar layout horizontal em desktop
    container_styles = page.evaluate("""
        () => {
            const container = document.querySelector('.pagination-container');
            const styles = window.getComputedStyle(container);
            return styles.flexDirection;
        }
    """)
    
    assert container_styles == "row", f"Em desktop deveria ser row, mas é {container_styles}"
    
    # Testar em mobile (400px)
    page.set_viewport_size({"width": 400, "height": 600})
    time.sleep(1)
    
    # Em mobile pode ser column, mas ainda deve funcionar
    container_styles_mobile = page.evaluate("""
        () => {
            const container = document.querySelector('.pagination-container');
            const styles = window.getComputedStyle(container);
            return styles.flexDirection;
        }
    """)
    
    # Em mobile pode ser column ou row, ambos são aceitáveis
    assert container_styles_mobile in ["row", "column"], f"Flex direction inválido em mobile: {container_styles_mobile}"
    
    print("✅ Teste de responsividade da paginação passou!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])