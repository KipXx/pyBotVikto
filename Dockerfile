FROM python

COPY . /python

WORKDIR /python

EXPOSE 8000

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install aiogram
RUN pip install sqlalchemy

CMD [ "python", "run.py" ]