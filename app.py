import fitz
from flask import Flask, request, make_response
import zipfile, tempfile

app = Flask(__name__)


# noinspection PyBroadException
@app.route('/upload', methods=['POST'])
def upload():
    page_number_arg, bundle_arg = [0], False

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

    # TODO: Add ?bundle=0 or ?bundle=1
    # If we find page also, we will bundle up to that page (inclusive).

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
    return 'Hello!', 200


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
