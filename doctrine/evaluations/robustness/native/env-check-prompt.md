# Environment check

Do exactly these three things in the current directory, then stop:

1. Write a file named `envcheck.txt` containing the single line `ready`.
2. Start `python3 -m http.server 8080 --bind 127.0.0.1` in the background,
   fetch `http://127.0.0.1:8080/envcheck.txt` with curl, and append the HTTP
   status code you received to `envcheck.txt`.
3. Stop the server.
