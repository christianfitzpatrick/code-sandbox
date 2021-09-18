FROM gcc:latest
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN gcc:latest -o main tmp_src/stupid.c
CMD ["./main"]