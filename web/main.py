"""
Application entry point
"""
import os
from random import randint, sample
from typing import List
from fastapi import (
    FastAPI,
    Request,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from web.models import (
    FormSchema
)
from web import utils


def get_app():
    """
    Return FastAPI application
    """

    application = FastAPI(title="Web")
    return application


async def comparison(
        first_image,  # pylint: disable=W0613
        second_image,  # pylint: disable=W0613
        models: List[str]
):
    img1 = utils.get_alignment_rgb(first_image[..., :3])
    img2 = utils.get_alignment_rgb(second_image[..., :3])
    img = utils.glue_and_prepare(img1, img2)
    result = utils.compare(img, models)
    return {"result": {get_models(str(k)): [v, True if v > 0 else False] for k, v in zip(models, result)}}


# Neural models
def get_models(model_id: str = None):
    """
    Neural networks models
    """

    models = {
        '0': 'VGGFace2_InceptionResnetV1',
        '1': 'Balanced_InceptionResnetV1',
        '2': 'IMAN_Asian_InceptionResnetV1',
        '3': 'IMAN_Indian_InceptionResnetV1',
    }

    if model_id:
        return models[model_id]

    return models


def get_gallery():
    """
    Returns all images from examples directory
    """

    # Examples path and required number of files
    web_path = "/static/examples/"
    examples_path = "./web/static/examples"
    result = []

    # Get all directories from path
    directories = os.listdir(examples_path)

    for _dir in directories:
        files = os.listdir(examples_path + "/" + _dir)
        chosen_files = sample(files, 2)

        result.append([{
            "web": web_path + _dir + "/" + fl,
            "server": examples_path + "/" + _dir + "/" + fl
        } for fl in chosen_files])

    return result


# Start application
app = get_app()

# Bind directory with static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Get templates
templates = Jinja2Templates(directory="web/templates")


# Exceptions
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    Handler for custom 422 exceptions
    """

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(),
                                  "body": exc.body}),
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Index page
    """

    # Select all neural models
    neural_networks = get_models()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "nn": neural_networks,
            "gallery": get_gallery(),
        }
    )


@app.post("/process", response_class=HTMLResponse)
async def process(
        request: Request,
        form_data: FormSchema = Depends(FormSchema.as_form)
):
    """
    Neural network processing
    """

    # Validate form data
    if (not form_data.first_image and not form_data.second_image)\
            and (not form_data.server_image_1 and not form_data.server_image_2):
        response = [
            dict(loc=["files"], msg="Вложите изображения", type="file")
        ]

        raise HTTPException(
            status_code=422,
            detail=response
        )

    # Prepare images
    has_images = False
    if form_data.first_image and form_data.second_image:
        has_images = True
        first_image = utils.decode_str_to_arr(form_data.first_image)
        second_image = utils.decode_str_to_arr(form_data.second_image)

    if form_data.server_image_1 and form_data.server_image_2 and not has_images:
        with open(form_data.server_image_1, "rb") as fl:
            first_image = utils.decode_str_to_arr(fl.read())

        with open(form_data.server_image_2, "rb") as fl:
            second_image = utils.decode_str_to_arr(fl.read())


    # Call fake function
    result = await comparison(
        first_image,
        second_image,
        form_data.models
    )

    # Process form_data
    form_data = utils.process_form_data(form_data)

    if not form_data:
        response = [
            dict(loc=["files"], msg="Недопустимый формат изображения", type="file")
        ]

        raise HTTPException(
            status_code=422,
            detail=response
        )

    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "result": result,
            "form_data": form_data
        }
    )

@app.post("/random")
async def get_random_images():
    """
    Return two random images
    """

    # Examples path and required number of files
    web_path = "/static/examples/"
    examples_path = "./web/static/examples"
    req_num_of_fl = 2

    # Get all directories from path
    directories = os.listdir(examples_path)

    # Return 404 "not found"
    # if directories not found
    if not len(directories):
        raise HTTPException(
            status_code=404,
            detail="Directories not found"
        )

    # Select random directory
    chosen_dir = directories[randint(0, len(directories)-1)]

    # Get files from chosen dir
    files = os.listdir(examples_path + "/" + chosen_dir)

    # Return 4040 "not found" if there
    # are not enough files in the folder
    if len(files) < req_num_of_fl:
        raise HTTPException(
            status_code=404,
            detail="Not enough files in directory"
        )

    # Select the required number of random files
    chosen_files = sample(files, req_num_of_fl)

    # Prepare response
    response = [{
        "web": web_path + chosen_dir + "/" + fl,
        "server": examples_path + "/" + chosen_dir + "/" + fl
    } for fl in chosen_files]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"files": response}
    )