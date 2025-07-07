@echo off
REM تفعيل البيئة الافتراضية
call "%cd%\.venv\Scripts\activate.bat"

REM تنفيذ git add, commit, push تلقائياً
git add -A

REM قم بتعديل الرسالة هنا إذا تريد رسالة ثابتة، أو أتركها ديناميكية
set commitMessage=Auto commit at %date% %time%

REM التحقق من وجود تغييرات
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "%commitMessage%"
    git push origin main
) else (
    echo No changes to commit.
)

REM إيقاف تفعيل البيئة الافتراضية
deactivate
