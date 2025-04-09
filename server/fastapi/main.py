from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from routers import login, client
from routers.control import website_control, process_control
from routers.terminal_admin import admin, role, perm, group, terminal
from utils.auth import get_current_user

app = FastAPI(
    title="用户上网行为管控平台",
    version="1.0.0"
)

# 允许跨域（默认允许全部）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(website_control.router, prefix="/website_control", tags=["网站访问控制"],dependencies=[Depends(get_current_user)])
app.include_router(process_control.router,prefix="/process", tags=["进程运行控制"],dependencies=[Depends(get_current_user)])
app.include_router(login.router)
app.include_router(admin.router,prefix="/admin", tags=["管理员管理"],dependencies=[Depends(get_current_user)])
app.include_router(role.router,prefix="/role", tags=["角色管理"],dependencies=[Depends(get_current_user)])
app.include_router(perm.router,prefix="/permission", tags=["权限管理"],dependencies=[Depends(get_current_user)])
app.include_router(group.router,prefix="/group",tags=["分组管理"],dependencies=[Depends(get_current_user)])
app.include_router(terminal.router, prefix="/terminal",tags=["终端管理"],dependencies=[Depends(get_current_user)])
app.include_router(client.router, prefix="/client",tags=["客户端无需拦截的路由"])