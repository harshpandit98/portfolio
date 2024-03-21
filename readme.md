
Repository consisting demonstration project

#### Venv based setup instruction

Required python version: 3.10 or above

Create the virtual environment:

```python -m venv /path/to/environment```

Activate the virtual environment:

```source /path/to/environment/bin/active```

Install the requirements:

```pip install -r requirements.txt```

Execute the program:

```python ./src/main.py```

#### Docker based setup instruction

Required tool: docker


Pull the image:

```docker pull harshpandit98/imagehub:listing_crawler```


Run the container:

```docker run --name listing_container harshpandit98/imagehub:listing_crawler```


Inspect exports by copying locally:
```
docker cp listing_container:/data.json .
docker cp listing_container:/temp.db .
```