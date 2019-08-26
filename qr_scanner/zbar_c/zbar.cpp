#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <zbar.h>
#include <iostream>

using namespace cv;
using namespace std;
using namespace zbar;

int main(int argc, char* argv[])
{
    // open the video camera no. 0
    int videoFd = 0;
	VideoCapture cap(videoFd);

	if (!cap.isOpened()) // if not success, exit program
	{
		cout << "Cannot open camera " << videoFd << "." << endl;
		return -1;
	}

	ImageScanner scanner;
	scanner.set_config(ZBAR_NONE, ZBAR_CFG_ENABLE, 1);

	double dWidth = cap.get(CV_CAP_PROP_FRAME_WIDTH); //get the width of frames of the video
	double dHeight = cap.get(CV_CAP_PROP_FRAME_HEIGHT); //get the height of frames of the video

    Mat frame;
    Mat grey;
    bool bSuccess = false;
	while (1)
	{
		bSuccess = cap.read(frame); // read a new frame from video

		if (!bSuccess) //if not success, break loop
		{
			cout << "Cannot read a frame from video stream." << endl;
			break;
		}

		cvtColor(frame, grey, CV_BGR2GRAY);
		uchar *raw = (uchar *)grey.data;

		// wrap image data
        //   might replace the parameters to the image() call by the two next lines
        //   but on arch it works with dWidth and dHeight
		//int width = frame.cols;
		//int height = frame.rows;
		Image image(dWidth, dHeight, "Y800", raw, dWidth * dHeight);

		// scan the image for barcodes
		int n = scanner.scan(image);

		// extract results and print them
		for(Image::SymbolIterator symbol = image.symbol_begin(); symbol != image.symbol_end(); ++symbol)
		{
			cout << "decoded " << symbol->get_type_name() << " symbol " << symbol->get_data() << endl;
		}
	}
	return 0;
}
