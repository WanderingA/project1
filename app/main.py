import json
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dependencies import get_db, authenticate_user, is_admin_user, LoginData, \
    get_node_number, get_nodes_info, get_classification_node_number, \
    get_node_status, get_nodes_with_classification
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


user1 = None


@app.post("/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    global user1
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if is_admin_user(user):
        user1 = user
        return RedirectResponse(url="/admin/index", status_code=303)
    else:
        user1 = user
        return RedirectResponse(url="/user/index", status_code=303)


@app.get("/admin/index")
async def admin_index(request: Request):
    user = user1
    # print(user)
    if not user:
        # 如果用户未登录或验证失败，重定向到登录页面
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("admin/index.html", {"request": request, "user": user})


@app.get("/user/index")
async def user_index(request: Request, db: Session = Depends(get_db)):
    user = user1
    if not user:
        # 如果用户未登录或验证失败，重定向到登录页面
        return RedirectResponse(url="/", status_code=303)
    node_number = get_node_number(db)
    node_classification = get_classification_node_number(db)
    chart_data = json.dumps([{"value": count, "name": classification} for classification, count in node_classification])
    node_status = get_node_status(db)
    status = json.dumps([{"value": value} for value in node_status])

    return templates.TemplateResponse("user/index.html", {"request": request, "node_number": node_number,
                                                          "chart_data": chart_data, "status": status})


@app.get("/user/node-control")
async def user_index(request: Request, db: Session = Depends(get_db)):
    node_data = get_nodes_info(db, 0, 10)
    return templates.TemplateResponse("user/NodeContrl.html", {"request": request, "node_data": node_data})


@app.get("/user/map")
async def user_index(request: Request, db: Session = Depends(get_db)):
    node_allinfo = get_nodes_with_classification(db)
    return templates.TemplateResponse("user/map.html", {"request": request, "node_allinfo": node_allinfo})


@app.get("/get_table_data")
async def get_table_data(db: Session = Depends(get_db)):
    node_allinfo = get_nodes_with_classification(db)
    return node_allinfo


@app.get("/admin/home/console")
async def read_admin_console(request: Request):
    return templates.TemplateResponse("admin/home/console.html", {"request": request})


@app.get("/admin/set/user/info")
async def read_set_info(request: Request):
    return templates.TemplateResponse("admin/set/user/info.html", {"request": request})


@app.get("/admin/set/user/password")
async def read_set_password(request: Request):
    return templates.TemplateResponse("admin/set/user/password.html", {"request": request})


@app.get("/admin/user/user/list")
async def read_user_list(request: Request):
    return templates.TemplateResponse("admin/user/user/list.html", {"request": request})


@app.get("/admin/user/administrators/list")
async def read_administrators_list(request: Request):
    return templates.TemplateResponse("admin/user/administrators/list.html", {"request": request})


@app.get("/admin/user/administrators/role")
async def read_administrators_role(request: Request):
    return templates.TemplateResponse("admin/user/administrators/role.html", {"request": request})

# @app.get("/register")
# async def register(username: str="wsr", password: str="123456aa", db: Session = Depends(get_db)):
#     db_user = register_user(db, username, password)
#     return {"username": db_user.username}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
