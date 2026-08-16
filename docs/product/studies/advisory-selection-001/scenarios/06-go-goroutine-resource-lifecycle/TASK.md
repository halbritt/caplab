# beacond memory and connection growth

We run beacond on each edge box, polling three regional status endpoints
every 10 seconds. After a day or two the process has grown from 15 MB to
several hundred, and `ss` shows hundreds of connections to the status
hosts held open. Eventually polls fail with `too many open files`;
restarting clears it for a while. Boxes where one endpoint is
consistently quickest hit the limit within days; where all three answer
at similar speed it barely shows. Expected: flat memory and a handful of
connections however long it runs. Reproduce: run against endpoints with
uneven response times and watch RSS and connection count climb.
