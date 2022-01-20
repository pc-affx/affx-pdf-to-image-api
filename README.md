# PDF To Image API - Python

![Image Icon showing PDF to Image](images/convert.jpg?raw=true "PDF to Image Banner")


## Overview

Due to the pandemic we have found ourselves sharing PDF's more than ever. However still some people face problem understanding the PDF file or opening the same on a compatible app. In all most applications, a person can view a page in the app itself, without installing a different application all together.   

To enable the same, [@formula21](https://formula21.github.io) has bought you an API which accepts a PDF file only to convert it's page(s) to high quality image(s).

Built in Python and deployed through Flask Server, the integrated experience is tailored to any user(s) experience.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/formula21/pdf-to-image-api/tree/main)

## App Documentation

`POST /upload`

`body`:
- `file`: Accepts a PDF documents.

`parameters`
- `page`: Accepts a range from `0` to `(total number of pages - 1)`
    - The property is optional, and will by default is assumed `0`.
- `bundle`: Accepts 0 or 1.
  - The property is optional, and will be ignored if not present.

### Explaining the parameters
#### A. The `page` parameter

>:memo: Note this parameter is conditionally mandatory.

The `page` parameter is an integer, which accepts a range between 0 to one less than the last page number of the PDF. 

- If `0` is given to the `page` parameter, the image for the first page is rendered.

- To generate the last page of a 5-page PDF file, passing `page=4` does the job.

> :bulb: **Tip:** Without the `bundle` parameter, only the `page` parameter **will always render an image**. 

#### B. The `bundle` parameter:
The `bundle` parameter is an integer which is actually a binary i.e. accepts either 0 or 1:

- If `0` is passed with a `page = 2` of a 5-page PDF file, then a zip file containing the images of all pages i.e. Page 1, Page 2, Page 3 will be generated.

- If `1` is passed with a `page=2` of a 5-page PDF file, then a zip file containing the images of all pages i.e. Page 3, Page 4, Page 5 will be generated.

- Concluding, `0` renders the left batch of images up to (and inclusive of) the given page number, while `1` renders the right batch of images from the given page number, till the last page of the PDF.

> :bulb: **Tip:** Specifying `bundle` will always force the output to be a **ZIP file of images**, even if there is only 1 page.

>:memo: Without specifying the `page` parameter, but specifying `bundle=0`, does not render any images.

## License
The project comes with an open-source MIT License. If you have not received the same with your copy of the project here the license is as below:

> Copyright 2022 Anweshan Roy Chowdhury

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.