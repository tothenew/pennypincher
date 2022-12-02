
FROM public.ecr.aws/lambda/python:3.9.2022.11.24.17
COPY . .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
CMD [ "main.cfnresponsefun" ]