from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.control import website_control, process_control

app = FastAPI(
    title="用户上网行为管控平台",
    version="1.0.0"
)

# 允许跨域（默认允许全部）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(website_control.router, prefix="/website_control", tags=["网站访问控制"])
app.include_router(process_control.router,prefix="/process", tags=["进程运行控制"])