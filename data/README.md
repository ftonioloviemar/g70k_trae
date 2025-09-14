# Pasta de Dados

Esta pasta contém os arquivos de banco de dados SQLite da aplicação.

## Arquivos

- `viemar_garantia.db` - Banco de dados principal da aplicação
- `viemar_garantia.db-shm` - Arquivo de memória compartilhada do SQLite
- `viemar_garantia.db-wal` - Arquivo de log write-ahead do SQLite
- `g70k.db` - Banco de dados auxiliar (se aplicável)
- `viemar.db` - Banco de dados legado (se aplicável)

## Backup

Recomenda-se fazer backup regular dos arquivos `.db` para preservar os dados da aplicação.

## Segurança

Esta pasta deve ser incluída no `.gitignore` em produção para evitar versionamento de dados sensíveis.