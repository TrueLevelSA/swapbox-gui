
all: clean
	g++ zbar.cpp -o main.run -lopencv_highgui -lopencv_core -lopencv_imgproc -lzbar

run: all
	./main.run

clean:
	rm *.o *.run -f
