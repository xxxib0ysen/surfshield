from fastapi import APIRouter, Depends
from model.log.log_model import OperationLogListResponse, OperationLogQuery
from service.log.log_service import get_operation_log_list, get_module_list_service
from utils.check_perm import check_permission
from utils.log.log_context import log_context_dependency

router = APIRouter()

# 获取系统操作日志列表
@router.get("/operation/list", response_model=OperationLogListResponse)
def list_operation_logs(query: OperationLogQuery = Depends(), _=Depends(log_context_dependency),
                        _p=Depends(check_permission("log:operation:list"))):
    print("Query 接收到参数：", query.dict())
    return get_operation_log_list(query)

# 获取模块
@router.get("/operation/module")
def get_module_list():
    return get_module_list_service()
