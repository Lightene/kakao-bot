FROM python:3.9

WORKDIR /home

RUN mkdir -p /home/logs

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 컨테이너 포트 노출
EXPOSE 9905

CMD ["python", "main.py"]
