import cv2
import fitz
import os
import tempfile
import zipfile
import numpy as np
from dotenv import load_dotenv
from flask import Flask, make_response, request

load_dotenv()

CLIENT_ID, CLIENT_SECRET = os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET")
app = Flask(__name__)


def blur_image(img, ksize=(10, 10), output='png'):
    print(ksize)
    copy_img = img
    try:
        if isinstance(img, bytes):
            np_arr = np.frombuffer(img, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # cv2.IMREAD_COLOR in OpenCV 3.1
        assert isinstance(img, np.ndarray)
        img = cv2.blur(img, ksize, cv2.BORDER_DEFAULT)
        assert isinstance(img, np.ndarray)
        img = cv2.imencode("." + output, img)[1].tobytes()
        return img
    except AssertionError:
        return copy_img


@app.route('/upload-url', methods=['GET', 'POST'])
def upload_url():
    page_number_arg, bundle_arg, url_arg = [0], False, None

    if 'url' in request.args and len(request.args.get('url')) > 0:
        # TODO: DOWNLOAD THE CONTENT FROM THE URL.
        pass
    else:
        return 'URL is expected', 400




# noinspection PyBroadException
@app.route('/upload', methods=['POST'])
def upload():
    page_number_arg, bundle_arg, blur_arg, blur_skew = [0], False, False, (10, 10)

    if not (request.method == 'POST' and 'file' in request.files):
        return 'The protocol is invalid.', 405

    uploaded_file = request.files.getlist('file')

    if len(uploaded_file) != 1:
        return 'Please upload a single PDF file.', 400

    uploaded_file = uploaded_file[0]

    if not uploaded_file.mimetype == 'application/pdf':
        return 'Invalid File Type.', 400

    if 'page' in request.args:
        page_number_arg = request.args.get('page')
        if not page_number_arg.isnumeric():
            return 'Page Number should be numeric', 400
        page_number_arg = [0, int(page_number_arg)]

    if 'bundle' in request.args:
        bundle_arg = request.args.get('bundle')
        if bundle_arg.isnumeric() and (int(bundle_arg) == 1 or int(bundle_arg) == 0):
            if int(bundle_arg) == 1:
                # Right side: page number given to Last Page
                page_number_arg = [max(page_number_arg)]
            bundle_arg = True
        else:
            return 'Bundle Number should be 0 or 1', 400

    if 'blur' in request.args:
        blur_arg = request.args.get('blur')
        blur_skew = request.args.get('blur_skew') or (10, 10)

        if not isinstance(blur_skew, tuple):
            blur_skew = (int(blur_skew), int(blur_skew))

        if blur_arg.isnumeric() and (int(blur_arg) == 1 or int(blur_arg) == 0):
            if int(blur_arg) == 1:
                blur_arg = True
            else:
                blur_arg = False
        else:
            return 'Blur should be 0 or 1', 400

    msg = 'Some Internal Error Occurred', 500
    try:
        print("Document is being read!! Upload: Success")
        document = fitz.Document(stream=uploaded_file.stream.read(), filetype='pdf')

        page_count = document.page_count
        page_number = max(page_number_arg)

        if bundle_arg:
            if len(page_number_arg) == 1:
                page_number_arg.append(page_count - 1)
            else:
                page_number = page_number_arg[1]

        print("Checking for page number {page_number} is within bounds or not.".format(page_number=page_number))

        # Page number checking...
        if not (0 <= page_number <= page_count):
            msg = 'Page number must be with in 0 and {max_lim} ' \
                  'both inclusive'.format(max_lim=(page_count - 1)), 400
            raise Exception("Page number out of bounds")

        if not bundle_arg:
            pdf_page = document.load_page(page_number)
            pdf_page_pix = (pdf_page.get_pixmap()).tobytes(output='png')

            if blur_arg:
                pdf_page_pix = blur_image(pdf_page_pix, output='png', ksize=blur_skew)

            img_response = make_response(pdf_page_pix)
            img_response.headers['Content-Type'] = 'image/png'
            img_response.headers['Content-Disposition'] = 'inline; ' \
                                                          'filename=Page-{pg_no}.png'.format(pg_no=(page_number + 1))
            msg = img_response, 200
        else:
            print("Bundle is now scanning from {x} to {y}. Both Inclusive!"
                  .format(x=page_number_arg[0], y=page_number_arg[1]))
            l = 0
            with tempfile.SpooledTemporaryFile() as tmp:
                with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for page_number in range(page_number_arg[0], page_number_arg[1] + 1):
                        pdf_page = document.load_page(page_number)
                        pdf_page_pix = (pdf_page.get_pixmap()).tobytes(output='png')
                        archive.writestr('page-{pnum}.png'.format(pnum=page_number), pdf_page_pix)
                        l += 1
                tmp.seek(0)
                msg = make_response(tmp.read())
                msg.headers['Content-Type'] = 'application/x-zip-compressed'
                msg.headers['Content-Disposition'] = 'attachment; filename=Zip-of-{tot}-images.zip'.format(tot=l)
                msg = msg, 200
    except Exception as e:
        if msg[1] == 500:
            msg = "Exception Thrown: {msg}".format(msg=e.__str__()), 500
        # pass
    finally:
        return msg


@app.route('/')
def index():
    return "<h1>Hello! Welcome to PDF to Image API.</h1>", 200


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)
