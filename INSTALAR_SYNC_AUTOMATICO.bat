@echo off
chcp 65001 >nul
title Instalar Sincronizacao Automatica - Gestao Pneus

echo.
echo ================================================
echo   INSTALADOR DE SINCRONIZACAO AUTOMATICA
echo   SQL Server -^> Supabase (todo dia as 06:00h)
echo ================================================
echo.

:: Verifica se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.x de https://python.org
    pause
    exit /b 1
)

:: Instala dependencias necessarias
echo [1/3] Instalando dependencias Python...
pip install pymssql requests python-dotenv --quiet
if errorlevel 1 (
    echo [AVISO] Falha ao instalar dependencias. Tente manualmente: pip install pymssql requests python-dotenv
)

:: Obtem o caminho absoluto do script de sincronizacao
set "SCRIPT_PATH=%~dp0sincronizar_sql_supabase.py"
set "PYTHON_PATH=%~dp0venv\Scripts\python.exe"

:: Se nao tem venv, usa o python do sistema
if not exist "%PYTHON_PATH%" (
    for /f "tokens=*" %%i in ('where python') do set "PYTHON_PATH=%%i"
)

echo [2/3] Criando tarefa agendada no Windows...
echo.
echo Configuracao:
echo   - Script: %SCRIPT_PATH%
echo   - Python: %PYTHON_PATH%
echo   - Horario: Todo dia as 06:00h
echo   - Nome da tarefa: GestaoPneus_SyncSQL
echo.

:: Remove tarefa antiga se existir
schtasks /delete /tn "GestaoPneus_SyncSQL" /f >nul 2>&1

:: Cria a nova tarefa agendada
schtasks /create ^
  /tn "GestaoPneus_SyncSQL" ^
  /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" --limite 20000" ^
  /sc daily ^
  /st 06:00 ^
  /ru "%USERNAME%" ^
  /rl highest ^
  /f

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao criar a tarefa agendada.
    echo Tente executar este arquivo como Administrador.
    pause
    exit /b 1
)

echo.
echo [3/3] Executando a primeira sincronizacao agora...
echo (Isso pode levar alguns minutos)
echo.
python "%SCRIPT_PATH%" --limite 20000

echo.
echo ================================================
echo   INSTALACAO CONCLUIDA!
echo ================================================
echo.
echo A sincronizacao agora roda automaticamente:
echo   - Todo dia as 06:00h (sem precisar fazer nada)
echo   - Ate 20.000 veiculos por vez
echo.
echo Para verificar a tarefa: Agendador de Tarefas do Windows
echo Para rodar manualmente: python sincronizar_sql_supabase.py
echo Para desinstalar: schtasks /delete /tn "GestaoPneus_SyncSQL" /f
echo.
pause
