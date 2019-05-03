tasklist /FI "IMAGENAME eq php.exe" 2>NUL | find /I /N "php.exe">NUL
if NOT "%ERRORLEVEL%"=="0" (
  cd www
  start ..\php\php.exe -S localhost:8000
)

"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" http://localhost:8000/start_concept_binding.html