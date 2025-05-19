# Implementação do desafio Aiqfome

Essa solução usa Python, [FastAPI](https://fastapi.tiangolo.com/) e [SQLModel](https://sqlmodel.tiangolo.com/) e Postgres, a documentação da API é gerada automaticamente (ver o link abaixo).

## Como rodar a aplicação

Para rodar a aplicação com o banco de dados você precisa ter o Docker e o docker compose instalados e dentro de um clone desse repositório rodar:

```bash
$ docker-compose up
```

<http://localhost:8000/docs>


## Rodar os testes
docker-compose exec web /app/.venv/bin/pyt
est

## TODO

- [x] Cliente
- [ ] Produtos
- [ ] Favoritos
- [ ] Reviews
- [x] Subir para o Github
- [ ] Rodar os testes num Gitbub Action/CI