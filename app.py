from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route
from starlette.templating import _TemplateResponse, Jinja2Templates
from starlette.datastructures import FormData
import uvicorn
import asyncpg

templates = Jinja2Templates(directory = "templates")

connection_pool = None

async def startdatabase():
    global connection_pool
    connection_pool = await asyncpg.create_pool(
            #user and password redacted
            user = "", 
            password = "",
            database = "starletteexample",
            host = "localhost",
            port = 5432)

async def homepage(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "index.html")

async def database_call(request: Request) -> _TemplateResponse:
    result = []

    async with connection_pool.acquire() as connection:
        get_query = await connection.fetch('SELECT * from dogs')
        result.append(get_query)
    
    return templates.TemplateResponse(request, "example.html", {"name" : result})

async def display_form(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "form.html")

async def form(request: Request) -> _TemplateResponse:
    if request.method == "POST":
        form_dictionary: FormData = await request.form()
        form_dictionary_name: str = str(form_dictionary["name"])
        
        return templates.TemplateResponse(request, "result.html", {"form_data" : [form_dictionary, form_dictionary_name]})
    
    return templates.TemplateResponse(request, "form.html")

async def example(request: Request) -> _TemplateResponse:
    name: str = "Star"

    return templates.TemplateResponse(request, "example.html", {"name" : name})

routes: list[Route] = [
    Route("/", endpoint = homepage),
    Route("/displayform", endpoint = display_form),
    Route("/form", endpoint = form, methods = ["POST"]),
    Route("/example", endpoint = example),
    Route("/query", endpoint = database_call),
    ]

app: Starlette = Starlette(debug = True, routes = routes, on_startup = [startdatabase])

if __name__ == "__main__":
    uvicorn.run(app, host = "localhost", port = 8000)
