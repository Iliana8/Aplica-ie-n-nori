# PAD – Laborator 3 (2025)  
---

## 1. Scopul lucrării

În acest laborator am migrat aplicația din **Laboratorul 2 – Web Proxy pentru Data-Warehouse**  
pe un **server VPS folosind:

- containere Docker pentru fiecare serviciu
- Docker Compose pentru orchestrare
- Nginx ca reverse proxy pe portul 80
- infrastructură accesibilă prin IP public

Scopul este să demonstrez:

1. Utilizarea unui (pseudo-)Cloud Provider (VPS în Internet)
2. Migrarea unei aplicații existente în acest mediu
3. Configurarea și expunerea serviciilor printr-un reverse proxy
4. Testarea accesului atât local, cât și extern (prin IP public)

---

## 2. Arhitectura sistemului în Lab 3

Arhitectura finală arată astfel:

```text
                  +----------------------------+
                  |        Client extern       |
                  |  (laptop, Postman, curl)  |
                  +-------------+--------------+
                                |
                                | HTTP (port 80, IP public)
                                v
                      +----------------------+
                      |   Nginx (container)  |
                      |  web-proxy-nginx     |
                      +----------+-----------+
                                 |
                                 | HTTP (port 9000, rețea Docker)
                                 v
                      +----------------------+
                      |  FastAPI Reverse     |
                      |  Proxy (container)   |
                      |   service: proxy     |
                      +----------+-----------+
                                 |
                +----------------+------------------+
                |                                   |
                v                                   v
       +------------------+                +------------------+
       |   DW1 (container)|                |   DW2 (container)|
       |  service: dw1    |                |  service: dw2    |
       +------------------+                +------------------+
       (stocare in RAM)                     (stocare in RAM)

````
## 3. Structura proiectului

lab3-cloud-vps-web-proxy/
│
├── app/
│   ├── requirements.txt       # dependențe Python (FastAPI, uvicorn, httpx)
│   ├── dw_server.py           # server DW: gestionează employees (JSON/XML)
│   └── proxy_server.py        # reverse proxy inteligent
│
└── deploy/
    ├── Dockerfile.dw          # imagine pentru DW (dw1, dw2)
    ├── Dockerfile.proxy       # imagine pentru Web Proxy (FastAPI)
    ├── docker-compose.prod.yml  # orchestrare servicii în Docker 
    └── nginx/
        └── nginx.conf         # configurare reverse proxy Nginx (port 80)

## 4. Demonstrarea funcționalităților (testare)

4.1. POST – creare employee (din VPS)
curl -X POST http://localhost/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "role": "Dev", "salary": 15000}'
Răspuns:
{"status":"ok","id":1}
<img width="729" height="66" alt="Screenshot 2025-11-19 at 15 50 12" src="https://github.com/user-attachments/assets/d1a4ca1c-b7b3-4e73-8063-146012a45e2e" />



4.2. GET – listare employees (din VPS)
curl "http://localhost/employees?offset=0&limit=10&format=json"
Exemplu răspuns:
[
  {"id":1,"name":"Alice","role":"Dev","salary":15000.0}
]

<img width="1083" height="33" alt="Screenshot 2025-11-19 at 15 50 38" src="https://github.com/user-attachments/assets/045d85fa-49de-4701-84d3-cf5d8de2755b" />


4.3. Test din exterior (cu IP public)
curl "http://<IP_PUBLIC_VPS>/employees?offset=0&limit=10&format=json"
=> demonstrează că aplicația este accesibilă din Internet, nu doar local.
<img width="981" height="132" alt="Screenshot 2025-11-19 at 15 52 45" src="https://github.com/user-attachments/assets/78714030-a565-450d-b4a4-981bbce09045" />

4.4. Observații:
Aplicația folosește:
2 servere DW (dw1, dw2), fiecare cu propria memorie internă
Reverse Proxy FastAPI care face load balancing și caching
Nginx care ascunde tot sistemul în spatele unui singur endpoint (/employees)
De aceea, dacă datele nu sunt replicate între DW-uri, în funcție de nodul la care ajunge cererea, răspunsul poate fi diferit – comportament real de sistem distribuit.

## 5. Legătura cu cerințele laboratorului

Utilizare Cloud Provider
Am folosit un VPS public  cu IP: 161.97.166.85
Aplicația este accesibilă public la:
http://161.97.166.85/employees.
<img width="1865" height="196" alt="Screenshot 2025-11-19 at 15 54 56" src="https://github.com/user-attachments/assets/cf54ad0e-d8e5-49aa-9649-340e174b5871" />


Migrare aplicație existentă în Cloud
Aplicația din Lab 2 (dw_server + proxy_server) a fost împachetată în imagini Docker.
Serviciile rulează acum complet în containere pe VPS.
<img width="1686" height="85" alt="Screenshot 2025-11-19 at 15 55 37" src="https://github.com/user-attachments/assets/7b5e0234-69f2-4f9f-8cb8-342cbd3149bb" />


Arhitectură cu Reverse Proxy
Nginx stă în fața aplicației și expune un singur endpoint.
Reverse proxy-ul FastAPI distribuie cererile între DW-uri (round-robin) și face caching.
Scalabilitate și distribuirea datelor
Două noduri DW (dw1, dw2) simulează un cluster distribuit.
Demonstrația arată că datele sunt independente pe fiecare nod (stocare in-memory).

## 6. Concluzii
În acest laborator am: 
migrat aplicația distribuită (Lab 2) pe un mediu de tip cloud (VPS)
orchestrat toate componentele cu Docker Compose
expus aplicația printr-un reverse proxy Nginx pe portul 80
demonstrat funcționalitatea prin teste locale (localhost) și externe (IP public)
analizat comportamentul unui sistem distribuit cu mai multe noduri DW și un Web Proxy în față
Acest setup este similar cu arhitecturi folosite în producție în aplicații moderne:
microservicii expuse printr-un API Gateway / Reverse Proxy
servicii de backend multiple (replicate sau shard-uite)
containerizare și orchestrare prin Docker


##Demonstrarea LOAD BALANCING între DW1 și DW2
<img width="824" height="492" alt="Screenshot 2025-11-19 at 16 03 11" src="https://github.com/user-attachments/assets/70828212-2b85-439b-9f4a-7b98ab6bc5f8" />

##Demonstrarea CACHING-ului în Web Proxy
<img width="944" height="750" alt="Screenshot 2025-11-19 at 16 04 40" src="https://github.com/user-attachments/assets/6ceb5c95-792a-4845-9383-21f7af99e89c" />

##Demonstrarea CONCURENȚEI și a comportamentului distribuit




