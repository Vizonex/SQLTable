# SQLTable
A Library Inspired by SQLModel that merges Msgspec and SQLAlchemy together. 



## Why SQLTable
As a fan of __SQLModel__ I was fond of the way it worked over just sqlalchemy but as 
I started using it more, I noticed many flaws as well as a large amount of unrequired spaghetti-code.
As I started to dig out the problems I was experiencing such as lag in load-times, relationships not 
loading into the json responses as well as the slow response times to pull requests I finally decided 
enough was enough and If I would be honest I am kinda glad I found msgspec soon after to satisfy this 
slowness as well as cut time-consumptions down. Originally I was going to develop my own library called
[CyClass](https://github.com/Vizonex/Cyclass) & [HeapStruct](https://github.com/Vizonex/heapstruct)
due to the difficulty of wrapping msgspec to sqlalchemy but as time rolled on I began to find many intresting 
results as well as better solutions to my problems and so now here we are, another successful library that 
I relate a lot to my first challenge which was winloop. And If I am going to be fair, why write a class twice 
when you could only do it once with SQLTable? 

There still maybe cases where you might need SQLModel still so I will see about thinking of ways you could use 
both of them at the same time.

I hope SQLTable will be the future of databases and I can't wait to see what you, other people as 
well as what companies big and small will end up doing with it. 

SQLTable still has a long way to go and I plan to make a way to use `AsyncAttrs` with it.










