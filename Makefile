

build:
	docker build -t blockchain-node .

clean:
	docker-compose down

start:
	docker-compose up
