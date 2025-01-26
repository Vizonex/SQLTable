# SQLTable
A Library Inspired by SQLModel that merges Msgspec and SQLAlchemy together. 

## Example

```python
from sqltable import SQLTable, Column, table
from typing import Optional, Annotated

# SQLAlchemy can be directly used for all database operations
from sqlalchemy import select

# SQLTable is a subclass of msgspec.Struct

# This would be an example of using SQLTable as a declarative base
class IDTable(SQLTable):
    id:Annotated[Optional[int], Column(primary_key=True)] = None

# When using a table wrapper we declare the table for use in our database
# This is different from SQLModel as there is less lag/overhang during our inital setup.
@table
class NameTable(IDTable, kw_only=True):
    name:str

if __name__ == "__main__":
    print(select(NameTable).where(NameTable.id > 1))
    
```
