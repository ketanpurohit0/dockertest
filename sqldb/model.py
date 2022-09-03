from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

INTERNAL_SQLITE = "sqlite:///database.db"
EXTERNAL_SQLITE = "sqlite:////my/sqlite/path/database.db"
engine = create_engine(EXTERNAL_SQLITE)


SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(hero_1)
    session.add(hero_2)
    session.add(hero_3)
    session.commit()


with Session(engine) as session:
    statement = select(Hero).where(Hero.name == "Spider-Boy")
    heroes = session.exec(statement).fetchall()
    for hero in heroes:
        print(hero)

# docker build -t sqldbimage . -f Dockerfile.sqldb
# docker run -d --name sqldbimage_c1 sqldbimage 
# docker start --name sqldbimage_c1 (retains memory of database)
