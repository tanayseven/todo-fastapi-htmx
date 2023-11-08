
### Run app in local-dev mode

```shell
uvicorn src.main:app --reload
```

### Crete a new revision

```shell
alembic revision --autogenerate -m "revision message"
```

### Upgrade to the latest revision

```shell
alembic upgrade head
```
