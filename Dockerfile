
FROM public.ecr.aws/lambda/python:3.8
COPY . .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
CMD [ "main.cfnresponsefun" ]

