## DOCKER

Creazione dell'immagine:
> docker build -t pw14a .

Esecuzione del container:
> docker run -p 8080:8000 pw14a 

Altri comandi di utilità
> ``` 
> docker ps -a
> docker stop <container_id>
> docker exec -it <container_id> bash
> ```

---

## DOCKER COMPOSE

> docker-compose up --build -d

