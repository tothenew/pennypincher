docker build -t pennypincher .
docker tag pennypincher:latest 743930152640.dkr.ecr.us-east-1.amazonaws.com/pennypincher:demo$1
docker push 743930152640.dkr.ecr.us-east-1.amazonaws.com/pennypincher:demo$1