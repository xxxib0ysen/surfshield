from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from routers import login, client
from routers.control import website_control, process_control
from routers.log import log
from routers.monitor import process_monitor, behavior
from routers.terminal_admin import admin, role, perm, group, terminal
from utils.auth import get_current_user
from utils.task.terminal_cleanup import init_scheduler, scheduler

app = FastAPI(
    title="用户上网行为管控平台",
    version="1.0.0"
)

# 定时在线/离线
@app.on_event("startup")
def startup_event():
    init_scheduler()
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

# 允许跨域（默认允许全部）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(website_control.router, prefix="/api/website_control", tags=["网站访问控制"],dependencies=[Depends(get_current_user)])
app.include_router(process_control.router,prefix="/api/process", tags=["进程运行控制"],dependencies=[Depends(get_current_user)])
app.include_router(login.router, prefix="/api")
app.include_router(admin.router,prefix="/api/admin", tags=["管理员管理"],dependencies=[Depends(get_current_user)])
app.include_router(role.router,prefix="/api/role", tags=["角色管理"],dependencies=[Depends(get_current_user)])
app.include_router(perm.router,prefix="/api/permission", tags=["权限管理"],dependencies=[Depends(get_current_user)])
app.include_router(group.router,prefix="/api/group",tags=["分组管理"],dependencies=[Depends(get_current_user)])
app.include_router(terminal.router, prefix="/api/terminal",tags=["终端管理"],dependencies=[Depends(get_current_user)])
app.include_router(process_monitor.router, prefix="/api/monitor",tags=["进程管控"],dependencies=[Depends(get_current_user)])
app.include_router(behavior.router, prefix="/api/behavior", tags=["行为记录"],dependencies=[Depends(get_current_user)])
app.include_router(log.router,prefix="/api/log",tags = ["日志"],dependencies=[Depends(get_current_user)])

app.include_router(client.router, prefix="/api/client",tags=["客户端无需拦截的路由"])
