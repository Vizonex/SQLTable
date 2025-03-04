# SQLTable
A Library Inspired by SQLModel that merges Msgspec and SQLAlchemy together. 



## Why SQLTable?

- SQLModel is a little sluggish at times and it's spaghetti-code shows.
- SQLTable retains many API Features from SQLAlchemy and has Mapped Api baked into the project
- Msgspec is easier to work with than Pydantic to some degrees and with it's backend written in
  `C` it's got all the speed required.
- __SQLTable's__ relationship colums & decoder & encoders work as they are supposed to.
- What SQLTable has over SQLModel is that it's Sessions and Engines can be used directly from SQLAlchemy
  Itself rather than needing a third party Session subclass to use which make tools like `aiohttp_sqlalchemy`
  desirable again.
- __SQLTable__ comes with an `AsyncSQLTable` Class that uses `AsyncAttrs`
- Json enocder is built-in to __SQLTable__ itself meaning that if you need a quick an dirty method for writing an HTTP Server API Response 
- Why write a class twice with msgspec.Struct and Sqlalchemy's DeclarativeBase when you only need to do it once with SQLTable? 

As a fan of __SQLModel__ I was fond of the way it worked over just sqlalchemy but as 
I started using it more, but I soon noticed many flaws as well as a large amount of unrequired spaghetti-code.
As I started to dig out the problems I was experiencing such as lag in load-times, relationships not 
loading into the json responses as well as the slow response times to pull requests I finally decided 
enough was enough and if I would be honest I am kinda glad I found msgspec soon after to satisfy this 
slowness as well as cut time-consumptions down. Originally I was going to develop my own library called
[CyClass](https://github.com/Vizonex/Cyclass) & [HeapStruct](https://github.com/Vizonex/heapstruct)
due to the difficulty of wrapping msgspec to sqlalchemy but as time rolled on, I began to find/discover many intresting 
ways to make the libraries work correctly together.
I relate a lot to my first experince making a library which was [winloop](https://github.com/Vizonex/winloop).

There will still be cases where you might need SQLModel still so I will see about thinking of ways you could use 
both of them at the same time.

I hope SQLTable will be the future of databases and I can't wait to see what you & other people will end up 
doing with it. 

## Examples
What if we wanted to write a proxy service? SQLTable Adapts many aspects from SQLAlchemy, SQLModel and msgspec 
and binds them all together
```python
from sqltable import SQLTable
from sqltable.orm import Mapped, mapped_column
from python_socks import ProxyType


class ProxyTable(SQLTable, table=True):    
    host:Mapped[str]
    port:Mapped[int]
    type:Mapped[ProxyType] = ProxyType.HTTP
    id:Mapped[int] = mapped_column(primary_key=True, default=None)


```

The personality of the code from SQLModel Remains the same but Mapped API is used instead as directed by the SQLAlchemy Dev's 
recommendations. Json Enocders are built in but you could also add in the `SQLTableDecoderMixin` If you plan to webscrape 
an ajax api of some sort in your project.

```python
from sqltable import SQLTable, SQLTableDecoderMixin
from sqltable.orm import Mapped, mapped_column
from python_socks import ProxyType


class ProxyTable(SQLTableDecoderMixin, SQLTable, table=True):    
    host:Mapped[str]
    port:Mapped[int]
    type:Mapped[ProxyType] = ProxyType.HTTP
    id:Mapped[int] = mapped_column(primary_key=True, default=None)


proxy = ProxyTable("127.0.0.1", 9150, ProxyType.SOCKS5)
# Json Response is b'{"host":"127.0.0.1","port":9150,"type":2,"id":null}'
print(proxy.encode())
print(ProxyTable.decode(b'{"host":"127.0.0.1","port":9150,"type":2,"id":null}'))
```
 










