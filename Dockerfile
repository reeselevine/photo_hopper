FROM python:2.7.10

RUN mkdir /photo_hopper

WORKDIR /photo_hopper

RUN pip install requests \
    		facebook-sdk \
		gdata
		
ADD photo_hopper.py ./

CMD [ "python", "photo_hopper.py" ]
